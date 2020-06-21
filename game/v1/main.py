import pygame
from pygame import K_w, K_a, K_s, K_d, K_UP, K_LEFT, K_DOWN, K_RIGHT
from game.engine.game import Game
from game.engine.constants import *

from game.v1.player import Player


def update(timedelta, game):
    Player.update_all(timedelta, game=game)


def draw(game):
    game.draw_background()
    Player.draw_all(game)
    game.update()


def run():
    game = Game(
        width=50 * SCALING_FACTOR,
        height=20 * SCALING_FACTOR,
        print_fps=True, max_fps=60
    )

    player_1 = Player(
        "Max", color=(200, 0, 50), position=(15, 3),
        keymap={K_w: 'UP', K_a: 'LEFT', K_d: 'RIGHT'}
    )
    player_2 = Player(
        "Moritz", color=(50, 0, 200), position=(35, 3),
        keymap={K_UP: 'UP', K_LEFT: 'LEFT', K_RIGHT: 'RIGHT'}
    )

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.exit()

            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                if event.key in (pygame.K_w, pygame.K_a, pygame.K_d):
                    player_1.keypress(event.key, event.type == pygame.KEYDOWN)
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP):
                    player_2.keypress(event.key, event.type == pygame.KEYDOWN)

        update(1/game.fps, game)
        draw(game)
