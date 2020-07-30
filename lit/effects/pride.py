name = "Pride"

start_message = name + " started!"

description = "Displays rainbow pride flag colors"

COLORS = [
    (231, 0, 0),
    (255, 85, 0),
    (255, 239, 0),
    (0, 129, 0),
    (0, 68, 255),
    (74, 0, 118),
]

default_speed = 1

schema = {}


def update(lights, step, state):
    stripe_width = lights.size / len(COLORS)
    start = 0
    end = stripe_width
    for ci in range(len(COLORS)):
        for i in range(int(start), int(end)):
            lights.set_pixel(i, *COLORS[(ci + step) % len(COLORS)])
        start += stripe_width
        end += stripe_width
