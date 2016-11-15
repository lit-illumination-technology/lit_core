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
    m = lights.num_leds/60
    if section == LEFT:
        for strip in range(0, m):
            for n in range(60*strip, (60*strip + 25)):
                lights.set_pixel(n, *color)
    elif section == RIGHT:
        for strip in range(0, m):
            for n in range(60*strip+35, (60*strip + 60)):
                lights.set_pixel(n, *color)
    elif section == CENTER_L:
        for strip in range(0, m):
            for n in range(60*strip+25, (60*strip + 30)):
                lights.set_pixel(n, *color)
    elif section == CENTER_R:
        for strip in range(0, m):
            for n in range(60*strip+30, (60*strip + 35)):
                lights.set_pixel(n, *color)
