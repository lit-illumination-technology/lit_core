name = "Slide"

start_message = name + " started!"

description = "The full color spectrum shifts along the strand."

schema = {}


def update(lights, step, state):
    for i in range(lights.size):
        lights.set_pixel_hsv(i, (1.0 * (i + step) / (lights.size / 2)) % 1, 1, 1)
