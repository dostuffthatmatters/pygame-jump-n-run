
# Engine
from engine.helpers import merge_into_list_dict, reduce_to_relevant_collisions, get_collision
from engine.tests import *

# Constants
from pygame.constants import *
from engine.constants import *

# Components
from v2.barrier import SquareBarrier


class Player:

    # A list of all Player instances
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
            TEST_keymap(keymap)

        # All properties as lists with length 2
        # => [x-component, y-component]
        self.starting_position = [p for p in position]
        self.position = [p for p in position]
        self.size = [width, height]
        self.velocity = [0.0, 0.0]

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

        # The collisions that are currently being detected
        self.collisions = {
            'CEILING': None,
            'FLOOR': None,
            'LEFT_WALL': None,
            'RIGHT_WALL': None
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

        # 1. Detecting movement collisions with Barriers and other
        #    players. Collisions should refer to the new velocity
        #    and new position that is why we preliminarily update
        #    the players state (self.)
        self.velocity, self.position = new_velocity, new_position
        movement_collisions = reduce_to_relevant_collisions(
            SquareBarrier.detect_all_collisions(self)
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
            'RIGHT_WALL': None
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

        # 2. React to vertical collisions
        if movement_collisions['CEILING'] is not None:
            if new_velocity[1] > -ERROR_MARGIN:
                snap_to_barrier('CEILING')
        elif movement_collisions['FLOOR'] is not None and new_velocity[1] < +ERROR_MARGIN:
            snap_to_barrier('FLOOR')

        # 3. React to horizontal collisions. Left and Right wall block
        # is only applied if the player is moving towards that barrier
        if movement_collisions['LEFT_WALL'] is not None and new_velocity[0] < ERROR_MARGIN:
            snap_to_barrier('LEFT_WALL')
        elif movement_collisions['RIGHT_WALL'] is not None and new_velocity[0] > -ERROR_MARGIN:
            snap_to_barrier('RIGHT_WALL')

        # 4. Now new_velocity and new_position has been adjusted to conform
        #    with collisions -> player state will be updated with the adjusted
        #    values
        self.collisions = new_collisions
        self.velocity = [round(v, COORDINATE_PRECISION) for v in new_velocity]
        self.position = [round(p, COORDINATE_PRECISION) for p in new_position]

    # Update a single Player instances
    def update(self, timedelta):

        # Preliminary new velocity
        new_velocity = [0.0, 0.0]

        # Set current horizontal velocity according to
        # self.collisions and self.keypressed
        if self.collisions['RIGHT_WALL'] is None:
            if self.keypressed['RIGHT'] and not self.keypressed['LEFT']:
                new_velocity[0] = +RUN_VELOCITY
        if self.collisions['LEFT_WALL'] is None:
            if self.keypressed['LEFT'] and not self.keypressed['RIGHT']:
                new_velocity[0] = -RUN_VELOCITY

        # Set current vertical velocity according to
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

        # Preliminary new position
        new_position = [
            self.position[0] + new_velocity[0] * timedelta,
            self.position[1] + new_velocity[1] * timedelta
        ]

        # Adjust new_velocity and new_position by detecting collisions
        # for the new state and modifying the new state to comply with
        # the collisions with other enemies, players and barriers
        self.update_for_collisions(new_velocity, new_position, timedelta)

    # Update all Player instances
    @staticmethod
    def update_all(timedelta):
        for player in Player.instances:
            player.update(timedelta)

    # Draw a single Player instances
    def draw(self, game):
        game.draw_rect_element(self.position, self.size, color=self.color, alpha=1.0)
        if DRAW_HELPERS:
            game.draw_helper_points(self)

    # Draw all Player instances
    @staticmethod
    def draw_all(game):
        for player in Player.instances:
            player.draw(game)
