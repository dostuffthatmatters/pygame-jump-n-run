
import pygame

from engine.sprite import Sprite
from engine.constants import *

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


heart_full_sprite = get_sprite(heart_spritesheet, 0, 0, 1, size=(40, 40))
heart_empty_sprite = get_sprite(heart_spritesheet, 0, 2, 1, size=(40, 40))
dead_enemy_sprite = get_sprite(enemy_spritesheet, 0, 4, 1, size=(32, 34))

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

get_pole = lambda i: get_sprite(pole_spritesheet, i, 0, 1, size=[SCALING_FACTOR*1.5] * 2)
pole_top_sprite, pole_mid_sprite, pole_bottom_sprite = get_pole(0), get_pole(1), get_pole(2)
flag_sprite = get_sprite(flag_spritesheet, 0, 0, 1, size=[SCALING_FACTOR*2]*2)

def draw_win_column(game):

    flag_image = pygame.transform.rotate(flag_sprite.getImage(), 90)
    game.draw_sprite_element(flag_image, center_position=(47.9, 12.3))

    for h in range(0, 7):
        game.draw_sprite_element(pole_mid_sprite.getImage(), center_position=(47, 1.75+(1.5*h)))
    game.draw_sprite_element(pole_top_sprite.getImage(), center_position=(47, 12.25))
