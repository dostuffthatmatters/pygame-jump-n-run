
# Libraries
import pygame
from pygame import gfxdraw
import sys

# Engine
from engine.tests import TEST_optional_coordinates, TEST_color, TEST_object_attributes
from engine.helpers import reverse_color

# Constants
from pygame.locals import DOUBLEBUF
from engine.constants import *


"""
The purpose of this class is just to provide a more comfortable
development experience with pygame.

It provides basic boilerplate functionality and makes all drawing
functions homogeneous and more intuitive. Also all shapes are drawn
with antialiasing enabled.

gfxdraw provides antialiased draw methods.
See full reference at: http://www.pygame.org/docs/ref/gfxdraw.html

To be clear: You don't have to use this!!! It's just something I
find useful. You may add further functionality as you like
"""

class Game():

    def __init__(
            self, width=500, height=500,
            title="MyGame", font_family='Roboto',
            track_fps=True, print_fps=True,
            max_fps=240
    ):

        self.width = width
        self.height = height
        self.font_family = font_family

        if track_fps:
            self.clock = pygame.time.Clock()
            self.max_fps = max_fps
            self.fps = max_fps
        else:
            assert not print_fps, "Cannot print_fps without track_fps=True"

        self.track_fps = track_fps
        self.print_fps = print_fps

        pygame.init()
        self.window = pygame.display.set_mode((width, height), DOUBLEBUF)
        pygame.display.set_caption(title)

        # Has to be called to use fonts at some point
        pygame.font.init()

    def draw_rect(self, x, y, width, height, color=(0, 0, 0), alpha=1):
        gfxdraw.box(self.window, (x, y, width, height), list(color) + [int(alpha * 255)])

    def draw_circle(self, x, y, radius, color=(0, 0, 0)):
        x, y, radius = math.ceil(x), math.ceil(y), math.ceil(radius)
        gfxdraw.aacircle(self.window, x, y, radius, color)
        gfxdraw.filled_circle(self.window, x, y, radius, color)

    def draw_polygon(self, points, color=(0, 0, 0)):
        gfxdraw.aapolygon(game_window, points, color)
        gfxdraw.filled_polygon(game_window, points, color)

    # You can pass in either the texts center coordinates or it edge coordinates
    # or not coordinates at all for both dimensions. In the last case the text will
    # be places in the windows center
    def draw_text(
            self, text,
            x_center=None, y_center=None,
            x_left=None, y_top=None,
            font_family=None, font_size=30,
            color=(0, 0, 0)
    ):
        TEST_optional_coordinates(x_left=x_left, x_center=x_center, y_top=y_top, y_center=y_center)

        font = pygame.font.SysFont(self.font_family if font_family is None else font_family, font_size)
        surface = font.render(text, True, color)
        (rx, ry, rw, rh) = surface.get_rect()  # The rectangle enclosing the text

        if x_left is None and x_center is None:
            x = round((self.width - rw)/2)  # If nothing has been set, use window center
        else:
            x = round(x_center - (rw/2)) if x_center is not None else round(x_left)

        if y_top is None and y_center is None:
            y = round((self.height - rh)/2)  # If nothing has been set, use window center
        else:
            y = round(y_center - (rh/2)) if y_center is not None else round(y_top)

        self.window.blit(surface, (x, y))

    def draw_background(self, color=(255, 255, 255)):
        TEST_color(color)
        self.window.fill(color)

    def update(self):
        # 1. Update fps
        if self.track_fps:
            # self.fps converges towards the actual fps -> reduces noise in fps
            timedelta = self.clock.tick(self.max_fps) * 0.001
            new_fps = round((self.fps*5 + (1/timedelta))/6)

            if self.print_fps and self.fps != new_fps:
                print("{:3d} FPS".format(round(new_fps)))

            self.fps = new_fps

        # 2. Update game window
        pygame.display.update()

    def get_mouse_position(self):
        if pygame.mouse.get_focused() == 0:
            return None  # If mouse is not in window
        else:
            return pygame.mouse.get_pos()

    def exit(self):
        pygame.quit()
        sys.exit()

    # Draw a rect from its center-position with the SCALING factor from
    # engine.constants applied and regular cartesion coordinates (y axis
    # points upwards)
    def draw_rect_element(self, position, size, color=(0, 0, 0), alpha=1):
        rect_w = size[0] * SCALING_FACTOR
        rect_h = size[1] * SCALING_FACTOR
        rect_x = position[0] * SCALING_FACTOR - (rect_w/2)
        rect_y = self.height - (position[1] * SCALING_FACTOR + (rect_h/2))
        self.draw_rect(rect_x, rect_y, rect_w, rect_h, color=color, alpha=alpha)

    # Draw a circle from its center-position with the SCALING factor from
    # engine.constants applied and regular cartesion coordinates (y axis
    # points upwards)
    def draw_circle_element(self, position, radius, color=(0, 0, 0)):
        circle_x = position[0] * SCALING_FACTOR
        circle_y = self.height - (position[1] * SCALING_FACTOR)
        circle_r = radius * SCALING_FACTOR
        self.draw_circle(circle_x, circle_y, circle_r, color=color)

    # Draw small helper circles indicating the center of a game element as
    # well as possible collisions
    def draw_helper_points(self, game_object):
        TEST_object_attributes(game_object, attributes=("position", "size", "color"))

        reversed_color = reverse_color(game_object.color)
        circle_radius = min(game_object.size) * 0.15
        self.draw_circle_element(game_object.position, circle_radius, color=reversed_color)

        if hasattr(game_object, "collisions"):
            circle_offsets = {
                "FLOOR": [0, -0.5 * game_object.size[1]],
                "CEILING": [0, 0.5 * game_object.size[1]],
                "LEFT_WALL": [-0.5 * game_object.size[0], 0],
                "RIGHT_WALL": [0.5 * game_object.size[0], 0],
            }
            for side in circle_offsets:
                if game_object.collisions[side] is not None:
                    position = [game_object.position[dim] + circle_offsets[side][dim] for dim in (0, 1)]
                    self.draw_circle_element(position, circle_radius, color=reversed_color)

    def draw_sprite(self, image, center_position):
        width, height = image.get_rect()[2:]
        self.window.blit(image, (center_position[0]-(width/2), center_position[1]-(height/2)))

    def draw_sprite_element(self, image, center_position, sprite_offset=(0, 0)):
        center_position = [
            (center_position[0] + sprite_offset[0]) * SCALING_FACTOR,
            self.height - (center_position[1] + sprite_offset[1]) * SCALING_FACTOR
        ]
        self.draw_sprite(image, center_position)
