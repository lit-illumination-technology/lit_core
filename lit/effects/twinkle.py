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
            'default': (255, 240, 0)
        },
        'user_input': True,
        'required': False
    },
    'density': {
        'value': {
            'type': 'number',
            'min': 1,
            'max': 100,
            'default': 50
        },
        'user_input': True,
        'required': False
    },
    'start_durations': {
        'value': {
            'type': '(int, int) list',
            'default_gen': setup_start_durations
        },
        'user_input': False
    }
}

# Average time a led is on
AVG_ON_TIME = 100

def update(lights, step, state):
    color = state['color'];
    start_durations = state['start_durations']
    """ MATH:
    DENSITY = OnTime/(Ontime+OffTime)
    OnTime(1-DENSITY) = Density*OffTime
    Offtime = ((1-Density)*OnTime)/Density 
    """
    density = state['density']/100
    avg_off_time = (((1-density)*AVG_ON_TIME)/density)
    for i in range(lights.num_leds):
        sd = start_durations[i]
        if sd[0] + sd[1] <= step:
            state['start_durations'][i] = (step+random.randint(0, int(2*avg_off_time)), random.randint(1, AVG_ON_TIME*2)) 
        brightness = (step-sd[0])/(sd[1]/2)
        if brightness > 1:
            brightness = 2 - brightness
        brightness = max(brightness, 0)
        lights.set_pixel(i, int(color[0]*brightness), int(color[1]*brightness), int(color[2]*brightness))
