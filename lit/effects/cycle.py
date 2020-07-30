name = "Cycle"

start_string = name + " started!"

description = "Cycles through the color spectrum."

schema = {
    "speed": {
        "value": {"type": "number", "min": 0, "max": 100, "default": 50},
        "user_input": True,
        "required": False,
    }
}


def update(lights, step, state):
    lights.set_all_pixels_hsv((step / 500) % 1, 1, 1)
