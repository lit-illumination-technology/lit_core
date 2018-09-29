#DO NOT CHANGE THESE#
SPEED = 0b10        #
COLOR = 0b1         #
NONE = 0b0          #
#####################

#This is what will appear in all interfaces
name = "Throb"

#This is what the user will see after the effect starts
start_string = name + " started!"

#This is what will appear in tips and help menus
description = "Shifts through brighness levels repeatedly"

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
def start(lights, stop_event, color = [255, 255, 255], speed = 1, **extras):
    lights.set_all_other_pixels(0, 0, 0)
    brightness = 0
    db = .01
    while(not stop_event.is_set()):
        lights.set_all_pixels(int(color[0]*brightness), int(color[1]*brightness), int(color[2]*brightness))
        lights.show()
        if brightness + db > 1 or brightness + db < 0:
            db = -db
        brightness += db
        stop_event.wait(.01/speed)

