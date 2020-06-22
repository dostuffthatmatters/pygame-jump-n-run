
import pygame
from copy import deepcopy
from game.v4.barrier import SquareBarrier
from game.v4.enemy import Enemy

from pygame.constants import *
from game.engine.constants import *
from game.engine.helpers import merge_into_list_dict, reduce_to_relevant_collisions, get_collision

class Player:

    # Keeps track of all instances of the Player class
    instances = []

    def __init__(
            self,
            name,
            color=(0, 0, 0),
            position=(0, 0),
            keymap=None,
            width=1.0,
            height=2.0,
    ):
        if keymap is None:
            keymap = {
                K_UP: 'UP',
                K_LEFT: 'LEFT',
                K_DOWN: 'DOWN',
                K_RIGHT: 'RIGHT'
            }
        else:
            # Just a few tests whether the passed keymap is valid
            assert \
                all([value in ('UP', 'LEFT', 'DOWN', 'RIGHT') for value in keymap.values()]), \
                'All keys [UP, LEFT, RIGHT] required in keymap property'

            assert \
                all([isinstance(key, int) for key in keymap.keys()]), \
                'All keys for [UP, LEFT, DOWN, RIGHT] in keymap property have to be integers (e.g. pygame.K_UP)'

            assert len(keymap) == 4, 'Only keys for [UP, LEFT, DOWN, RIGHT] allowed in keymap property'

        self.starting_position = list(position)
        self.position = list(deepcopy(position))
        self.size = [width, height]
        self.velocity = [0.0, 0.0]

        self.lifes_left = 3
        self.enemies_killed = 0
        self.old_corpses = []
        self.won = False

        self.keymap = keymap
        self.keypressed = {
            'UP': False,
            'LEFT': False,
            'DOWN': False,
            'RIGHT': False,
        }

        self.name = name
        self.color = color

        self.collisions = {
            'CEILING': None,
            'FLOOR': None,
            'LEFT_WALL': None,
            'RIGHT_WALL': None,
            'OBJECTS_ON_TOP': []
        }

        # Add this new instance to the instance-list Player.players
        Player.instances.append(self)

    def keypress(self, event_key, keydown):
        assert \
            event_key in self.keymap.keys(),\
            f"Only key-events from {list(self.keymap.keys())} allowed"
        self.keypressed[self.keymap[event_key]] = keydown

    def update_for_collisions(self, new_velocity, new_position, timedelta):

        combat_collisions = Enemy.detect_all_collisions(self)
        for enemy in combat_collisions['BARRIER_KILLED']:
            enemy.kill()
            self.enemies_killed += 1
        if len(combat_collisions['MOVING_OBJECT_KILLED']) > 0:
            self.kill()

        # Collisions should refer to new velocity and position
        self.velocity, self.position = new_velocity, new_position
        movement_collisions = reduce_to_relevant_collisions(
            merge_into_list_dict(
                SquareBarrier.detect_all_collisions(self),
                Player.detect_all_collisions(self)
            )
        )

        new_collisions = {
            'CEILING': None,
            'FLOOR': None,
            'LEFT_WALL': None,
            'RIGHT_WALL': None,
            'OBJECTS_ON_TOP': movement_collisions['OBJECTS_ON_TOP'],
        }

        def snap_to_barrier(side):
            dimension = 1 if (side in ('FLOOR', 'CEILING')) else 0
            coordinate_direction = +1 if (side in ('FLOOR', 'LEFT_WALL')) else -1
            new_velocity[dimension] = 0
            limit_center_offset = ((self.size[dimension]/2) - ERROR_MARGIN) * coordinate_direction
            new_position[dimension] = movement_collisions[side] + limit_center_offset
            new_collisions[side] = movement_collisions[side]

        if movement_collisions['CEILING'] is not None:
            if new_velocity[1] > -ERROR_MARGIN:
                snap_to_barrier('CEILING')
            for _object in movement_collisions['OBJECTS_BELOW']:
                _object.velocity[1] = 0
                limit_center_offset = (_object.size[1]) + (self.size[1]/2) + 2 * ERROR_MARGIN
                _object.position[1] = movement_collisions['CEILING'] - limit_center_offset

        elif movement_collisions['FLOOR'] is not None and new_velocity[1] < +ERROR_MARGIN:
            snap_to_barrier('FLOOR')

        # Left and Right wall block is only applied if the player is moving towards that barrier
        if movement_collisions['LEFT_WALL'] is not None and new_velocity[0] < ERROR_MARGIN:
            snap_to_barrier('LEFT_WALL')
        elif movement_collisions['RIGHT_WALL'] is not None and new_velocity[0] > -ERROR_MARGIN:
            snap_to_barrier('RIGHT_WALL')

        if len(movement_collisions['OBJECTS_BELOW']) > 0:
            _object = movement_collisions['OBJECTS_BELOW'][0]
            if (
                _object.velocity[0] < 0 and new_collisions['LEFT_WALL'] is None or
                _object.velocity[0] > 0 and new_collisions['RIGHT_WALL'] is None
            ):
                new_position[0] += _object.velocity[0] * timedelta

        self.collisions = new_collisions
        self.velocity = [round(v, COORDINATE_PRECISION) for v in new_velocity]
        self.position = [round(p, COORDINATE_PRECISION) for p in new_position]

    def update(self, timedelta):
        new_velocity = [0, 0]

        if self.collisions['RIGHT_WALL'] is None:
            if self.keypressed['RIGHT'] and not self.keypressed['LEFT']:
                new_velocity[0] = +RUN_VELOCITY
        if self.collisions['LEFT_WALL'] is None:
            if self.keypressed['LEFT'] and not self.keypressed['RIGHT']:
                new_velocity[0] = -RUN_VELOCITY

        if self.collisions['FLOOR'] is not None:
            if self.keypressed['UP'] and not self.keypressed['DOWN']:
                if self.velocity[1] < ERROR_MARGIN:
                    new_velocity[1] = JUMP_VELOCITY
        else:
            if self.keypressed['DOWN']:
                new_velocity[1] = -JUMP_VELOCITY  # A Mario like forced smash downwards
            else:
                new_velocity[1] = self.velocity[1] - GRAVITY * timedelta

        new_position = [
            self.position[0] + new_velocity[0] * timedelta,
            self.position[1] + new_velocity[1] * timedelta
        ]

        self.update_for_collisions(new_velocity, new_position, timedelta)

    @staticmethod
    def update_all(timedelta):
        for player in Player.instances:
            if player.lifes_left > 0:
                player.update(timedelta)

    def draw(self, game):
        if self.lifes_left > 0:
            game.draw_rect_element(self.position, self.size, color=self.color, alpha=1.0)
            if DRAW_HELPERS:
                game.draw_helper_points(self)

        for corpse in self.old_corpses:
            game.draw_rect_element(corpse, self.size, color=self.color, alpha=0.3)

    @staticmethod
    def draw_all(game):
        for player in Player.instances:
            player.draw(game)

    def kill(self):
        self.old_corpses.append(self.position)
        self.lifes_left -= 1
        self.collisions = {
            'CEILING': None,
            'FLOOR': None,
            'LEFT_WALL': None,
            'RIGHT_WALL': None,
            'OBJECTS_ON_TOP': []
        }
        self.velocity, self.position = [0, 0], deepcopy(self.starting_position)

    @staticmethod
    def detect_all_collisions(moving_player):
        # 1. Fetch all possiple collisions
        all_collisions = {
            'FLOOR': [],
            'OBJECTS_ON_TOP': [],
            'OBJECTS_BELOW': [],
            'LEFT_WALL': [],
            'RIGHT_WALL': [],
        }

        for player in Player.instances:
            if player != moving_player and player.lifes_left > 0:
                collision = get_collision(barrier=player, moving_object=moving_player, stacked_collision=True)
                all_collisions = merge_into_list_dict(
                    all_collisions,
                    collision
                )

        # 2. Reduce all collisions to the relevant ones, example:
        #    all_collisions['FLOOR'] = [3.0, 4.2, 2.2, 4.0]
        #    -> relevant_collisions['FLOOR'] = 4.2
        return reduce_to_relevant_collisions(all_collisions)
