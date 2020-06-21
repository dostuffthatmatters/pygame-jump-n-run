
import pygame
from game.v2.barrier import SquareBarrier

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
            # Just a few tests whether the passed
            assert \
                all([value in ('UP', 'LEFT', 'DOWN', 'RIGHT') for value in keymap.values()]), \
                'All keys [UP, LEFT, RIGHT] required in keymap property'

            assert \
                all([isinstance(key, int) for key in keymap.keys()]), \
                'All keys for [UP, LEFT, DOWN, RIGHT] in keymap property have to be integers (e.g. pygame.K_UP)'

            assert len(keymap) == 4, 'Only keys for [UP, LEFT, DOWN, RIGHT] allowed in keymap property'

        self.position = position
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
        self.width = width
        self.height = height

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

    def update_collisions(self, new_velocity, new_position):
        all_collisions = SquareBarrier.detect_all_collisions(
            x_center=new_position[0], y_center=new_position[1],
            width=self.width, height=self.height
        )

        new_collisions = {
            'CEILING': None,
            'FLOOR': None,
            'LEFT_WALL': None,
            'RIGHT_WALL': None
        }

        if 'FLOOR' in all_collisions and new_velocity[1] < ERROR_MARGIN:
            y_floor = all_collisions['FLOOR']
            new_velocity[1] = 0
            new_position[1] = y_floor + (self.height/2) - ERROR_MARGIN
            new_collisions['FLOOR'] = y_floor

        if 'CEILING' in all_collisions and new_velocity[1] > -ERROR_MARGIN:
            y_ceil = all_collisions['CEILING']
            new_velocity[1] = 0
            new_position[1] = y_ceil - (self.height/2) + ERROR_MARGIN
            new_collisions['CEILING'] = y_ceil

        if 'LEFT_WALL' in all_collisions and new_velocity[0] < ERROR_MARGIN:
            x_wall = all_collisions['LEFT_WALL']
            new_velocity[0] = 0
            new_position[0] = x_wall + (self.width/2) - ERROR_MARGIN
            new_collisions['LEFT_WALL'] = x_wall

        if 'RIGHT_WALL' in all_collisions and new_velocity[0] > -ERROR_MARGIN:
            x_wall = all_collisions['RIGHT_WALL']
            new_velocity[0] = 0
            new_position[0] = x_wall - (self.width/2) + ERROR_MARGIN
            new_collisions['RIGHT_WALL'] = x_wall

        self.collisions = new_collisions

        new_velocity = [round(v, COORDINATE_PRECISION) for v in new_velocity]
        new_position = [round(p, COORDINATE_PRECISION) for p in new_position]
        return new_velocity, new_position

    def update(self, timedelta):
        new_velocity = [0, 0]

        if self.collisions['RIGHT_WALL'] is None and \
                self.keypressed['RIGHT'] and not self.keypressed['LEFT']:
            new_velocity[0] = RUN_VELOCITY

        if self.collisions['LEFT_WALL'] is None and \
                self.keypressed['LEFT'] and not self.keypressed['RIGHT']:
            new_velocity[0] = -RUN_VELOCITY

        new_position = [
            self.position[0] + new_velocity[0] * timedelta,
            0
        ]

        if self.collisions['FLOOR'] is None:
            new_velocity[1] = self.velocity[1] - GRAVITY * timedelta
            if self.keypressed['DOWN']:
                new_velocity[1] = -JUMP_VELOCITY
            new_position[1] = self.position[1] + new_velocity[1] * timedelta
        else:
            # If on some floor
            if self.keypressed['UP'] and not self.keypressed['DOWN']:
                if self.velocity[1] < ERROR_MARGIN:
                    new_velocity[1] = new_velocity[1] = JUMP_VELOCITY
                new_position[1] = self.position[1] + new_velocity[1] * timedelta
            else:
                new_position[1] = self.collisions['FLOOR'] + (self.height/2) - ERROR_MARGIN

        self.velocity, self.position = self.update_collisions(new_velocity, new_position)

    @staticmethod
    def update_all(timedelta):
        for player in Player.instances:
            player.update(timedelta)

    def draw(self, game):
        rect_w = self.width * SCALING_FACTOR
        rect_h = self.height * SCALING_FACTOR
        rect_x = self.position[0] * SCALING_FACTOR - (rect_w/2)
        rect_y = game.height - (self.position[1] * SCALING_FACTOR + (rect_h/2))
        game.draw_rect(rect_x, rect_y, rect_w, rect_h, color=self.color)

        if DRAW_HELPERS:
            circle_r = min((self.width, self.height)) * 0.1 * SCALING_FACTOR
            sides = [
                {"identifier": "CENTER", "dx": 0, "dy": 0},
                {"identifier": "FLOOR", "dx": 0, "dy": -self.height/2},
                {"identifier": "CEILING", "dx": 0, "dy": +self.height/2},
                {"identifier": "LEFT_WALL", "dx": -self.width/2, "dy": 0},
                {"identifier": "RIGHT_WALL", "dx": +self.width/2, "dy": 0}
            ]
            for side in sides:
                if side["identifier"] == "CENTER" or self.collisions[side["identifier"]] is not None:
                    circle_x = (self.position[0] + side["dx"]) * SCALING_FACTOR
                    circle_y = game.height - ((self.position[1] + side["dy"]) * SCALING_FACTOR)
                    game.draw_circle(circle_x, circle_y, circle_r, color=(0, 0, 255))

    @staticmethod
    def draw_all(game):
        for player in Player.instances:
            player.draw(game)
