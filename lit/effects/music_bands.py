import colorsys
import numpy as np
import random
import math
from music_visualization_framework import music_analyzer
import random
import colorsys
#DO NOT CHANGE THESE#
SPEED = 0b10        #
COLOR = 0b1         #
NONE = 0b0          #
#####################

#This is what will appear in all interfaces
name = "Music Bands"

#This is what the user will see after the effect starts
start_string = name + " started!"

#This is what will appear in tips and help menus
description = "Changes color and brightness with music"

#This defines which additional arguments this effect can take.
#Combine multiple options with a '|'
modifiers = NONE

#This is the function that controls the effect. Look at the included effects for examples.
#Params:
#   lights: A reference to the light controls (the only way to make anything happen).
#   stop_event: A threading event that allows this effect to be stopped by the parent.
#   color: The color if passed, otherwise the default color. REMOVE IF COLOR IS NOT A MODIFIER.
#   speed: The speed multiplier if passed, otherwise the default speed. REMOVE IF SPEED IS NOT A MODIFIER.
#   **extras: Any other parameters that may have been passed. Do not use, but do not remove.
def start(lights, stop_event, speed = 1, **extras):
    lights.set_all_other_pixels(0, 0, 0)
    app = music_analyzer.Analyzer("/dev/ttyACM0")
    @app.decorators.on_level_change()
    def update():
        lights_per_band = lights.num_leds / len(app.bands)
        for i, band in enumerate(app.bands):
            color_h = float(i)/len(app.bands)
            for n in range(int(lights_per_band * i), int(lights_per_band * (i + 1))):
                val = 1/(1+math.exp(-(10*(band/1023)-7)))
                lights.set_pixel_hsv(n, color_h, 1, val)
        lights.show()
    app.start(stop_event)
