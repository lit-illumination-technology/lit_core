import math
name = "Christmas"

start_string = name + " started!"

description = "Red and green pattern slides along the strand"

def setup_pixels(lights, args):
    colors = [None]*lights.num_leds
    for n in range(0, lights.num_leds):
        x = math.fabs((lights.num_leds/2 - n)/(lights.num_leds/2))
        colors[n] = (int(255-(x*255)), int(x*255), 0)
    return colors

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
    },
    'colors': {
        'value': {
            'type': 'array',
            'default_gen': setup_pixels
        },
        'user_input': False
    }
}

def update(lights, step, state):
    state['colors'] = state['colors'][1:] + [state['colors'][0]]
    lights.set_pixels(state['colors'])
