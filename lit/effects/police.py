#This is what will appear in all interfaces
name = "Police"

#This is what the user will see after the effect starts
start_string = "Cops are here!"

#This is what will appear in tips and help menus
description = "Mimics lights on top of police cars."

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
        for n in range(int(lights.num_leds*(7/12)), len(r)):
            lights.set_pixel(n, *color)
    elif section == CENTER_L:
        for n in range(int(lights.num_leds*(5/12)), int(lights.num_leds*(1/2))):
            lights.set_pixel(n, *color)
    elif section == CENTER_R:
        for n in range(int(lights.num_leds*(1/2)), int(lights.num_leds*(7/12))):
            lights.set_pixel(n, *color)
