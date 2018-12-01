import math
#This is what will appear in all interfaces
name = "Christmas"

#This is what the user will see after the effect starts
start_string = name + " started!"

#This is what will appear in tips and help menus
description = "Red and green pattern slides along the strand"

#This defines the format of update's 'state' parameter
#If a 'speed' key is defined it must be an int and will automatically be used by the daemon.
schema = {
    'speed': {
        'value': {
            'type': 'int',
            'min': 1,
            'max': 1000,
            'default': 500
        },
        'user_input': True,
        'required': False
    }
}

#This is the function that updates the effect.
#Params:
#   lights: A reference to the light controls (the only way to make anything happen).
#   step: The number of times that this effect has been updated
#   state: Dict with information about the state of the effect
def update(lights, step, state):
    colors = [None]*lights.num_leds
    for n in range(0, lights.num_leds):
        x = math.fabs((lights.num_leds/2 - n)/float(lights.num_leds/2))
        lights.set_pixel((n+step)%lights.num_leds, int(255-(x*255)), int(x*255), 0)
