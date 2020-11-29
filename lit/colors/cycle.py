import colorsys
import random

name = "Cycle"
description = "Cycle through the spectrum of colors"
schema = {}


def get_generator(args):
    def generator(step, _position):
        return tuple(
            map(lambda x: int(255 * x), colorsys.hsv_to_rgb((step % 255) / 255, 1, 1))
        )

    return generator
