
# Engine
from engine.sprite import Sprite
from engine.helpers import merge_into_list_dict, reduce_to_relevant_collisions, get_collision
from engine.tests import *

# Constants
from pygame.constants import *
from engine.constants import *

# Components
from v6.barrier import SquareBarrier
from v6.enemy import Enemy


class Player:

    # A list of all Player instances
    instances = []

    def __init__(
            self,
            name,
            color=(0, 0, 0),
            position=(0, 0),
            keymap=None,
            size=(1.0, 1.6),
            sprite_run=None, sprite_jump_up=None, sprite_jump_down=None,
    ):
        if keymap is None:
            keymap = {
                K_UP: 'UP',
                K_LEFT: 'LEFT',
                K_DOWN: 'DOWN',
                K_RIGHT: 'RIGHT'
            }
        else:
            TEST_keymap(keymap)

        # All properties as lists with length 2
        # => [x-component, y-component]
        self.starting_position = list(position)
        self.position = [p for p in position]  # manual deepcopy
        self.size = list(size)
        self.velocity = [0.0, 0.0]

        # Game specific stuff
        self.lifes_left = 3
        self.enemies_killed = 0
        self.old_corpses = []
        self.won = False
        self.score = 0

        # Store the relations between keyboard keys and
        # movement direction i.e. WASD vs ULDR
        self.keymap = keymap

        # Store which keys are currently being pressed
        self.keypressed = {
            'UP': False,
            'LEFT': False,
            'DOWN': False,
            'RIGHT': False,
        }

        self.name = name
        self.color = color

        assert all([ s is not None for s in (sprite_run, sprite_jump_up, sprite_jump_down)])
        self.sprite_run = sprite_run
        self.sprite_jump_up = sprite_jump_up
        self.sprite_jump_down = sprite_jump_down

        # sprite_size = (16, 25), hit_box = (3, 11, 10, 16)
        scaled_sprite_size = [self.size[0] * SCALING_FACTOR * (16 / 10), self.size[1] * SCALING_FACTOR * (25 / 16)]
        for s in (self.sprite_run, self.sprite_jump_up, self.sprite_jump_down):
            s.size = scaled_sprite_size

        # The collisions that are currently being detected
        self.collisions = {
            'CEILING': None,
            'FLOOR': None,
            'LEFT_WALL': None,
            'RIGHT_WALL': None,
            'OBJECTS_ON_TOP': []
        }

        # Add this new instances to the instance-list from above
        Player.instances.append(self)

    def keypress(self, event_key, keydown):
        # We know from self.keymap which event.key will lead to which
        # direction in self.keypressed being set to true or false

        # "keydown" is a boolean value and "event_key" is a constant
        # like "pygame.K_LEFT"/"pygame.K_RIGHT"

        TEST_keypress(self.keymap, event_key)
        self.keypressed[self.keymap[event_key]] = keydown

    def update_for_collisions(self, new_velocity, new_position, timedelta):

        # 1. Detect combat collisions with enemies. "MOVING_OBJECT"
        #    refers to the player. "BARRIER" refers to the enemy.
        combat_collisions = Enemy.detect_all_collisions(self)
        for enemy in combat_collisions['BARRIER_KILLED']:
            enemy.kill()
            self.enemies_killed += 1
        if len(combat_collisions['MOVING_OBJECT_KILLED']) > 0:
            self.kill()
            return

        # 2. Detecting movement collisions with Barriers and other
        #    players. Collisions should refer to the new velocity
        #    and new position that is why we preliminarily update
        #    the players state (self.)
        self.velocity, self.position = new_velocity, new_position
        movement_collisions = reduce_to_relevant_collisions(
            merge_into_list_dict(
                SquareBarrier.detect_all_collisions(self),
                Player.detect_all_collisions(self)
            )
        )

        # The strategy now is to go through all the collisions that
        # were detected and successively adjust new_velocity and
        # new_position if needed. In the end the players state (self.
        # will be updated with the adjusted position/velocity once
        # again

        new_collisions = {
            'CEILING': None,
            'FLOOR': None,
            'LEFT_WALL': None,
            'RIGHT_WALL': None,
            'OBJECTS_ON_TOP': movement_collisions['OBJECTS_ON_TOP'],
        }

        # "Snap" to Wall/Floor/Ceiling when hitting one. Example
        #   Moving left & new_x = -0.04
        #   Wall detected at x=0
        #   Snaps to x=0 and velocity *= -1 (turns around)
        def snap_to_barrier(side):
            dimension = 1 if (side in ('FLOOR', 'CEILING')) else 0
            coordinate_direction = +1 if (side in ('FLOOR', 'LEFT_WALL')) else -1
            new_velocity[dimension] = 0
            limit_center_offset = ((self.size[dimension]/2) - ERROR_MARGIN) * coordinate_direction
            new_position[dimension] = movement_collisions[side] + limit_center_offset
            new_collisions[side] = movement_collisions[side]

        # 3. React to vertical collisions
        if movement_collisions['CEILING'] is not None:
            if new_velocity[1] > -ERROR_MARGIN:
                snap_to_barrier('CEILING')

            # Edge case for two players standing on top of each other with
            # the bottom player jumping up and only the top player hitting
            # a ceiling. This snippet is needed so that the upper player is
            # not being "forced into the wall" and the bottom player detects
            # the ceiling indirectly
            for _object in movement_collisions['OBJECTS_BELOW']:
                _object.velocity[1] = 0
                limit_center_offset = (_object.size[1]) + (self.size[1]/2) + 2 * ERROR_MARGIN
                _object.position[1] = movement_collisions['CEILING'] - limit_center_offset
        elif movement_collisions['FLOOR'] is not None and new_velocity[1] < +ERROR_MARGIN:
            snap_to_barrier('FLOOR')

        # 4. React to horizontal collisions. Left and Right wall block
        # is only applied if the player is moving towards that barrier
        if movement_collisions['LEFT_WALL'] is not None and new_velocity[0] < ERROR_MARGIN:
            snap_to_barrier('LEFT_WALL')
        elif movement_collisions['RIGHT_WALL'] is not None and new_velocity[0] > -ERROR_MARGIN:
            snap_to_barrier('RIGHT_WALL')

        # 5. When standing on top of another player and that player moves
        #    then the player on top should also be moved by that players
        #    movement = the player on top will be carried around (as long
        # as he doe not hit a wall
        if len(movement_collisions['OBJECTS_BELOW']) > 0:
            _object = movement_collisions['OBJECTS_BELOW'][0]
            if (
                _object.velocity[0] < 0 and new_collisions['LEFT_WALL'] is None or
                _object.velocity[0] > 0 and new_collisions['RIGHT_WALL'] is None
            ):
                new_position[0] += _object.velocity[0] * timedelta

        # 6. Now new_velocity and new_position has been adjusted to conform
        #    with collisions -> player state will be updated with the adjusted
        #    values
        self.collisions = new_collisions
        self.velocity = [round(v, COORDINATE_PRECISION) for v in new_velocity]
        self.position = [round(p, COORDINATE_PRECISION) for p in new_position]

    # Update a single Player instances
    def update(self, timedelta):

        # 1. Preliminary new velocity
        new_velocity = [0.0, 0.0]

        # 2. Set current horizontal velocity according to
        # self.collisions and self.keypressed

        if self.keypressed['RIGHT'] and not self.keypressed['LEFT']:
            # Flip sprite
            self.sprite_run.flip = (False, False)
            self.sprite_jump_up.flip = (False, False)
            self.sprite_jump_down.flip = (False, False)

            # Propose move if there is not RIGHT_WALL
            if self.collisions['RIGHT_WALL'] is None:
                new_velocity[0] = +RUN_VELOCITY

        if self.keypressed['LEFT'] and not self.keypressed['RIGHT']:
            # Flip sprite
            self.sprite_run.flip = (True, False)
            self.sprite_jump_up.flip = (True, False)
            self.sprite_jump_down.flip = (True, False)

            # Propose move if there is not LEFT_WALL
            if self.collisions['LEFT_WALL'] is None:
                new_velocity[0] = -RUN_VELOCITY

        # 3. Set current vertical velocity according to
        # self.collisions and self.keypressed
        if self.collisions['FLOOR'] is not None:
            if self.keypressed['UP'] and not self.keypressed['DOWN']:
                if self.velocity[1] < ERROR_MARGIN:
                    new_velocity[1] = JUMP_VELOCITY
        else:
            if self.keypressed['DOWN']:
                # A Mario like forced smash downwards
                new_velocity[1] = -JUMP_VELOCITY
            else:
                # Regular gravitational acceleration
                new_velocity[1] = self.velocity[1] - GRAVITY * timedelta

        # 4. Preliminary new position
        new_position = [
            self.position[0] + new_velocity[0] * timedelta,
            self.position[1] + new_velocity[1] * timedelta
        ]

        # 5. Adjust new_velocity and new_position by detecting collisions
        # for the new state and modifying the new state to comply with
        # the collisions with other enemies, players and barriers
        self.update_for_collisions(new_velocity, new_position, timedelta)

        if abs(self.velocity[0]) > ERROR_MARGIN:
            self.sprite_run.update(timedelta, fps=abs(MAX_RUN_FPS * self.velocity[0])/RUN_VELOCITY)

        if -ERROR_MARGIN <= self.velocity[0] <= ERROR_MARGIN:
            self.sprite_run.reset()

        self.calculate_score()


    # Update all Player instances
    @staticmethod
    def update_all(timedelta):
        for player in Player.instances:
            if player.lifes_left > 0 and not player.won:
                player.update(timedelta)

    # Draw a single Player instances
    def draw(self, game):
        if self.lifes_left > 0:
            # Uses the scaled draw rect method from engine.game
            if self.velocity[1] > ERROR_MARGIN:
                self.sprite_run.reset()
                game.draw_sprite_element(
                    self.sprite_jump_up.getImage(),
                    center_position=self.position,
                    sprite_offset=[0, 0.55]
                )
            elif self.velocity[1] < - ERROR_MARGIN:
                self.sprite_run.reset()
                game.draw_sprite_element(
                    self.sprite_jump_down.getImage(),
                    center_position=self.position,
                    sprite_offset=[0, 0.45]
                )
            else:
                game.draw_sprite_element(
                    self.sprite_run.getImage(),
                    center_position=self.position,
                    sprite_offset=[0, 0.45]
                )

            # game.draw_rect_element(self.position, self.size, color=self.color, alpha=1.0)
            if DRAW_HELPERS:
                game.draw_rect_element(self.position, self.size, color=self.color, alpha=0.4)
                game.draw_helper_points(self)

        if DRAW_HELPERS:
            for corpse in self.old_corpses:
                game.draw_rect_element(corpse, self.size, color=self.color, alpha=0.3)

    # Draw all Player instances
    @staticmethod
    def draw_all(game):
        for player in Player.instances:
            player.draw(game)

    def kill(self):
        # "kill" moves the player to its starting position and
        # decrements his number of lifes left. In addition to
        # that, the position-of-death will be appended to the
        # self.corpses array in order to draw old corpses on the
        # screen
        self.old_corpses.append(self.position)
        self.lifes_left -= 1
        self.collisions = {
            'CEILING': None,
            'FLOOR': None,
            'LEFT_WALL': None,
            'RIGHT_WALL': None,
            'OBJECTS_ON_TOP': []
        }
        self.velocity = [0, 0]
        self.position = [p for p in self.starting_position]

    # The method used by a player (=moving_player) to detect all
    # collisions with other players from the Player.instances list
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

    def calculate_score(self, height_bonus=False):
        if self.lifes_left > 0:
            score = 10 * self.enemies_killed + self.lifes_left * 3
            score += self.position[1] if height_bonus else 0
            score = round(score, 2)
        else:
            score = 0
        self.score = score
