name = "Police"

start_message = "Cops are here!"

description = "Mimics lights on top of police cars."

default_speed = 25

schema = {}

# CONSTANTS
LEFT = 0
CENTER_L = 2
CENTER_R = 3
RIGHT = 1


def update(lights, step, state):
    lights.clear()
    if step % 3 != 0:
        if (step // 10) % 2 == 0:
            set_section(lights, LEFT, (255, 0, 0))
            set_section(lights, CENTER_R, (255, 255, 255))
        else:
            set_section(lights, RIGHT, (0, 0, 255))
            set_section(lights, CENTER_L, (255, 255, 255))


def set_section(lights, section, color):
    if section == LEFT:
        for n in range(0, int(lights.size * (5 / 12))):
            lights.set_pixel(n, *color)
    elif section == RIGHT:
        for n in range(int(lights.size * (7 / 12)), lights.size):
            lights.set_pixel(n, *color)
    elif section == CENTER_L:
        for n in range(int(lights.size * (5 / 12)), int(lights.size * (1 / 2))):
            lights.set_pixel(n, *color)
    elif section == CENTER_R:
        for n in range(int(lights.size * (1 / 2)), int(lights.size * (7 / 12))):
            lights.set_pixel(n, *color)
