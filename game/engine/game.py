
import pygame
from pygame import gfxdraw
import sys
import math
from datetime import datetime

from pygame.locals import DOUBLEBUF


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
            max_fps=240,
    ):

        self.width = width
        self.height = height
        self.font_family = font_family

        if track_fps:
            self.clock = pygame.time.Clock()
            self.max_fps = max_fps
            self.fps = max_fps
        else:
            assert not print_fps, "Cannot print_fps without track_fps"

        self.track_fps = track_fps
        self.print_fps = print_fps

        pygame.init()
        self.window = pygame.display.set_mode((width, height), DOUBLEBUF)
        pygame.display.set_caption(title)

        # Has to be called to use fonts at some point
        pygame.font.init()

    def draw_rect(self, x, y, width, height, color=(0, 0, 0), alpha=1):
        if x < 0:
            width += x
            x = 0
            if width <= 0:
                return

        if y < 0:
            height += y
            y = 0
            if height <= 0:
                return

        gfxdraw.box(self.window, (x, y, width, height), list(color) + [int(alpha * 255)])

    def draw_circle(self, x, y, radius, color=(0, 0, 0)):
        x, y, radius = math.ceil(x), math.ceil(y), math.ceil(radius)
        gfxdraw.aacircle(self.window, x, y, radius, color)
        gfxdraw.filled_circle(self.window, x, y, radius, color)

    def draw_polygon(self, points, color=(0, 0, 0)):
        gfxdraw.aapolygon(game_window, points, color)
        gfxdraw.filled_polygon(game_window, points, color)

    def draw_text(
            self, text,
            x_center=None, y_center=None,
            x_left=None, y_top=None,
            font_family=None, font_size=30,
            color=(0, 0, 0)
    ):
        font = pygame.font.SysFont(self.font_family if font_family is None else font_family, font_size)

        surface = font.render(text, True, color)

        # The rectangle enclosing the text
        (rx, ry, rw, rh) = surface.get_rect()

        assert (
                x_center is None or x_left is None
        ), "Cannot set both x_center and x_left at the same time"
        assert (
                y_center is None or y_top is None
        ), "Cannot set both y_center and y_top at the same time"

        if x_left is None and x_center is None:
            # If nothing has been set, use window center
            x = round((self.width - rw)/2)
        elif x_center is not None:
            x = round((x_center) - (rw/2))
        else:
            x = round(x_left)

        if y_top is None and y_center is None:
            # If nothing has been set, use window center
            y = round((self.height - rh)/2)
        elif y_center is not None:
            y = round((y_center) - (rh/2))
        else:
            y = round(y_top)

        self.window.blit(surface, (x, y))

    def draw_background(self, color=(255, 255, 255)):
        self.window.fill(color)

    def update(self, rects=None):
        if self.track_fps:
            max_fps = self.max_fps

            timedelta = self.clock.tick(max_fps) * 0.001
            # self.fps converges towards the actual fps -> reduces noise in fps
            new_fps = round((self.fps*5 + (1/timedelta))/6)

            if self.print_fps and self.fps != new_fps:
                print("{:3d} FPS".format(round(new_fps)))

            self.fps = new_fps

        if rects is None:
            pygame.display.update()
        else:
            pygame.display.update(rects)

    def get_mouse_position(self):
        if pygame.mouse.get_focused() == 0:
            # If mouse is not in window
            return None
        else:
            return pygame.mouse.get_pos()

    def exit(self):
        pygame.quit()
        sys.exit()
