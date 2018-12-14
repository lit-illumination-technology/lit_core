import colorsys
import numpy as np
import random
import math
from music_visualization_framework import music_analyzer
import random
import logging
import colorsys
#DO NOT CHANGE THESE#
SPEED = 0b10        #
COLOR = 0b1         #
NONE = 0b0          #
#####################
logger = logging.getLogger(__name__)

#This is what will appear in all interfaces
name = "Music Expand"

#This is what the user will see after the effect starts
start_string = name + " started!"

#This is what will appear in tips and help menus
description = "Changes color with music"

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
    lights.clear()
    app = music_analyzer.Analyzer("/dev/ttyACM0")
    @app.decorators.on_level_change()
    def update():
        lights.clear()
        center = lights.num_leds / 2
        hues = [(1, 0)]*lights.num_leds
        bands = [app.bands[0], (app.bands[1] + app.bands[2] + app.bands[3])/3, (app.bands[4] + app.bands[5] + app.bands[6])/3]
        for i, band in enumerate(bands):
            color_h = i/len(bands)
            val = (1/(1+math.exp(-(10*(band/1023)-7))))*(lights.num_leds/2)
            for n in range(int(center-val), int(center+val)):
                h, s = hues[n]
                hues[n] = (h*color_h, s+1)
        for n, (h, s) in enumerate(hues):
            if s is not 0:
                lights.set_pixel_hsv(n, h, 1, 1)
        lights.show()
    app.start(stop_event)
