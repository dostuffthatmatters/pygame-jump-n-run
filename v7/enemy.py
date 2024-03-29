
# Engine
from engine_v2.perlin import PerlinNoise1D
from engine_v2.helpers import merge_into_list_dict, get_collision
from engine_v2.sprite import Sprite

# Constants
from engine_v2.constants import *

# Components
from v7.barrier import Barrier


class Enemy:

    # A list of all Enemy instances
    instances = []

    def __init__(
            self,
            color=(75, 75, 75),
            position=(0, 0),
            size=(14*0.075, 17*0.075)
    ):

        # All properties as lists with length 2
        # => [x-component, y-component]
        self.position = position
        self.velocity = [0.0, 0.0]
        self.size = list(size)

        # The perlin noise used for the velocity
        self.noise_index = 0
        self.noise_sign = 1
        self.noise = PerlinNoise1D(
            value_range=(-ENEMY_RUN_VELOCITY, ENEMY_RUN_VELOCITY),
            repeatable=True
        )

        self.color = color

        # Attach sprite and scale sprite to the enemies given size
        sprite_size = [SCALING_FACTOR * s for s in size]
        self.sprite = Sprite(
            spritesheet_path="assets/dungeon_spritesheets/enemy_spritesheet@8x.png",
            row_count=1, column_count=5, number_of_images=4, size=sprite_size
        )

        # The collisions that are currently being detected
        self.collisions = {
            'CEILING': None,
            'FLOOR': None,
            'LEFT_WALL': None,
            'RIGHT_WALL': None
        }

        # Add this new instances to the instance-list from above
        Enemy.instances.append(self)

    def update_for_collisions(self, new_velocity, new_position):
        # 1. Detecting movement collisions with Barriers and other
        #    players. Collisions should refer to the new velocity
        #    and new position that is why we preliminarily update
        #    the players state (self.)
        self.velocity, self.position = new_velocity, new_position
        all_collisions = Barrier.detect_all_collisions(self)

        # The strategy now is to go through all the collisions that
        # were detected and successively adjust new_velocity and
        # new_position if needed. In the end the players state (self.
        # will be updated with the adjusted position/velocity once
        # again

        new_collisions = {
            'CEILING': None,
            'FLOOR': None,
            'LEFT_WALL': None,
            'RIGHT_WALL': None
        }

        # "Snap" to Wall/Floor/Ceiling when hitting one. Example
        #   Moving left & new_x = -0.04
        #   Wall detected at x=0
        #   Snaps to x=0 and velocity *= -1 (turns around)
        def fix_position(side):
            dimension = 1 if (side in ('FLOOR', 'CEILING')) else 0
            coordinate_direction = +1 if (side in ('FLOOR', 'LEFT_WALL')) else -1

            if dimension == 0:
                # Turn around at wall
                self.noise_sign *= -1
                new_velocity[0] *= -1
                limit_center_offset = 0
            else:
                # Stop at floor/ceiling
                new_velocity[1] = 0
                limit_center_offset = ((self.size[dimension]/2) - ERROR_MARGIN) * coordinate_direction

            new_position[dimension] = all_collisions[side] + limit_center_offset
            new_collisions[side] = all_collisions[side]

        # 2. React to vertical collisions
        if all_collisions['FLOOR'] is not None and new_velocity[1] < ERROR_MARGIN:
            fix_position('FLOOR')
        elif all_collisions['CEILING'] is not None and new_velocity[1] > -ERROR_MARGIN:
            fix_position('CEILING')

        # 3. React to horizontal collisions. Left and Right wall block
        # is only applied if the enemy is moving towards that barrier
        if all_collisions['LEFT_WALL'] is not None and new_velocity[0] < ERROR_MARGIN:
            fix_position('LEFT_WALL')
        elif all_collisions['RIGHT_WALL'] is not None and new_velocity[0] > -ERROR_MARGIN:
            fix_position('RIGHT_WALL')

        # 4. Now new_velocity and new_position has been adjusted to conform
        #    with collisions -> player state will be updated with the adjusted
        #    values
        self.collisions = new_collisions
        self.velocity = [round(v, COORDINATE_PRECISION) for v in new_velocity]
        self.position = [round(p, COORDINATE_PRECISION) for p in new_position]

    # Update a single Enemy instance
    def update(self, timedelta):
        # Get the current velocity with perlin noise
        self.noise_index = (self.noise_index + timedelta*1.5) % 127
        run_velocity = self.noise_sign * self.noise[self.noise_index]

        # Preliminary new velocity
        new_velocity = [run_velocity, 0.0]

        # Set correct sprite flip direction for the current movement direction
        if run_velocity >= 0:
            self.sprite.flip = (False, False)
        else:
            self.sprite.flip = (True, False)

        # Only update the sprite if the enemy is moving
        if abs(run_velocity) > 0.05 * ENEMY_RUN_VELOCITY:
            # The update frequency is proportional to the velocity
            self.sprite.update(timedelta, fps=abs(MAX_ENEMY_RUN_FPS * run_velocity)/ENEMY_RUN_VELOCITY)

        # Set current vertical velocity according to
        # self.collisions and jump if velocity is high
        if self.collisions['FLOOR'] is not None:
            if abs(run_velocity) > (0.7 * ENEMY_RUN_VELOCITY):
                if self.velocity[1] < ERROR_MARGIN:
                    new_velocity[1] = ENEMY_JUMP_VELOCITY
        else:
            new_velocity[1] = self.velocity[1] - GRAVITY * timedelta

        # Preliminary new position
        new_position = [
            self.position[0] + new_velocity[0] * timedelta,
            self.position[1] + new_velocity[1] * timedelta
        ]

        # Adjust new_velocity and new_position by detecting collisions
        # for the new state and modifying the new state to comply with
        # the collisions with barriers
        self.update_for_collisions(new_velocity, new_position)

        # Occasionally enemies somehow glitch outside the drawing area -> this is a monkey patch
        if any([abs(p) > 200 for p in self.position]):
            self.kill()

    # Update all Enemy instances
    @staticmethod
    def update_all(timedelta):
        for enemy in Enemy.instances:
            enemy.update(timedelta)

    # Draw a single Enemy instance
    def draw(self, game):
        # Draw the sprite using the draw_sprite_rect method from the Game class
        game.draw_sprite_element(self.sprite.getImage(), center_position=self.position)

        if DRAW_HELPERS:
            game.draw_rect_element(self.position, self.size, color=self.color, alpha=0.3)
            game.draw_helper_points(self)

    # Draw all Enemy instances
    @staticmethod
    def draw_all(game):
        for enemy in Enemy.instances:
            enemy.draw(game)

    # The method used by a player to detect all collisions with
    # enemies from the Enemy.instances list
    @staticmethod
    def detect_all_collisions(player):
        all_collisions = {
            'BARRIER_KILLED': [],
            'MOVING_OBJECT_KILLED': [],
        }
        for enemy in Enemy.instances:
            all_collisions = merge_into_list_dict(
                all_collisions, get_collision(
                    barrier=enemy, moving_object=player, combat_collision=True
                )
            )

        return all_collisions

    def kill(self):
        # "kill" the Enemy instance by remove it from the instance list
        Enemy.instances.remove(self)
