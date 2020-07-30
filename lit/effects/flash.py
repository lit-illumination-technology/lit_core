import random

name = "Flash"

start_message = name + " started!"

description = "All lights change to a random color repeatedly"

default_speed = 3


def update(lights, step, state):
    color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
    lights.set_all_pixels(color[0], color[1], color[2])
