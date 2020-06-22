
import pygame
import time
import math
from datetime import datetime
from game.engine.game import Game

from pygame.constants import *
from game.engine.constants import *

from game.v5.player import Player
from game.v5.win_logic import check_for_win, draw_flag_pole, draw_scores
from game.v4.enemy import Enemy
from game.v4.barrier import SquareBarrier


def update(timedelta):
    Enemy.update_all(timedelta)
    Player.update_all(timedelta)


def draw(game, player_1, player_2, sorted_scores):
    game.draw_background()
    SquareBarrier.draw_all(game)
    Enemy.draw_all(game)
    Player.draw_all(game)
    draw_flag_pole(game)
    draw_scores(game, sorted_scores)

    if DRAW_HELPERS:
        game.draw_text(text=f"collisions: {player_1.collisions}",
                       x_left=5, y_top=5, font_size=20, color=player_1.color)
        game.draw_text(text=f"position: {player_1.position}, velocity: {player_1.velocity}",
                       x_left=5, y_top=30, font_size=20, color=player_1.color)
    else:
        game.draw_text(text=f"{player_1.name} - "
                            f"{player_1.enemies_killed} Kill(s), "
                            f"{3 - player_1.lifes_left} Death(s),",
                       x_left=5, y_top=5, font_size=20, color=player_1.color)
        game.draw_text(text=f"{player_2.name} - "
                            f"{player_2.enemies_killed} Kill(s), "
                            f"{3 - player_2.lifes_left} Death(s),",
                       x_left=5, y_top=30, font_size=20, color=player_2.color)

    game.draw_text(text=f"{game.fps * SIMULATION_FRAMES_PER_DRAW} FPS (simulation) "
                        f"{game.fps} FPS (canvas)", x_left=5, y_top=55, font_size=20)

    game.update()


def run():
    game = Game(
        width=50 * SCALING_FACTOR,
        height=20 * SCALING_FACTOR,
        print_fps=False, max_fps=MAX_DRAW_FPS
    )

    sorted_scores = []
    game_finish_time = None
    win_area = ((46.75, 47.25), (1.5, 12))

    player_1 = Player(
        "Max", color=(200, 0, 50), position=(21.5, 12),
        keymap={K_w: 'UP', K_a: 'LEFT', K_s: 'DOWN', K_d: 'RIGHT'}
    )
    player_2 = Player(
        "Moritz", color=(50, 0, 200), position=(14.5, 12),
        keymap={K_UP: 'UP', K_LEFT: 'LEFT', K_DOWN: 'DOWN', K_RIGHT: 'RIGHT'}
    )

    for x in range(2, 32, 3):
        Enemy(position=(x, 2))
        pass

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

    # Flag bottom
    SquareBarrier(x_left=45.5, y_top=1.5, width=3, height=0.5, color=(200, 200, 0))
    win_area = ((46.75, 47.25), (1.5, 12))

    while game_finish_time is None or (datetime.now() - game_finish_time).seconds < 6:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.exit()

            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                if event.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d):
                    player_1.keypress(event.key, event.type == pygame.KEYDOWN)
                if event.key in (pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT):
                    player_2.keypress(event.key, event.type == pygame.KEYDOWN)

        if not SLOWDOWN:
            # Collision detection is not fully working with low fps, yet...
            fps = max(game.fps, MIN_DRAW_FPS)

            for i in range(SIMULATION_FRAMES_PER_DRAW):
                update(1/(fps * SIMULATION_FRAMES_PER_DRAW))
                sorted_scores = check_for_win(win_area, sorted_scores)
                if game_finish_time is None and len(sorted_scores) > 0:
                    game_finish_time = datetime.now()
        else:
            time.sleep((1/SLOWDOWN_FPS) - (1/45))
            update(1/45)

        draw(game, player_1, player_2, sorted_scores)
