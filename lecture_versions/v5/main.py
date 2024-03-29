
# Libraries
import pygame
import time
from datetime import datetime

# Engine
from lecture_versions.engine.game import Game

# Constants
from pygame.constants import *
from lecture_versions.engine.constants import *

# Components
from lecture_versions.v5.player import Player
from lecture_versions.v5.enemy import Enemy
from lecture_versions.v5.barrier import Barrier
from lecture_versions.v5.win_logic import check_for_win, draw_flag_pole, draw_scores


def update(timedelta):
    # Only the moving objects have to be updated
    Enemy.update_all(timedelta)
    Player.update_all(timedelta)


def draw(game, player_1, player_2, sorted_scores):

    # 1. Draw game elements
    game.draw_background()
    Barrier.draw_all(game)
    Enemy.draw_all(game)
    Player.draw_all(game)
    draw_flag_pole(game)

    # 2. Draw scores if score-list is not empty
    draw_scores(game, sorted_scores)

    # 3. Draw text in top left corner
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

    # 4. Update game window (and fps)
    game.update()


def run():

    sorted_scores = []
    game_finish_time = None
    win_area = ((46.75, 47.25), (1.5, 12))

    # 1. Initialize game
    game = Game(
        width=50 * SCALING_FACTOR,
        height=20 * SCALING_FACTOR,
        print_fps=False, max_fps=MAX_DRAW_FPS
    )

    # 2. Initialize players
    player_1 = Player(
        "Max", color=(200, 0, 50), position=(21.5, 12),
        keymap={K_w: 'UP', K_a: 'LEFT', K_s: 'DOWN', K_d: 'RIGHT'}
    )
    player_2 = Player(
        "Moritz", color=(50, 0, 200), position=(14.5, 12),
        keymap={K_UP: 'UP', K_LEFT: 'LEFT', K_DOWN: 'DOWN', K_RIGHT: 'RIGHT'}
    )

    # 3. Initialize enemies
    for x in range(2, 32, 3):
        Enemy(position=(x, 2))
        pass

    # 4. Initialize barriers
    Barrier(x_left=-1, y_top=21, width=52, height=1)  # window top
    Barrier(x_left=-1, y_top=1, width=52, height=1)  # window bottom
    Barrier(x_left=-1, y_top=21, width=1, height=22)  # window left
    Barrier(x_left=50, y_top=21, width=1, height=22)  # window right

    Barrier(x_left=12, y_top=6, width=5, height=1)  # step 1
    Barrier(x_left=19, y_top=8, width=5, height=1)  # step 2
    Barrier(x_left=26, y_top=10, width=5, height=1)  # step 3

    Barrier(x_left=36, y_top=9, width=2, height=8)  # pyramid column 1
    Barrier(x_left=38, y_top=7, width=2, height=6)  # pyramid column 2
    Barrier(x_left=40, y_top=5, width=2, height=4)  # pyramid column 3
    Barrier(x_left=42, y_top=3, width=2, height=2)  # pyramid column 4

    Barrier(x_left=45.5, y_top=1.5, width=3, height=0.52, color=(200, 200, 0))  # flag bottom

    # After game_finish_time has been set from inside check_for_win
    # The game will continue to run for 6 seconds and then end
    while game_finish_time is None or (datetime.now() - game_finish_time).seconds < 6:

        # 1. Attach event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.exit()

            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                if event.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d):
                    player_1.keypress(event.key, event.type == pygame.KEYDOWN)
                if event.key in (pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT):
                    player_2.keypress(event.key, event.type == pygame.KEYDOWN)

        # 2. Update (simulation)
        if not SLOWDOWN:
            # Collision detection is not fully working with very
            # low fps (<< 10 fps)
            fps = max(game.fps, MIN_DRAW_FPS)

            # Solution: Simulate multiple time steps per drawing
            # because drawing takes > 250 times longer than
            # simulating
            for i in range(SIMULATION_FRAMES_PER_DRAW):
                update(1/(fps * SIMULATION_FRAMES_PER_DRAW))

                # Check for a possible game ending
                sorted_scores, game_finish_time = check_for_win(win_area, sorted_scores, game_finish_time)

        else:
            # SLOWDOWN can be set to true in order to observe the
            # in extreme slow_motion. How many fps with SLOWDOWN
            # enabled can be set with SLOWDOWN_FPS
            time.sleep((1/SLOWDOWN_FPS) - (1/100))
            update(1/100)

        # 3. Draw (visualization)
        draw(game, player_1, player_2, sorted_scores)
