import random
#DO NOT CHANGE THESE#
SPEED = 0b10        #
COLOR = 0b1         #
NONE = 0b0          #
#####################

#This is what will appear in all interfaces
name = "Multi-Chase"

#This is what the user will see after the effect starts
start_string = name + " started!"

#This is what will appear in tips and help menus
description = "The string is sequentially covered by random colors with multiple at the same time"

#This defines which additional arguments this effect can take.
#Combine multiple options with a '|'
modifiers = SPEED

#This is the function that controls the effect. Look at the included effects for examples.
#Params:
#   lights: A reference to the light controls (the only way to make anything happen).
#   stop_event: A threading event that allows this effect to be stopped by the parent.
#   color: The color if passed, otherwise the default color. REMOVE IF COLOR IS NOT A MODIFIER.
#   speed: The speed multiplier if passed, otherwise the default speed. REMOVE IF SPEED IS NOT A MODIFIER.
#   **extras: Any other parameters that may have been passed. Do not use, but do not remove.
def start(lights, stop_event, speed = 1, **extras):
    lights.set_all_other_pixels(0, 0, 0)
    colors = [random.random() for _ in range(0, 3)]
    heads = [i*-150 for i in range(0, 3)];
    while not stop_event.is_set():
        for i, v in enumerate(heads):
            if v >= 0:
                lights.set_pixel_hsv(v, colors[i], 1, 1)
            heads[i] = v+1
            if heads[i] >= lights.num_leds:
                heads[i] = 0
                colors[i] = random.random()
        lights.show()
        stop_event.wait(.02/speed)
