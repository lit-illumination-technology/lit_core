#DO NOT CHANGE THESE#
SPEED = 0b10        #
COLOR = 0b1         #
NONE = 0b0          #
#####################

#This is what will appear in all interfaces
name = "Police"

#This is what the user will see after the effect starts
start_string = "Cops are here!"

#This is what will appear in tips and help menus
description = "Mimics lights on top of police cars."

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
LEFT=0
CENTER_L=2
CENTER_R=3
RIGHT=1
def start(lights, stop_event, color = [255, 255, 255], speed = 1, **extras):
    state = 0
    while not stop_event.is_set():
        lights.off()
        if state < 1000:
            if state % 3 != 0:
                if (state/10) % 2 == 0:
                    set_section(lights, LEFT, (255, 0, 0))
                    set_section(lights, CENTER_R, (255, 255, 255))
                else:
                    set_section(lights, RIGHT, (0, 0, 255))
                    set_section(lights, CENTER_L, (255, 255, 255))
        lights.show()
        state = (state + 1)%1000
        stop_event.wait(.02/speed)

def set_section(lights, section, color):
    if section == LEFT:
        for r in lights.get_ranges():
            for n in range(r[0], r[0] + int(len(r) * (5.0/12))):
                lights.set_pixel(n, *color)
    elif section == RIGHT:
        for r in lights.get_ranges():
            for n in range(r[0] + int(len(r)*(7.0/12)), r[0] + len(r)):
                lights.set_pixel(n, *color)
    elif section == CENTER_L:
        for r in lights.get_ranges():
            for n in range(r[0] + int(len(r)*(5.0/12)), r[0] + int(len(r)*(1.0/2))):
                lights.set_pixel(n, *color)
    elif section == CENTER_R:
        for r in lights.get_ranges():
            for n in range(r[0] + int(len(r)*(1.0/2)), r[0] + int(len(r)*(7.0/12))):
                lights.set_pixel(n, *color)
