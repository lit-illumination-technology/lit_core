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
name = "Music Dots"

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
        inverse_total_brightness = 1-(1/(1+math.exp(-(10*(app.total_volume/(1023*app.num_bands))-1))))

        for n in range(0, lights.num_leds, len(app.bands)+1):
            lights.set_pixel_hsv(n, 1, 0, inverse_total_brightness)
        for i, band in enumerate(app.bands):
            color_h = float(i)/len(app.bands)
            val = 1/(1+math.exp(-(10*(band/1023)-7)))
            for n in range(i+1, lights.num_leds, len(app.bands)+1):
                lights.set_pixel_hsv(n, color_h, 1, val)
        lights.show()
    app.start(stop_event)
