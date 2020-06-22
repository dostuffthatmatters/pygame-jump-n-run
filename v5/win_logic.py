
# Constants
from engine.constants import *

# Components
from v5.player import Player


def check_for_win(win_area, sorted_scores):

    for player in Player.instances:
        if not player.won:
            if win_area[0][0] <= player.position[0] <= win_area[0][1]:
                if win_area[1][0] <= player.position[1] <= win_area[1][1]:
                    player.won = True

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

    return sorted_scores


def draw_flag_pole(game):
    game.draw_rect(
        46.8 * SCALING_FACTOR, game.height - (12 * SCALING_FACTOR),
        (0.4 * SCALING_FACTOR), (10.5 * SCALING_FACTOR), color=(230, 230, 0)
    )
    game.draw_circle(47 * SCALING_FACTOR, game.height - (12 * SCALING_FACTOR), 0.4 * SCALING_FACTOR,
                     color=(200, 200, 0))


def draw_scores(game, sorted_scores):
    if len(sorted_scores) > 1:
        if sorted_scores[0]["score"] == sorted_scores[1]["score"]:
            text = "It's a tie!"
        else:
            text = sorted_scores[0]["name"] + " won the game!"

        game.draw_text(text, y_center=100, font_size=30)

    for i in range(len(sorted_scores)):
        game.draw_text(f"{sorted_scores[i]['name']}: {sorted_scores[i]['score']}", y_center=140 + 25 * i, font_size=20)

