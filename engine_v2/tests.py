
# Constants
from pygame.constants import *


"""
These test are very useful to have a better debugging experience!

Basically with it tests wether certain conditions are true. As a 
programmer, we assume (aka assert) that these conditions are true
if our code is correct. Therefore we can use an automatic test when
we know these conditions.

Without Assertion: A wrong/invalid value will cause the program to
crash at some point and we get a rather cryptic error message.

With Assertion: We get the error right where the value is wrong/
invalid with an error message we can write ourselves.

Usage: assert <condition>, <Error text if condition is false>

You can learn more about Assertion here: https://www.tutorialspoint.com/python/assertions_in_python.htm
"""

# I cannot use the one from engine.tests because that would lead to
# a circular import = tests needs helpers <-> helpers needs tests
def is_number(x):
    return any([isinstance(x, _type) for _type in (int, float)])


def TEST_keymap(keymap, sides=('UP', 'DOWN', 'LEFT', 'RIGHT')):
    assert \
        all([side in keymap.values() for side in sides]), \
        f'All keys {sides} required in keymap property'

    assert \
        all([isinstance(key, int) for key in keymap.keys()]), \
        f'All keys for {sides} in keymap property have to be integers (e.g. pygame.K_UP)'

    assert len(keymap) == len(sides), 'Only keys for [UP, LEFT, DOWN, RIGHT] allowed in keymap property'

def TEST_keypress(keymap, event_key):
    assert \
        event_key in keymap.keys(), \
        f"Only key-events from {keymap} allowed"

def TEST_mandatory_coordinates(x_left=None, x_center=None, y_top=None, y_center=None):
    assert \
        x_left is None and x_center is not None or \
        x_center is None and x_left is not None, \
        "Exactly one of (x_left, x_center) has to be set"
    assert \
        is_number(x_left if x_left is not None else x_center), \
        "x has to be a number (integer or float)"
    assert \
        y_top is None and y_center is not None or \
        y_center is None and y_top is not None, \
        "Exactly one of (y_top, y_center) has to be set"
    assert \
        is_number(y_top if y_top is not None else y_center), \
        "y has to be a number (integer or float)"

def TEST_optional_coordinates(
        x_left=None, x_center=None, x_right=None,
        y_top=None, y_center=None, y_bottom=None
):
    assert \
        len(list(filter(lambda x: x is not None, (x_left, x_center, x_right)))) <= 1,\
        "Can only set one of (x_left, x_center, x_right) at once"
    assert \
        all([is_number(x) or x is None for x in (x_left, x_center, x_right)]), \
        "x has to be a number (integer or float)"

    assert \
        len(list(filter(lambda y: y is not None, (y_top, y_center, y_bottom)))) <= 1, \
        "Can only set one of (y_top, y_center, y_bottom) at once"
    assert \
        all([is_number(y) or y is None for y in (y_top, y_center, y_bottom)]), \
        "y has to be a number (integer or float)"

def TEST_object_attributes(game_object, attributes=("position", "size", "color")):
    for attribute in attributes:
        assert hasattr(game_object, attribute), f"Game object has not attribute {attribute}"

def TEST_color(color):
    assert all([0 <= c <= 255 for c in color]), f"Color components out of range, color={color}"
    assert all([isinstance(c, int) for c in color]), f"Color components have to be integers, color={color}"

def TEST_value_range(value_range):
    assert \
        isinstance(value_range, tuple) or isinstance(value_range, list),\
        "value_range has to be a tuple or a list"
    assert len(value_range) == 2, "value_range must contain exactly two values"
    assert all([is_number(v) for v in value_range]), "value_range must contain only integers and floats"
    assert value_range[1] > value_range[0], "value_range invalid: min >= max"

def TEST_perlin_weights(width, weights):
    assert isinstance(weights, dict), "Weights has to be a dictionary"
    assert all([isinstance(w, int) for w in weights]), "All weight keys must be integers"
    assert all([is_number(w) for w in weights]), "All weight keys must be numbers"
    assert all(
        [int(width/key) == (width/key) for key in weights]
    ), "The width must be dividable by all weight keys"


