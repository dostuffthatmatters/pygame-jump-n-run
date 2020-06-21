
import pygame
import time
import math
from game.engine.game import Game

from pygame.constants import *
from game.engine.constants import *

from game.v2.player import Player
from game.v2.barrier import SquareBarrier


def update(timedelta):
    Player.update_all(timedelta)


def draw(game, player):
    game.draw_background()
    SquareBarrier.draw_all(game)
    Player.draw_all(game)

    if DRAW_HELPERS:
        game.draw_text(text=f"collisions: {player.collisions}", x_left=5, y_top=5, font_size=20, color=player.color)
        game.draw_text(text=f"position: {player.position}", x_left=5, y_top=30, font_size=20, color=player.color)
        game.draw_text(text=f"velocity: {player.velocity}", x_left=5, y_top=55, font_size=20, color=player.color)
        game.draw_text(text=f"{game.fps * SIMULATION_FRAMES_PER_DRAW} FPS (simulation) "
                            f"{game.fps} FPS (canvas)", x_left=5, y_top=80, font_size=20)
    else:
        game.draw_text(text=f"{game.fps} FPS", x_left=5, y_top=5, font_size=20)

    game.update()


def run():
    game = Game(
        width=50 * SCALING_FACTOR,
        height=20 * SCALING_FACTOR,
        print_fps=False, max_fps=MAX_DRAW_FPS
    )

    player_1 = Player(
        "Max", color=(200, 0, 50), position=(15, 12),
        keymap={K_w: 'UP', K_a: 'LEFT', K_s: 'DOWN', K_d: 'RIGHT'}
    )

    # Window boundaries
    SquareBarrier(x_left=-1, y_top=21, width=52, height=1)  # top
    SquareBarrier(x_left=-1, y_top=1, width=52, height=1)  # bottom
    SquareBarrier(x_left=-1, y_top=21, width=1, height=22)  # left
    SquareBarrier(x_left=50, y_top=21, width=1, height=22)  # right

    # 3 step barriers
    SquareBarrier(x_left=12, y_top=6, width=5, height=1)  # step 1
    SquareBarrier(x_left=19, y_top=8, width=5, height=1)  # step 2
    SquareBarrier(x_left=26, y_top=10, width=5, height=1)  # step 3

    # "half pyramid" barrier
    SquareBarrier(x_left=36, y_top=9, width=2, height=8)  # column 1
    SquareBarrier(x_left=38, y_top=7, width=2, height=6)  # column 2
    SquareBarrier(x_left=40, y_top=5, width=2, height=4)  # column 3
    SquareBarrier(x_left=42, y_top=3, width=2, height=2)  # column 4

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.exit()

            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                if event.key in (pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d):
                    player_1.keypress(event.key, event.type == pygame.KEYDOWN)

        if not SLOWDOWN:
            # Collision detection is not fully working with low fps, yet...
            fps = max(game.fps, MIN_DRAW_FPS)

            for i in range(SIMULATION_FRAMES_PER_DRAW):
                update(1/(fps * SIMULATION_FRAMES_PER_DRAW))
        else:
            time.sleep((1/SLOWDOWN_FPS) - (1 / 45))
            update(1/45)

        draw(game, player_1)
