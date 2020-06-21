
from game.engine.constants import *

def is_number(x):
    return any([isinstance(x, _type) for _type in (int, float)])


class SquareBarrier:

    instances = []

    def __init__(
            self,
            x_left=None, x_center=None,
            y_top=None, y_center=None,
            width=1, height=1,
            color=(150, 150, 150)
    ):

        # Just some tests to validate that the correct init_values are given
        assert \
            x_left is None and x_center is not None or \
            x_center is None and x_left is not None, \
            "Exactly one of (x_left, x_center) has to be set"
        assert \
            is_number(x_left if x_left is not None else x_center),\
            "x has to be a number (integer or float)"
        assert \
            y_top is None and y_center is not None or \
            y_center is None and y_top is not None, \
            "Exactly one of (y_top, y_center) has to be set"
        assert \
            is_number(y_top if y_top is not None else y_center), \
            "y has to be a number (integer or float)"

        # self.x/self.y is referencing the blocks center
        self.x = x_left + width/2 if x_left is not None else x_center
        self.y = y_top - height/2 if y_top is not None else y_center

        self.width = width
        self.height = height

        self.color = color

        SquareBarrier.instances.append(self)

    def draw(self, game):
        w = self.width * SCALING_FACTOR
        h = self.height * SCALING_FACTOR
        x = (self.x * SCALING_FACTOR) - (w/2)
        y = game.height - ((self.y * SCALING_FACTOR) + (h/2))
        game.draw_rect(x, y, w, h, color=self.color)

    @staticmethod
    def draw_all(game):
        for barrier in SquareBarrier.instances:
            barrier.draw(game)

    @staticmethod
    def create(x_left, y_top, width, height, color=(150, 150, 150)):
        SquareBarrier(x_left=x_left, y_top=y_top, width=width, height=height, color=color)

    def detect_collision(self, x_center, y_center, width, height):
        dx_min = width/2 + self.width/2
        dy_min = height/2 + self.height/2

        dx = x_center - self.x  # dx > 0 = player is right from the barrier
        dy = y_center - self.y  # dy > 0 = player is above the barrier

        collision = {}

        if dx_min > abs(dx) and dy_min > abs(dy):
            # Overlaps!

            vertical_overlap = (dy_min-abs(dy))
            horizontal_overlap = (dx_min-abs(dx))

            if vertical_overlap < horizontal_overlap:
                if dy > 0:
                    collision = {"FLOOR": self.y + self.height/2}
                else:
                    collision = {"CEILING": self.y - self.height/2}
            else:
                if dx > 0:
                    collision = {"LEFT_WALL": self.x + self.width/2}
                else:
                    collision = {"RIGHT_WALL": self.x - self.width/2}

            assert len(collision) > 0, "Math is wrong"

        return collision

    @staticmethod
    def detect_all_collisions(x_center, y_center, width, height):
        all_collisions = {}
        for barrier in SquareBarrier.instances:
            single_collision = barrier.detect_collision(x_center, y_center, width, height)
            for side in single_collision:
                # Only detect one collision per direction yet!
                if side not in all_collisions:
                    all_collisions[side] = single_collision[side]
        return all_collisions
