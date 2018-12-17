import random
name = "Flash"

start_string = name + " started!"

description = "All lights change to a random color repeatedly"

schema = {
    'speed': {
        'value': {
            'type': 'number',
            'min': 0,
            'max': 10,
            'default': 3
        },
        'user_input': True,
        'required': False
    }
}

def update(lights, step, state):
    color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
    lights.set_all_pixels(color[0], color[1], color[2])
