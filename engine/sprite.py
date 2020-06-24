import pygame
import os
import sys
import math

from engine.helpers import ends_with
"""
Die Funktionen getAnimationFromFolder und getAnimationFromSpritesheet
geben eine Liste von pygame.image.load-Bildern zurueck. 
"""

def get_animation_from_directory(directory_path):

    assert \
        os.path.isdir(directory_path), \
        "Parameter directory_path does not refer to a directory"

    # Get all image filesnames in that directory
    directory_images = list(filter(
        lambda f: ends_with(f, ('.png', '.jpg', '.jpeg')),
        os.listdir(directory_path)
    ))

    assert \
        len(directory_images) > 0, \
        "No images found in that directory"

    # Load images with pygame
    return [
        pygame.image.load(directory_path + "/" + filename)
        for filename in sorted(directory_images)
    ]

def get_animation_from_spritesheet(
        spritesheet_path,
        row_count=None, column_count=None,
        start_row_index=0, start_column_index=0,
        number_of_images=None
):
    assert \
        os.path.isfile(spritesheet_path), \
        "Parameter spritesheet_path does not refer to a file"
    assert \
        ends_with(spritesheet_path, ('.png', '.jpg', '.jpeg')), \
        "The spritesheet has to be of type png/jpg"
    assert \
        not any([p is None for p in (row_count, column_count)]), \
        "Both row_count and column_count have to be specified"

    if number_of_images is None:
        number_of_images = row_count * column_count
    assert \
        number_of_images <= row_count * column_count,\
        "Parameter number_of_images too large for " \
        "specified row_count and column_count"


    spritesheet = pygame.image.load(spritesheet_path)
    spritesheet_size = spritesheet.get_size()
    sprite_size = [
        round(spritesheet_size[0]/column_count),
        round(spritesheet_size[1]/row_count),
    ]

    animation_images = []
    row_index = start_row_index
    column_index = start_column_index
    for i in range(number_of_images):

        # Get current crop region
        w = sprite_size[0]
        h = sprite_size[1]
        x = column_index * w
        y = row_index * h

        # Generate the single sprite by cropping with (x, y, w, h)
        single_sprite = pygame.Surface(sprite_size)
        single_sprite.blit(spritesheet, (0, 0), (x, y, w, h))
        single_sprite = single_sprite.convert()
        single_sprite.set_colorkey(single_sprite.get_at((0, 0)), pygame.RLEACCEL)

        animation_images.append(single_sprite)

        column_index += 1
        if column_index == column_count:
            column_index = 0
            row_index += 1

    return animation_images


class Sprite(pygame.sprite.Sprite):

    # properties = horizontalSprites, verticalSprites, horizontalStart, verticalStart, numberOfImages
    def __init__(self, directory_path=None, spritesheet_path=None, **kwargs):
        assert \
            isinstance(directory_path, str) and spritesheet_path is None or \
            isinstance(spritesheet_path, str) and directory_path is None, \
            "Exactly one of directory_path or spritesheet_path has to be set as a string"

        if directory_path is not None:
            self.images = get_animation_from_directory(directory_path)
        else:
            self.images = get_animation_from_spritesheet(spritesheet_path, **kwargs)

        self.index = 0
        self.counter = 0

    def update(self, nFrames=5):
        assert nFrames > 0, "nFrames must be greater that 0"
        # nFrames = how many game frames per animation frame update
        self.index = (self.index + 1/nFrames) % len(self.images)

    def reset(self):
        self.index = 0

    def getImage(self):
        return self.images[math.floor(self.index)]


if __name__ == '__main__':

    pygame.init()
    screen = pygame.display.set_mode([600, 400])
    pygame.display.set_caption("Animation Beispiel")
    clock = pygame.time.Clock()

    sprite_1 = Sprite(spritesheet_path="../assets/mario_run_sheet.png", row_count=1, column_count=3)

    sprite_x = 200

    while True:

        sprite_x -= 6
        if sprite_x < -50:
            sprite_x = 650

        # Check Quit Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Draw background
        screen.fill((255, 255, 0))

        image_1 = sprite_1.getImage()
        image_1 = pygame.transform.scale(image_1, (18*4, 28*4))
        image_1 = pygame.transform.flip(image_1, True, False)
        image_1 = pygame.transform.rotate(image_1, 360)
        screen.blit(image_1, (sprite_x, 200))

        sprite_1.update(nFrames=2.5)

        # Update pygame screen
        pygame.display.update()
        clock.tick(30)
