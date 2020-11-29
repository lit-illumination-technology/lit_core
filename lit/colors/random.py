import colorsys
import random

name = "Random Colors"
description = "Random fully saturated colors"
schema = {}


def get_generator(args):
    def generator(_step, _position):
        return list(
            map(lambda x: int(255 * x), colorsys.hsv_to_rgb(random.random(), 1, 1))
        )

    return generator
