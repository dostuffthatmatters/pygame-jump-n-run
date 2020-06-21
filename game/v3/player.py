
import pygame
from game.v3.barrier import SquareBarrier

from pygame.constants import *
from game.engine.constants import *

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

        self.position = position
        self.size = [width, height]
        self.velocity = [0.0, 0.0]

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
            'RIGHT_WALL': None
        }

        # Add this new instance to the instance-list Player.players
        Player.instances.append(self)

    def keypress(self, event_key, keydown):
        assert \
            event_key in self.keymap.keys(),\
            f"Only key-events from {list(self.keymap.keys())} allowed"
        self.keypressed[self.keymap[event_key]] = keydown

    def update_for_collisions(self, new_velocity, new_position):
        all_collisions = SquareBarrier.detect_all_collisions(self)

        new_collisions = {
            'CEILING': None,
            'FLOOR': None,
            'LEFT_WALL': None,
            'RIGHT_WALL': None
        }

        def fix_position(side):
            dimension = 1 if (side in ('FLOOR', 'CEILING')) else 0
            coordinate_direction = +1 if (side in ('FLOOR', 'LEFT_WALL')) else -1
            new_velocity[dimension] = 0
            limit_center_offset = ((self.size[dimension]/2) - ERROR_MARGIN) * coordinate_direction
            new_position[dimension] = all_collisions[side] + limit_center_offset
            new_collisions[side] = all_collisions[side]

        if 'FLOOR' in all_collisions and new_velocity[1] < ERROR_MARGIN:
            fix_position('FLOOR')
        elif 'CEILING' in all_collisions and new_velocity[1] > -ERROR_MARGIN:
            fix_position('CEILING')

        if 'LEFT_WALL' in all_collisions and new_velocity[0] < ERROR_MARGIN:
            fix_position('LEFT_WALL')
        elif 'RIGHT_WALL' in all_collisions and new_velocity[0] > -ERROR_MARGIN:
            fix_position('RIGHT_WALL')

        self.collisions = new_collisions
        self.velocity = [round(v, COORDINATE_PRECISION) for v in new_velocity]
        self.position = [round(p, COORDINATE_PRECISION) for p in new_position]

    def update(self, timedelta):
        new_velocity = [0, 0]

        if self.collisions['RIGHT_WALL'] is None:
            if self.keypressed['RIGHT'] and not self.keypressed['LEFT']:
                new_velocity[0] = RUN_VELOCITY

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

        self.update_for_collisions(new_velocity, new_position)

    @staticmethod
    def update_all(timedelta):
        for player in Player.instances:
            player.update(timedelta)

    def draw(self, game):
        game.draw_rect_element(self.position, self.size, color=self.color)

        if DRAW_HELPERS:
            circle_radius = min(self.size) * 0.1
            circle_offsets = {
                "FLOOR": [0, -0.5*self.size[1]],
                "CEILING": [0, 0.5*self.size[1]],
                "LEFT_WALL": [-0.5*self.size[0], 0],
                "RIGHT_WALL": [0.5*self.size[0], 0],
            }

            game.draw_circle_element(self.position, circle_radius, color=(0, 0, 255))
            for side in circle_offsets:
                if self.collisions[side] is not None:
                    position = [self.position[dim] + circle_offsets[side][dim] for dim in (0, 1)]
                    game.draw_circle_element(position, circle_radius, color=(0, 0, 255))

    @staticmethod
    def draw_all(game):
        for player in Player.instances:
            player.draw(game)
