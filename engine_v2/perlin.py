
import random
import math

from engine.tests import *


"""

This perlin class generate a naturally looking random noise.
Perlin noise reference: https://en.wikipedia.org/wiki/Perlin_noise

I implemented this Perlin noise myself because I sadly did not find a
decent library for simple 1D noise ...


"""
WIDTH = 128
WEIGHTS = {
    1: 1,
    2: 0.5,
    4: 0.25,
    8: 0.125,
    16: 1/16,
    32: 1/32,
    64: 1/64,
    128: 1/128,
}

VALUE_RANGE = (0, 1)

class PerlinNoise1D():

    def __init__(
            self,
            width=None, weights=None, value_range=None,
            decimal_places=6, repeatable=False
    ):

        if width is None:
            width = WIDTH
        else:
            assert isinstance(width, int), "Width has to be an integer"

        if weights is None:
            weights = WEIGHTS
        else:
            TEST_perlin_weights(width, weights)

        if value_range is None:
            value_range = VALUE_RANGE
        else:
            TEST_value_range(value_range)

        self.width = width
        self.weights = weights
        self.value_range = value_range
        self.decimal_places = decimal_places
        self.repeatable = repeatable

        self.noise = self.generate_noise()


    def generate_noise(self):
        random_array = [random.random() for i in range(self.width + 1)]
        noise_array = [0] * (self.width + 1)

        # Add the weighted noise for each layers described in weights
        for sections_count in self.weights:
            weight = self.weights[sections_count]

            sections_width = int(self.width/sections_count)

            # Get noise array for this layer
            sample_array = [
                random_array[sections_width * i]
                for i in range(sections_count + 1)
            ]
            interpolated_array = PerlinNoise1D.interpolated_scaling(
                sample_array, sections_width
            )


            # Get noise layer to overall noise array
            for noise_index in range(self.width + 1):
                noise_array[noise_index] += interpolated_array[noise_index] * weight

        if self.repeatable:
            difference = noise_array[127] - noise_array[0]
            corrector = lambda i: round(
                (i * (difference / 127)), self.decimal_places
            )
            noise_array = [noise_array[i] - corrector(i) for i in range(128)]

        # 1. Normalize array to (0, 1)
        # 2. Scale array to actual size
        # 3. Translate array to actual offset
        max_value = max(noise_array)
        min_value = min(noise_array)
        normalizing_factor = (1/(max_value - min_value)) * (self.value_range[1] - self.value_range[0])
        translation_offset = self.value_range[0]
        noise_array = [
            round(((x - min_value) * normalizing_factor) + translation_offset, self.decimal_places)
            for x in noise_array
        ]

        return noise_array[:128]

    @staticmethod
    def interpolated_scaling(array, scaling_factor):
        factors = [(1-(x/(scaling_factor)), (x/(scaling_factor))) for x in range(scaling_factor)]
        # scaling_factor = 2 -> factors = [(1.0, 0.0), (0.5, 0.5)]
        # scaling_factor = 3 -> factors = [(1.0, 0.0), (0.66, 0.33), (0.33, 0.66)]

        new_array = []
        for i in range(len(array) - 1):
            new_array += [(array[i] * factor[0] + array[i+1] * factor[1]) for factor in factors]
        return new_array + [array[-1]]

    def get(self, x):

        if isinstance(x, int) or isinstance(x, float):

            assert 0 <= x <= self.width - 1, "x must be in range(0, width)"

            if int(x) == x:
                return self.noise[int(x)]
            else:
                # Basic linear interpolation
                left_index = math.floor(x)
                right_index = math.ceil(x)
                left_weight = right_index - x
                right_weight = x - left_index
                return round(
                    self.noise[left_index] * left_weight +
                    self.noise[right_index] * right_weight,
                    self.decimal_places
                )

        elif isinstance(x, slice):

            assert x.start is None or x.step == 0, "Only supports slicing with start=0"
            assert x.step is None or x.step == 1, "Only supports slicing with step=1"

            if x.stop is None:
                stop = self.width
            else:
                assert \
                    isinstance(x.stop, int) and 0 < x.stop < self.width, \
                    "Only supports slicing with 0<stop<width"
                stop = x.stop

            return [self.noise[int(i)] for i in range(0, stop)]

        assert False, "x must be of type integer, float or slice"

    def __getitem__(self, x):
        return self.get(x)

    def generate(self):
        self.noise = self.generate_noise()

    def array(self):
        return self.noise[:128]


if __name__ == '__main__':
    # Dev dependency: I use matplotlib to plot the result as a graph
    import matplotlib.pyplot as plt

    # With repeatable set to True the array has the same start and end value
    noise = PerlinNoise1D(value_range=(0, 1), repeatable=True)

    plt.plot(list(range(0, 128)), noise[:])

    # Test if repeatable setting
    plt.plot(list(range(127, -1, -1)), noise.array())

    # Test if slices work
    plt.plot(list(range(0, 80)), noise[:80])
    plt.show()
