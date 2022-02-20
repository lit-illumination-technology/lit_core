import colorsys
import random

name = "Slide"
description = "Sliding spectrum of colors"
schema = {
        "frequency": {
            "value": {
                "type": "number",
                "min": 0,
                "max": 5,
                "default": 1
                },
            "user_input": True,
            "required": False
            }
        }


def get_generator(args):
    def generator(step, position):
        return tuple(
            map(lambda x: int(255 * x), colorsys.hsv_to_rgb(((step + (position*255*args["frequency"])) % 255) / 255, 1, 1))
        )

    return generator
