
import math

SCALING_FACTOR = 20  # pixels/meter
GRAVITY = 9.81 * 9  # m/s^2

RUN_VELOCITY = 10  # m/s
JUMP_HEIGHT = 6  # meter
JUMP_VELOCITY = math.sqrt(2 * GRAVITY * JUMP_HEIGHT)  # m/s

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
MIN_DRAW_FPS = 30
MAX_DRAW_FPS = 60

COORDINATE_PRECISION = 4  # Decimals places of coordinates being stored
SIMULATION_FRAMES_PER_DRAW = 10

# Careful: The more frames per seconds are being simulated the smaller
#          the changes in position and velocity will be therefore the
#          COORDINATE_PRECISION has to be higher!
