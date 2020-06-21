
import math

SCALING_FACTOR = 20  # pixels/meter
GRAVITY = 9.81 * 9  # m/s^2

RUN_VELOCITY = 10  # m/s
JUMP_HEIGHT = 6  # meter
JUMP_VELOCITY = math.sqrt(2 * GRAVITY * JUMP_HEIGHT)  # m/s

COORDINATE_PRECISION = 2  # Decomals places of coordinates being stored

"""
The game's physics-calculations are accurate, however:

With gravity at 9.81 m/s^2 one jump with 6 meters would take 
about 2.2 seconds (up and down). However with the real gravity
this feels way too slow (I mean real people cannot jump 6 
meters high ;))

So that is why I artificially bumped up the gravity:
x times the gravity -> 1/sqrt(x) times the jump-duration
"""

# For debugging purposes
SLOWDOWN = False
SLOWDOWN_FPS = 4
DRAW_HELPERS = True

ERROR_MARGIN = 0.025
MIN_FPS = 30
MAX_FPS = 60
