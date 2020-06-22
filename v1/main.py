
# Libraries
import pygame
import time
from datetime import datetime

# Engine
from engine.game import Game

# Constants
from pygame.constants import *
from engine.constants import *

# Components
from v1.player import Player


def update(timedelta, game):
    # Only the moving objects have to be updated
    Player.update_all(timedelta, game=game)


def draw(game, player_1, player_2):

    # 1. Draw game elements
    game.draw_background()
    Player.draw_all(game)

    # 2. Draw text in top left corner
    if DRAW_HELPERS:
        game.draw_text(text=f"position: {player_1.position}, velocity: {player_1.velocity}",
                       x_left=5, y_top=5, font_size=20, color=player_1.color)
        fps_y_top = 30
    else:
        fps_y_top = 5

    game.draw_text(text=f"{game.fps * SIMULATION_FRAMES_PER_DRAW} FPS (simulation) "
                        f"{game.fps} FPS (canvas)", x_left=5, y_top=fps_y_top, font_size=20)

    # 3. Update game window (and fps)
    game.update()


def run():

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

    # After game_finish_time has been set from inside check_for_win
    # The game will continue to run for 6 seconds and then end
    while True:

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
                update(1/(fps * SIMULATION_FRAMES_PER_DRAW), game)

        else:
            # SLOWDOWN can be set to true in order to observe the
            # in extreme slow_motion. How many fps with SLOWDOWN
            # enabled can be set with SLOWDOWN_FPS
            time.sleep((1/SLOWDOWN_FPS) - (1/100))
            update(1/100)

        # 3. Draw (visualization)
        draw(game, player_1, player_2)
