import math
#This is what will appear in all interfaces
name = "Alternate"

#This is what the user will see after the effect starts
start_string = name + " started!"

#This is what will appear in tips and help menus
description = "Two alternating colors"

#This defines the format of update's 'state' parameter
#If a 'speed' key is defined it must be an int and will automatically be used by the daemon.
schema = {
    'speed': {
        'value': {
            'type': 'int',
            'min': 1,
            'max': 100,
            'default': 1 
        },
        'user_input': True,
        'required': False
    },
    'color 1': {
        'value': {
            'type': 'color',
            'default': '0xFF0000'
        },
        'user_input': True,
        'required': False
    },
    'color 2': {
        'value': {
            'type': 'color',
            'default': '0x0000FF'
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
    for i in lights.all_lights():
        if (i+step) % 2 == 0:
            lights.set_pixel(i, *state['color 1'])
        else:
            lights.set_pixel(i, *state['color 2'])
