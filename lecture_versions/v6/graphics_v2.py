
# Libraries
import pygame

# Engine
from lecture_versions.engine.sprite import Sprite

# Constants
from lecture_versions.engine.constants import *


# Spritesheets in use
heart_spritesheet = {
    "spritesheet_path": "assets/dungeon_spritesheets/heart_spritesheet@8x.png",
    "row_count": 1, "column_count": 3,
}
enemy_spritesheet = {
    "spritesheet_path": "assets/dungeon_spritesheets/enemy_spritesheet@8x.png",
    "row_count": 1, "column_count": 5,
}
player_spritesheet = {
    "spritesheet_path": "assets/dungeon_spritesheets/player_spritesheet@8x.png",
    "row_count": 2, "column_count": 9,
}
pole_spritesheet = {
    "spritesheet_path": "assets/dungeon_spritesheets/pole_spritesheet@8x.png",
    "row_count": 3, "column_count": 1,
}
flag_spritesheet = {
    "spritesheet_path": "assets/dungeon_spritesheets/flag_spritesheet@8x.png",
    "row_count": 1, "column_count": 4,
}


# This function shortens the sprite access notation
def get_sprite(spritesheet, i, j, n, **kwargs):
    # kwarges is stuff like size and scale
    return Sprite(
        **spritesheet,
        row_start_index=i, column_start_index=j, number_of_images=n,
        **kwargs
    )


# The sprites the two players will use. Will be passed to the player
# upon the player initialization inside main after the graphics import
player_1_sprites = {
    "sprite_run": get_sprite(player_spritesheet, 0, 0, 8),
    "sprite_jump_up": get_sprite(player_spritesheet, 0, 0, 1),
    "sprite_jump_down": get_sprite(player_spritesheet, 0, 8, 1)
}
player_2_sprites = {
    "sprite_run": get_sprite(player_spritesheet, 1, 0, 8),
    "sprite_jump_up": get_sprite(player_spritesheet, 1, 0, 1),
    "sprite_jump_down": get_sprite(player_spritesheet, 1, 8, 1)
}


# Draws the winning pole on the right hand side
get_pole = lambda i: get_sprite(pole_spritesheet, i, 0, 1, size=[SCALING_FACTOR*1.5] * 2)
pole_top_sprite, pole_mid_sprite, pole_bottom_sprite = get_pole(0), get_pole(1), get_pole(2)
flag_sprite = get_sprite(flag_spritesheet, 0, 0, 1, size=[SCALING_FACTOR*2]*2)
def draw_winning_pole(game):
    # Flag at the top
    flag_image = pygame.transform.rotate(flag_sprite.getImage(), 90)
    game.draw_sprite_element(flag_image, center_position=(47.9, 12.3))

    # Regular pole segment
    for h in range(0, 7):
        game.draw_sprite_element(pole_mid_sprite.getImage(), center_position=(47, 1.75+(1.5*h)))

    # Top pole segment
    game.draw_sprite_element(pole_top_sprite.getImage(), center_position=(47, 12.25))


# Draws the graphical game stats, when DRAW_HELPERS is set to false
heart_full_sprite = get_sprite(heart_spritesheet, 0, 0, 1, size=(40, 40))
heart_empty_sprite = get_sprite(heart_spritesheet, 0, 2, 1, size=(40, 40))
dead_enemy_sprite = get_sprite(enemy_spritesheet, 0, 4, 1, size=(32, 34))
def draw_player_stats(game, player_1, player_2):

    # Player name + score
    game.draw_text(
        text=f"Player \"{player_1.name}\": {player_1.score} points",
        x_left=18, y_top=10, font_size=20, color=player_1.color
    )
    game.draw_text(
        text=f"Player \"{player_2.name}\": {player_2.score} points",
        x_right=18, y_top=10, font_size=20, color=player_2.color
    )

    # Player lifes lefts
    for i in range(3):
        if player_1.lifes_left > i:
            player_1_heart = heart_full_sprite.getImage()
        else:
            player_1_heart = heart_empty_sprite.getImage()
        if player_2.lifes_left > i:
            player_2_heart = heart_full_sprite.getImage()
        else:
            player_2_heart = heart_empty_sprite.getImage()
        game.draw_sprite(player_1_heart, (32 + i*32, 56))
        game.draw_sprite(player_2_heart, (game.width - 32 - i*32, 56))

    # Enemies killed
    for i in range(player_1.enemies_killed):
        game.draw_sprite(dead_enemy_sprite.getImage(), (32 + i * 32, 90))
    for i in range(player_2.enemies_killed):
        game.draw_sprite(dead_enemy_sprite.getImage(), (game.width - 32 - i * 32, 90))


# Draws the debugging stats, when DRAW_HELPERS is set to true
def draw_debug_stats(game, player_1):
    game.draw_text(text=f"collisions: {player_1.collisions}",
                   x_left=5, y_top=5, font_size=20, color=player_1.color)
    game.draw_text(text=f"position: {player_1.position}, velocity: {player_1.velocity}",
                   x_left=5, y_top=30, font_size=20, color=player_1.color)


# Draws the fps in the bottom left corner
def draw_fps(game):
    game.draw_text(
        text=f"{game.fps * SIMULATION_FRAMES_PER_DRAW} FPS (simulation) {game.fps} FPS (canvas)",
        x_left=6, y_bottom=6, font_size=12
    )


# Draws the  final scores to the screen
def draw_scores(game, sorted_scores):
    if len(sorted_scores) > 0:
        if len(sorted_scores) > 1:
            if sorted_scores[0]["score"] == sorted_scores[1]["score"]:
                text = "It's a tie!"
            else:
                text = sorted_scores[0]["name"] + " won the game!"

            game.draw_text(text, y_center=100, font_size=30)

        for i in range(len(sorted_scores)):
            game.draw_text(f"{sorted_scores[i]['name']}: {sorted_scores[i]['score']}", y_center=140 + 25 * i, font_size=20)
