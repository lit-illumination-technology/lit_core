import random
import logging
logger = logging.getLogger(__name__)

name = "Twinkle"

start_string = name + " started!"

description = "Like a little star"

def setup_start_durations(lights, args):
    return [(-1, 1)]*lights.num_leds

schema = {
    'speed': {
        'value': {
            'type': 'number',
            'min': 1,
            'max': 100,
            'default': 50
        },
        'user_input': True,
        'required': False
    },
    'color': {
        'value': {
            'type': 'color',
            'default': (255, 255, 255)
        },
        'user_input': True,
        'required': False
    },
    'twinkleyness': {
        'value': {
            'type': 'number',
            'min': 1,
            'max': 200,
            'default': 50
        },
        'user_input': True,
        'required': False
    }
}

def update(lights, step, state):
    color = state['color'];
    off_prob = state['twinkleyness']/10000
    for i in range(lights.num_leds):
        if random.random() <= off_prob:
            lights.set_pixel(i, 0, 0, 0)
        else:
            lights.set_pixel(i, *color)
