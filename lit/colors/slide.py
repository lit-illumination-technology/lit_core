import colorsys
import random

name = "Slide"
description = "Sliding spectrum of colors"
schema = {}


def get_generator(args):
    def generator(step, position):
        return tuple(
            map(lambda x: int(255 * x), colorsys.hsv_to_rgb(((step + (position*100)) % 255) / 255, 1, 1))
        )

    return generator
