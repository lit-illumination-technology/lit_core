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
name = "Music Flash"

#This is what the user will see after the effect starts
start_string = name + " started!"

#This is what will appear in tips and help menus
description = "Changes color and brightness with music"

#This defines which additional arguments this effect can take.
#Combine multiple options with a '|'
modifiers = NONE
 
color = (255, 255, 255)

#This is the function that controls the effect. Look at the included effects for examples.
#Params:
#   lights: A reference to the light controls (the only way to make anything happen).
#   stop_event: A threading event that allows this effect to be stopped by the parent.
#   color: The color if passed, otherwise the default color. REMOVE IF COLOR IS NOT A MODIFIER.
#   speed: The speed multiplier if passed, otherwise the default speed. REMOVE IF SPEED IS NOT A MODIFIER.
#   **extras: Any other parameters that may have been passed. Do not use, but do not remove.
def start(lights, stop_event, speed = 1, **extras):
    lights.set_all_other_pixels(0, 0, 0)
    app = music_analyzer.Analyzer("/dev/ttyACM0", threshold_acceleration=0.05, smoothing=.7)
    MIN_BRIGHTNESS = 0.3
    @app.decorators.on_level_change()
    def update():
        global color
        if app.total_volume_beat:
            color = tuple([int(255*x) for x in colorsys.hsv_to_rgb(random.random(), 1, 1)])
            #color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            vol = 1
        elif color is None:
            color = (255, 255, 255)
        else:
            #vol = math.sqrt((app.total_volume / (1023 *  app.num_bands)))
            #vol = (app.total_volume / (1023 *  app.num_bands))
            vol = (app.bands[0] / 1023)
            #vol = (1 - MIN_BRIGHTNESS) * np.tanh((app.total_volume / (1023 *  app.num_bands))) + MIN_BRIGHTNESS

        display_color = tuple([int(vol*x) for x in color])
        lights.set_all_pixels(*display_color)
        lights.show()
    app.start(stop_event)
