name = "Disco"

start_message = name + " started!"

description = "Color spectrum is repeatedly 'squished' to one side."

schema = {}


def update(lights, step, state):
    off = step / 10
    for i in range(lights.size):
        lights.set_pixel_hsv(i, ((i * off) / float(lights.size)) % 1, 1, 1)
