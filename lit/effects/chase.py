import colorsys
import random

name = "Chase"

start_message = name + " started!"

description = (
    "The string is sequentially covered by random colors"
)


def create_heads(lights, args):
    num_heads = int(args["number"])
    print(args['color'])
    colors = [args['color'].get_color(i) for i in range(0, num_heads)]
    head_locations = [i * (-lights.size // num_heads) for i in range(0, num_heads)]
    return [head_locations, colors]


schema = {
    "number": {
        "value": {
            "type": "number",  # TODO integer type (or step)
            "min": 1,
            "max": 20,
            "default": 3,
        },
        "user_input": True,
        "required": False,
        "index": 0,
    },
    "color": {
        "value": {
            "type": "color",
            "default": {"type": "Random Colors"},
        },
        "user_input": True,
        "required": False,
        "index": 0
    },
    "heads": {
        "value": {"type": "tuple list", "default_gen": create_heads},
        "user_input": False,
        "index": 1
    },
}


def update(lights, step, state):
    heads = state["heads"]
    for i in range(len(heads[0])):
        if heads[0][i] >= 0:
            lights.set_pixel(heads[0][i], *heads[1][i])
        heads[0][i] += 1
        if heads[0][i] >= lights.size:
            heads[0][i] = 0
            heads[1][i] = state["color"].get_color(step)
