import random
name = "Rave"

start_string = name + " started!"

description = "Each light flashes a random color"

schema = {
    'speed': {
        'value': {
            'type': 'number',
            'min': 0,
            'max': 100,
            'default': 50
        },
        'user_input': True,
        'required': False
    }
}

def update(lights, step, state):
    for i in range(lights.num_leds):
        lights.set_pixel(i, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
