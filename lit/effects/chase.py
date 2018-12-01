#This is what will appear in all interfaces
name = "Chase"

#This is what the user will see after the effect starts
start_string = name + " started!"

#This is what will appear in tips and help menus
description = "The string is sequentially covered by different colors"

#This defines the format of update's 'state' parameter
#If a 'speed' key is defined it must be an int and will automatically be used by the daemon.
schema = {
    'speed': {
        'value': {
            'type': 'int',
            'min': 1,
            'max': 100,
            'default': 50
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
    hue = (.2*(step//lights.num_leds))%1
    lights.set_pixel_hsv(step%lights.num_leds, hue, 1, 1)
