
# Engine
from lecture_versions.engine.tests import *

# Constants
from pygame.constants import *
from lecture_versions.engine.constants import *


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
        self.position = list(position)
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

        # Add this new instances to the instance-list from above
        Player.instances.append(self)

    def keypress(self, event_key, keydown):
        # We know from self.keymap which event.key will lead to which
        # direction in self.keypressed being set to true or false

        # "keydown" is a boolean value and "event_key" is a constant
        # like "pygame.K_LEFT"/"pygame.K_RIGHT"

        TEST_keypress(self.keymap, event_key)
        self.keypressed[self.keymap[event_key]] = keydown

    # Update a single Player instances
    def update(self, timedelta, game=None):
        # 1. Preliminary new velocity
        new_velocity = [
            0,
            self.velocity[1] - GRAVITY * timedelta
        ]

        # 2. Apply horizontal movement when exactly one
        # sideways key is currently being pressed
        if self.keypressed['LEFT'] and not self.keypressed['RIGHT']:
            new_velocity[0] = -RUN_VELOCITY
        elif self.keypressed['RIGHT'] and not self.keypressed['LEFT']:
            new_velocity[0] = +RUN_VELOCITY

        # 3. Preliminary new velocity
        new_position = [
            self.position[0] + new_velocity[0] * timedelta,
            self.position[1] + new_velocity[1] * timedelta
        ]

        # 4. Check for horizontal boundaries. Th reference
        # to game is needed to get the window width
        if game is not None:
            if new_position[0] < self.size[0]/2:
                new_velocity[0] = 0.0
                new_position[0] = self.size[0]/2
            if new_position[0] > ((game.width/SCALING_FACTOR) - (self.size[0]/2)):
                new_velocity[0] = 0.0
                new_position[0] = ((game.width/SCALING_FACTOR) - (self.size[0]/2))

        # 5. Check for floor boundary
        if new_position[1] < (self.size[1]/2 + ERROR_MARGIN):
            # The player is standing on the floor
            if self.keypressed['UP']:
                new_velocity[1] = JUMP_VELOCITY
            else:
                new_velocity[1] = 0
            new_position[1] = self.size[1]/2
        else:
            # Gravity has already been applied above
            pass

        # 6. Now new_velocity and new_position has been adjusted to conform
        #    with collisions -> player state will be updated with the adjusted
        #    values
        self.velocity = [round(v, COORDINATE_PRECISION) for v in new_velocity]
        self.position = [round(p, COORDINATE_PRECISION) for p in new_position]

    # Update all Player instances
    @staticmethod
    def update_all(timedelta, game=None):
        for player in Player.instances:
            player.update(timedelta, game)

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
