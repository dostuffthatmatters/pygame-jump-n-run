
import pygame
from game.v4.barrier import SquareBarrier
from game.v4.perlin import PerlinNoise1D

from pygame.constants import *
from game.engine.constants import *

class Enemy:

    # Keeps track of all instances of the Player class
    instances = []

    def __init__(
            self,
            color=(75, 75, 75),
            position=(0, 0),
            width=0.8,
            height=1.2,
    ):
        self.position = position
        self.velocity = [0.0, 0.0]
        self.size = [width, height]

        self.noise_index = 0
        self.noise = PerlinNoise1D(
            value_range=(-ENEMY_RUN_VELOCITY, ENEMY_RUN_VELOCITY),
            repeatable=True
        )
        self.noise_sign = 1

        self.color = color

        self.collisions = {
            'CEILING': None,
            'FLOOR': None,
            'LEFT_WALL': None,
            'RIGHT_WALL': None
        }

        # Add this new instance to the instance-list Player.players
        Enemy.instances.append(self)

    def update_for_collisions(self, new_velocity, new_position):
        all_collisions = SquareBarrier.detect_all_collisions(self)

        new_collisions = {
            'CEILING': None,
            'FLOOR': None,
            'LEFT_WALL': None,
            'RIGHT_WALL': None
        }

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

        if 'FLOOR' in all_collisions and new_velocity[1] < ERROR_MARGIN:
            fix_position('FLOOR')
        elif 'CEILING' in all_collisions and new_velocity[1] > -ERROR_MARGIN:
            fix_position('CEILING')

        if 'LEFT_WALL' in all_collisions and new_velocity[0] < ERROR_MARGIN:
            fix_position('LEFT_WALL')
        elif 'RIGHT_WALL' in all_collisions and new_velocity[0] > -ERROR_MARGIN:
            fix_position('RIGHT_WALL')

        self.collisions = new_collisions
        self.velocity = [round(v, COORDINATE_PRECISION) for v in new_velocity]
        self.position = [round(p, COORDINATE_PRECISION) for p in new_position]

    def update(self, timedelta):
        self.noise_index += timedelta
        noise_value = self.noise_sign * self.noise[self.noise_index % 128]
        new_velocity = [noise_value, 0]

        if (
            (self.collisions['RIGHT_WALL'] is not None and new_velocity[0] > 0) or
            (self.collisions['LEFT_WALL'] is not None and new_velocity[0] < 0)
        ):
            new_velocity[0] *= -1


        if self.collisions['FLOOR'] is not None:
            if abs(self.noise[self.noise_index]) > (0.7 * ENEMY_RUN_VELOCITY):
                if self.velocity[1] < ERROR_MARGIN:
                    new_velocity[1] = ENEMY_JUMP_VELOCITY
        else:
            new_velocity[1] = self.velocity[1] - GRAVITY * timedelta

        new_position = [
            self.position[0] + new_velocity[0] * timedelta,
            self.position[1] + new_velocity[1] * timedelta
        ]

        self.update_for_collisions(new_velocity, new_position)

    @staticmethod
    def update_all(timedelta):
        for enemy in Enemy.instances:
            enemy.update(timedelta)

    def draw(self, game):
        game.draw_rect_element(self.position, self.size, color=self.color)

        if DRAW_HELPERS:
            circle_radius = min(self.size) * 0.1
            circle_offsets = {
                "FLOOR": [0, -0.5*self.size[1]],
                "CEILING": [0, 0.5*self.size[1]],
                "LEFT_WALL": [-0.5*self.size[0], 0],
                "RIGHT_WALL": [0.5*self.size[0], 0],
            }

            game.draw_circle_element(self.position, circle_radius, color=(0, 0, 255))
            for side in circle_offsets:
                if self.collisions[side] is not None:
                    position = [self.position[dim] + circle_offsets[side][dim] for dim in (0, 1)]
                    game.draw_circle_element(position, circle_radius, color=(0, 0, 255))

    @staticmethod
    def draw_all(game):
        for enemy in Enemy.instances:
            enemy.draw(game)

    def detect_collision(self, player):
        dx_min = player.size[0]/2 + self.size[0]/2
        dy_min = player.size[1]/2 + self.size[1]/2

        dx = player.position[0] - self.position[0]  # dx > 0 = player is right from the enemy
        dy = player.position[1] - self.position[1]  # dy > 0 = player is above the enemy

        horizontal_overlap = (dx_min - abs(dx))
        vertical_overlap = (dy_min - abs(dy))

        if vertical_overlap > 0 and horizontal_overlap > 0:
            if vertical_overlap < horizontal_overlap and dy > 0:
                return {"ENEMY_KILLED": self}
            else:
                return {"PLAYER_KILLED": self}

        return {}

    @staticmethod
    def detect_all_collisions(player):
        all_collisions = {
            'ENEMY_KILLED': [],
            'PLAYER_KILLED': [],
        }
        for enemy in Enemy.instances:
            single_collision = enemy.detect_collision(player)
            for collision_type in single_collision:
                all_collisions[collision_type].append(single_collision[collision_type])

        return all_collisions

    def kill(self):
        Enemy.instances.remove(self)
