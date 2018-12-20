name = "Police"

start_string = "Cops are here!"

description = "Mimics lights on top of police cars."

schema = {
    'speed': {
        'value': {
            'type': 'number',
            'min': 0,
            'max': 100,
            'default': 25
        },
        'user_input': True,
        'required': False
    }
}

#CONSTANTS
LEFT=0
CENTER_L=2
CENTER_R=3
RIGHT=1

def update(lights, step, state):
    lights.clear()
    if step % 3 != 0:
        if (step//10) % 2 == 0:
            set_section(lights, LEFT, (255, 0, 0))
            set_section(lights, CENTER_R, (255, 255, 255))
        else:
            set_section(lights, RIGHT, (0, 0, 255))
            set_section(lights, CENTER_L, (255, 255, 255))

def set_section(lights, section, color):
    if section == LEFT:
        for n in range(0, int(lights.num_leds * (5/12))):
            lights.set_pixel(n, *color)
    elif section == RIGHT:
        for n in range(int(lights.num_leds*(7/12)), lights.num_leds):
            lights.set_pixel(n, *color)
    elif section == CENTER_L:
        for n in range(int(lights.num_leds*(5/12)), int(lights.num_leds*(1/2))):
            lights.set_pixel(n, *color)
    elif section == CENTER_R:
        for n in range(int(lights.num_leds*(1/2)), int(lights.num_leds*(7/12))):
            lights.set_pixel(n, *color)
