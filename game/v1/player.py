
import pygame
from pygame.constants import *
from engine.constants import *

class Player:

    # Keeps track of all instances of the Player class
    instances = []

    def __init__(
            self,
            name,
            color=(0, 0, 0),
            position=(0, 0),
            keymap=None,
            width=0.8,
            height=1.8,
    ):
        if keymap is None:
            keymap = {
                pygame.K_UP: 'UP',
                pygame.K_LEFT: 'LEFT',
                pygame.K_RIGHT: 'RIGHT'
            }
        else:
            # Just a few tests whether the passed
            assert \
                all([value in ('UP', 'LEFT', 'RIGHT') for value in keymap.values()]), \
                'All keys [UP, LEFT, RIGHT] required in keymap property'

            assert \
                all([isinstance(key, int) for key in keymap.keys()]), \
                'All keys for [UP, LEFT, RIGHT] in keymap property have to be integers (e.g. pygame.K_UP)'

            assert len(keymap) == 3, 'Only keys for [UP, LEFT, RIGHT] allowed in keymap property'

        self.position = position
        self.velocity = [0.0, 0.0]

        self.keymap = keymap
        self.keypressed = {
            'UP': False,
            'LEFT': False,
            'RIGHT': False,
        }

        self.name = name
        self.color = color
        self.width = width
        self.height = height

        # Add this new instance to the instance-list Player.players
        Player.instances.append(self)

    def keypress(self, event_key, keydown):
        assert \
            event_key in self.keymap.keys(),\
            f"Only key-events from {list(self.keymap.keys())} allowed"
        self.keypressed[self.keymap[event_key]] = keydown

    def update(self, timedelta, game=None):
        new_velocity = [
            0,
            self.velocity[1] - GRAVITY * timedelta
        ]

        if self.keypressed['LEFT'] and not self.keypressed['RIGHT']:
            new_velocity[0] = -RUN_VELOCITY
        elif self.keypressed['RIGHT'] and not self.keypressed['LEFT']:
            new_velocity[0] = +RUN_VELOCITY

        self.velocity = new_velocity

        new_position = [
            self.position[0] + self.velocity[0] * timedelta,
            self.position[1] + self.velocity[1] * timedelta
        ]
        if new_position[1] < (self.height/2 + 0.05):
            self.velocity[1] = JUMP_VELOCITY if self.keypressed['UP'] else 0.0
            new_position[1] = self.height/2
        if game is not None:
            if new_position[0] < self.width/2:
                self.velocity[0] = 0.0
                new_position[0] = self.width/2
            if new_position[0] > ((game.width/SCALING_FACTOR) - (self.width/2)):
                self.velocity[0] = 0.0
                new_position[0] = ((game.width/SCALING_FACTOR) - (self.width/2))

        self.velocity = [round(v, COORDINATE_PRECISION) for v in self.velocity]
        self.position = [round(p, COORDINATE_PRECISION) for p in new_position]

    @staticmethod
    def update_all(timedelta, game=None):
        for player in Player.instances:
            player.update(timedelta, game)

    def draw(self, game):
        w = self.width * SCALING_FACTOR
        h = self.height * SCALING_FACTOR
        x = self.position[0] * SCALING_FACTOR - (w / 2)
        y = game.height - (self.position[1] * SCALING_FACTOR + (h / 2))
        game.draw_rect(x, y, w, h, color=self.color)

    @staticmethod
    def draw_all(game):
        for player in Player.instances:
            player.draw(game)
