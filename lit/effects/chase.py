name = "Chase"

start_string = name + " started!"

description = "The string is sequentially covered by different colors"

schema = {
    "speed": {
        "value": {"type": "number", "min": 0, "max": 100, "default": 50},
        "user_input": True,
        "required": False,
    }
}


def update(lights, step, state):
    hue = (0.2 * (step // lights.size)) % 1
    lights.set_pixel_hsv(step % lights.size, hue, 1, 1)
