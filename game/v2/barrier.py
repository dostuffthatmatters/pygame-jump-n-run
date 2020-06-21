
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

        # self.position is referring to the blocks center
        self.position = [
            (x_left + (width/2)) if x_left is not None else x_center,
            (y_top - (height/2)) if y_top is not None else y_center
        ]
        self.size = [width, height]
        self.color = color

        SquareBarrier.instances.append(self)

    @staticmethod
    def draw_all(game):
        for barrier in SquareBarrier.instances:
            game.draw_rect_element(barrier.position, barrier.size, color=barrier.color)

    def detect_collision(self, player):
        dx_min = player.size[0]/2 + self.size[0]/2
        dy_min = player.size[1]/2 + self.size[1]/2

        dx = player.position[0] - self.position[0]  # dx > 0 = player is right from the barrier
        dy = player.position[1] - self.position[1]  # dy > 0 = player is above the barrier

        horizontal_overlap = (dx_min - abs(dx))
        vertical_overlap = (dy_min - abs(dy))

        collision = {}

        if vertical_overlap > 0 and horizontal_overlap > 0:

            if vertical_overlap < horizontal_overlap:
                if dy > 0:
                    collision = {"FLOOR": self.position[1] + self.size[1]/2}
                else:
                    collision = {"CEILING": self.position[1] - self.size[1]/2}
            else:
                if dx > 0:
                    collision = {"LEFT_WALL": self.position[0] + self.size[0]/2}
                else:
                    collision = {"RIGHT_WALL": self.position[0] - self.size[0]/2}

        return collision

    @staticmethod
    def detect_all_collisions(player):
        # 1. Fetch all possiple collisions
        all_collisions = {
            'FLOOR': [],
            'CEILING': [],
            'LEFT_WALL': [],
            'RIGHT_WALL': [],
        }
        for barrier in SquareBarrier.instances:
            single_collision = barrier.detect_collision(player)
            for side in single_collision:
                all_collisions[side].append(single_collision[side])

        # 2. Reduce all collisions to the relevant ones, example:
        #    all_collisions['FLOOR'] = [3.0, 4.2, 2.2, 4.0]
        #    -> relevant_collisions['FLOOR'] = 4.2
        relevant_collisions = {}
        for side in all_collisions:
            collisions_count = len(all_collisions[side])
            if collisions_count > 0:
                if collisions_count > 1:
                    all_collisions[side] = list(sorted(all_collisions[side], reverse=side in ('FLOOR', 'LEFT_WALL')))
                relevant_collisions[side] = all_collisions[side][0]

        return relevant_collisions
