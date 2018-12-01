import random
#This is what will appear in all interfaces
name = "Drip"

#This is what the user will see after the effect starts
start_string = name + " started!"

#This is what will appear in tips and help menus
description = "Mimics water droplets accumulating and falling"


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
    },
    'color': {
        'value': {
            'type': 'color',
            'default': '0x0014AF'
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
    if step == 0:
        state['dullness'] = [15]*lights.num_leds
    color = state['color'];
    dullness = state['dullness']
    for i, n in lights.all_lights_with_count():
        lights.set_pixel(i, int(color[0]/dullness[n]), int(color[1]/dullness[n]), int(color[2]/dullness[n]))
        dullness[n] -= random.random()/20
        if dullness[n]<=1 or random.randint(0, int(dullness[n]*20)) == 0:
            dullness[n] = (random.random()*2)+4
