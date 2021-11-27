import colorsys
import random

name = "Palette"
description = "Pre-selected color palettes"
palettes = {"Patriotic": [(255, 0, 0), (255, 255, 255), (0, 0, 255)],
        "Gay": [
                (231, 0, 0),
                (255, 85, 0),
                (255, 239, 0),
                (0, 129, 0),
                (0, 68, 255),
                (74, 0, 118)
                ]
        }
schema = {"palette": {"value": {"type": "choices", "choices": list(palettes)}, "user_input": True, "required": True}}

def get_generator(args):
    palette = palettes[args['palette']]
    i = 0
    def generator(_step, _position):
        nonlocal i
        i += 1
        return palette[i%len(palette)]
    return generator
