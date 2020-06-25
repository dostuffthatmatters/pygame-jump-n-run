
import random

# Engine
from engine.sprite import Sprite
from engine.helpers import is_number, merge_into_list_dict, reduce_to_relevant_collisions, get_collision
from engine.tests import TEST_mandatory_coordinates

# Constants
from engine.constants import *


class SquareBarrier:

    # A list of all SquareBarrier instances
    instances = []

    def __init__(
            self,
            x_left=None, x_center=None,
            y_top=None, y_center=None,
            width=1, height=1,
            color=(150, 150, 150),
            sprites=None
    ):

        TEST_mandatory_coordinates(x_left=x_left, x_center=x_center, y_top=y_top, y_center=y_center)

        # self.position is referring to the blocks center
        # All properties as lists with length 2
        # => [x-component, y-component]
        self.position = [
            (x_left + (width/2)) if x_left is not None else x_center,
            (y_top - (height/2)) if y_top is not None else y_center
        ]
        self.size = [width, height]
        self.color = color

        # Add this new instances to the instance-list from above
        SquareBarrier.instances.append(self)

    # Draw a single SquareBarrier instances
    def draw(self, game):
        game.draw_rect_element(self.position, self.size, color=self.color)

    # Draw all SquareBarrier instances
    @staticmethod
    def draw_all(game):
        for barrier in SquareBarrier.instances:
            barrier.draw(game)

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
