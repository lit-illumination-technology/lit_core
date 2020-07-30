import random
import logging

logger = logging.getLogger(__name__)

name = "Twinkle"

start_message = name + " started!"

description = "Like a little star"


def setup_start_durations(lights, args):
    return [(-1, 1)] * lights.size


schema = {
    "color": {
        "value": {"type": "color", "default": (255, 255, 255)},
        "user_input": True,
        "required": False,
    },
    "twinkleyness": {
        "value": {"type": "number", "min": 1, "max": 200, "default": 50},
        "user_input": True,
        "required": False,
    },
    "brightnesses": {
        "value": {"type": "int list", "default_gen": lambda l, a: [0.5] * l.size},
        "user_input": False,
    },
}


def update(lights, step, state):
    color = state["color"]
    brightnesses = state["brightnesses"]
    for i in range(lights.size):
        brightness = brightnesses[i]
        lights.set_pixel(
            i,
            int(color[0] * brightness),
            int(color[1] * brightness),
            int(color[2] * brightness),
        )
        rand = random.random()
        if rand > brightness:
            brightnesses[i] += state["twinkleyness"] / 200
        elif rand > 1 - brightness:
            brightnesses[i] -= state["twinkleyness"] / 200
        brightnesses[i] = max(min(brightnesses[i], 1), 0)
