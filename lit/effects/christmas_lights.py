name = "Christmas Lights"

start_message = name + " started!"

description = "Colors of traditional colored christmas lights"

schema = {}

BRIGHTNESS = 0.2


def update(lights, step, state):
    for i in range(lights.size):
        seq = i % 10
        if seq == 0:
            lights.set_pixel(i, int(170 * BRIGHTNESS), 0, 0)
        elif seq == 2:
            lights.set_pixel(i, int(170 * BRIGHTNESS), 0, int(85 * BRIGHTNESS))
        elif seq == 4:
            lights.set_pixel(i, 0, int(170 * BRIGHTNESS), 0)
        elif seq == 6:
            lights.set_pixel(i, int(255 * BRIGHTNESS), int(170 * BRIGHTNESS), 0)
        elif seq == 8:
            lights.set_pixel(i, 0, 0, int(170 * BRIGHTNESS))
        else:
            lights.set_pixel(i, 0, 0, 0)
