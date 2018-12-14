name = "Christmas Lights"

start_string = name + " started!"

description = "Colors of traditional colored christmas lights"

schema = {}

BRIGHTNESS = .2
def update(lights, step, state):
    for i in range(lights.num_leds):
        seq = i%5
        if seq == 0:
            lights.set_pixel(i, int(170*BRIGHTNESS), 0, 0)
        elif seq == 1:
            lights.set_pixel(i, int(170*BRIGHTNESS), 0, int(85*BRIGHTNESS))
        elif seq == 2:
            lights.set_pixel(i, 0, int(170*BRIGHTNESS), 0)
        elif seq == 3:
            lights.set_pixel(i, int(255*BRIGHTNESS), int(170*BRIGHTNESS), 0)
        elif seq == 4:
            lights.set_pixel(i, 0, 0, int(170*BRIGHTNESS))
