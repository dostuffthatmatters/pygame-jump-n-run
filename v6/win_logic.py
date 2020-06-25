
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
                        player.calculate_score(height_bonus=True)

            # If a players have reached the win_area or have no
            # lifes left then the game os finished -> generate scores
            # and save the game_finish_time
        if all([(player.won or player.lifes_left == 0) for player in Player.instances]):
            scores = [
                {"name": player.name, "score": player.score}
                for player in Player.instances
            ]
            sorted_scores = list(sorted(scores, key=lambda player: player["score"], reverse=True))
            game_finish_time = datetime.now()

    return sorted_scores, game_finish_time
