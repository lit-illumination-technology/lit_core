#DO NOT CHANGE THESE#
SPEED = 0b10        #
COLOR = 0b1         #
NONE = 0b0          #
#####################

#This is what will appear in all interfaces
name = "Fade"

#This is what the user will see after the effect starts
start_string = "Fading!"

#This is what will appear in tips and help menus
description = "Lights fade from their current color to a new color"

#This defines which additional arguments this effect can take.
#Combine multiple options with a '|'
modifiers = COLOR | SPEED

#This is the function that controls the effect. Look at the included effects for examples.
#Params: #   lights: A reference to the light controls (the only way to make anything happen).
#   stop_event: A threading event that allows this effect to be stopped by the parent.
#   color: The color if passed, otherwise the default color. REMOVE IF COLOR IS NOT A MODIFIER.
#   speed: The speed multiplier if passed, otherwise the default speed. REMOVE IF SPEED IS NOT A MODIFIER.
#   **extras: Any other parameters that may have been passed. Do not use, but do not remove.
def start(lights, stop_event, color = [0, 0, 0], speed = 1, **extras):
    h = 0
    pixels = [(float(r), float(g), float(b)) for (r, g, b) in lights.get_pixels()]
    n = int(100/speed)
    ds = [((color[0]-r)/n, (color[1]-g)/n, (color[2]-b)/n) for (r, g, b) in pixels]
    for i in range(0, n):
        pixels = [(pixels[n][0]+ds[n][0], pixels[n][1]+ds[n][1], pixels[n][2]+ds[n][2]) for n in range(0, len(pixels))]
        pixelsi = [(max(0,int(r)), max(0,int(g)), max(0,int(b))) for (r, g, b) in pixels]
        lights.set_pixels(pixelsi)
        lights.show()
        stop_event.wait(.02)
    lights.set_all_pixels(color[0], color[1], color[2])
    lights.show()
