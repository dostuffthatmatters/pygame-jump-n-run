
import pygame
from game import Game

from pygame.constants import *
from constants import *

from player import Player


def update(timedelta, game):
    for player in Player.instances:
        player.update(timedelta, game=game)


def draw(game):
    game.draw_background()

    player_count = len(Player.instances)
    for i in range(player_count):
        player = Player.instances[i]
        game.draw_text(
            f"{player.name}: position={player.position}",
            x_left=5, y_top=(5+(i*25)), font_size=20, color=player.color
        )

    game.draw_text(f"{game.fps} FPS", x_left=5, y_top=(5+(player_count*25)), font_size=20)

    Player.draw_all(game)
    game.update()


def run():
    game = Game(
        width=50 * SCALING_FACTOR,
        height=20 * SCALING_FACTOR,
        print_fps=False, max_fps=65
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
