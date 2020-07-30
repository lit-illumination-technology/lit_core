import random

name = "Drip"

start_message = name + " started!"

description = "Mimics water droplets accumulating and falling"


def setup_dullness(lights, args):
    return [0] * lights.size


schema = {
    "color": {
        "value": {"type": "color", "default": (0, 20, 175)},
        "user_input": True,
        "required": False,
    },
    "intensity": {
        "value": {"type": "number", "min": 1, "max": 100, "default": 50},
        "user_input": True,
        "required": False,
    },
    "dullness": {
        "value": {"type": "number list", "default_gen": setup_dullness},
        "user_input": False,
    },
}


def update(lights, step, state):
    color = state["color"]
    dullness = state["dullness"]
    intensity = state["intensity"]
    for i in range(lights.size):
        if dullness[i] <= 1 or random.randint(0, int(dullness[i] ** 2)) == 0:
            dullness[i] = (1000 / intensity) * (random.random() + 1)
        lights.set_pixel(
            i,
            int(color[0] / dullness[i]),
            int(color[1] / dullness[i]),
            int(color[2] / dullness[i]),
        )
        dullness[i] -= (random.random() * intensity) / 100
