
# Engine
from engine.helpers import is_number, merge_into_list_dict, reduce_to_relevant_collisions, get_collision


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
            all_collisions = merge_into_list_dict(
                all_collisions,
                get_collision(barrier=barrier, moving_object=player)
            )

        # 2. Reduce all collisions to the relevant ones, example:
        #    all_collisions['FLOOR'] = [3.0, 4.2, 2.2, 4.0]
        #    -> relevant_collisions['FLOOR'] = 4.2
        return reduce_to_relevant_collisions(all_collisions)
