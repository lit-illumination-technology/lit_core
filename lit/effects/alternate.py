name = "Alternate"

start_message = name + " started!"

description = "Two alternating colors"

default_speed = 1

schema = {
    "color": {
        "value": {
            "type": "color",
            "default_selector": "palette",
            "default": (255, 0, 0),
        },
        "user_input": True,
        "required": False,
    },
}


def update(lights, step, state):
    colors = state["color"].get_palette(2)
    for i in range(lights.size):
        if (i + step) % 2 == 0:
            lights.set_pixel(i, *colors[1])
        else:
            lights.set_pixel(i, *colors[2])
