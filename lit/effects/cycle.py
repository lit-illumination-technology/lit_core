name = "Cycle"

start_message = name + " started!"

description = "Cycles through the color spectrum."

schema = {}


def update(lights, step, state):
    lights.set_all_pixels_hsv((step / 500) % 1, 1, 1)
