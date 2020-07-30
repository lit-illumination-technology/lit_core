import random

name = "Rave"

start_message = name + " started!"

description = "Each light flashes a random color"

schema = {}


def update(lights, step, state):
    for i in range(lights.size):
        lights.set_pixel(
            i, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        )
