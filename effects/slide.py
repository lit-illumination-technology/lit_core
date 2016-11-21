#DO NOT CHANGE THESE#
SPEED = 0b10        #
COLOR = 0b1         #
NONE = 0b0          #
#####################

#This is what will appear in all interfaces
name = "Slide"

#This is what the user will see after the effect starts
start_string = name + " started!"

#This is what will appear in tips and help menus
description = "The full color spectrum shifts along the strand."

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
    offset = 0
    while not stop_event.is_set():
        for i, n in lights.all_lights_with_count():
            lights.set_pixel_hsv(i, (1.0*(n+offset)/lights.num_leds)%1, 1, 1)
        offset += .2
        lights.show()
        stop_event.wait(.02/speed)
