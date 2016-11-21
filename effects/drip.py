import random
#DO NOT CHANGE THESE#
SPEED = 0b10        #
COLOR = 0b1         #
NONE = 0b0          #
#####################

#This is what will appear in all interfaces
name = "Drip"

#This is what the user will see after the effect starts
start_string = name + " started!"

#This is what will appear in tips and help menus
description = "Mimics water droplets accumulating and falling"

#This defines which additional arguments this effect can take.
#Combine multiple options with a '|'
modifiers = COLOR | SPEED

#This is the function that controls the effect. Look at the included effects for examples.
#Params:
#   lights: A reference to the light controls (the only way to make anything happen).
#   stop_event: A threading event that allows this effect to be stopped by the parent.
#   color: The color if passed, otherwise the default color. REMOVE IF COLOR IS NOT A MODIFIER.
#   speed: The speed multiplier if passed, otherwise the default speed. REMOVE IF SPEED IS NOT A MODIFIER.
#   **extras: Any other parameters that may have been passed. Do not use, but do not remove.
def start(lights, stop_event, color = [0, 20, 175], speed = 1, **extras):
    dullness = [15]*lights.num_leds
    while not stop_event.is_set():
        for i, n in lights.all_lights_with_count():
            lights.set_pixel(i, int(color[0]/dullness[n]), int(color[1]/dullness[n]), int(color[2]/dullness[n]))
            dullness[n] -= random.random()/20
            if dullness[n]<=1 or random.randint(0, int(dullness[n]*20)) == 0:
                dullness[n] = (random.random()*2)+4
        lights.show()
        stop_event.wait(.05/speed)

