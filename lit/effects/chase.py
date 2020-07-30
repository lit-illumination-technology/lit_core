name = "Chase"

start_message = name + " started!"

description = "The string is sequentially covered by different colors"

schema = {}


def update(lights, step, state):
    hue = (0.2 * (step // lights.size)) % 1
    lights.set_pixel_hsv(step % lights.size, hue, 1, 1)
