
# Libraries
from datetime import datetime

# Constants
from engine.constants import *

# Components
from v6.player import Player


def check_for_win(win_area, sorted_scores, game_finish_time):

    if game_finish_time is None:

        for player in Player.instances:
            # If a player enters the win_area (the flag pole)
            # then the player.won property gets set to true and
            # the player cannot move anymore
            if not player.won:
                if win_area[0][0] <= player.position[0] <= win_area[0][1]:
                    if win_area[1][0] <= player.position[1] <= win_area[1][1]:
                        player.won = True

            # If a players have reached the win_area or have no
            # lifes left then the game os finished -> generate scores
            # and save the game_finish_time
        if all([(player.won or player.lifes_left == 0) for player in Player.instances]):
            scores = []
            for player in Player.instances:
                score = 0
                if player.won:
                    score = round(player.position[1] + 10 * player.enemies_killed + player.lifes_left * 3, 2)
                else:
                    score = 0

                scores.append({"name": player.name, "score": score})

            sorted_scores = list(sorted(scores, key=lambda player: player["score"], reverse=True))
            game_finish_time = datetime.now()

    return sorted_scores, game_finish_time


def draw_flag_pole(game):
    # Draw flag pole to screen
    game.draw_rect_element((47, 6.75), (0.4, 10.5), color=(230, 230, 0))
    game.draw_circle_element((47, 12), 0.4, color=(200, 200, 0))


def draw_scores(game, sorted_scores):
    # Draw scores to screen if scores exist
    if len(sorted_scores) > 0:
        if len(sorted_scores) > 1:
            if sorted_scores[0]["score"] == sorted_scores[1]["score"]:
                text = "It's a tie!"
            else:
                text = sorted_scores[0]["name"] + " won the game!"

            game.draw_text(text, y_center=100, font_size=30)

        for i in range(len(sorted_scores)):
            game.draw_text(f"{sorted_scores[i]['name']}: {sorted_scores[i]['score']}", y_center=140 + 25 * i, font_size=20)
