import random
import colorsys
#DO NOT CHANGE THESE#
SPEED = 0b10        #
COLOR = 0b1         #
NONE = 0b0          #
#####################

#This is what will appear in all interfaces
name = "Nexus"

#This is what the user will see after the effect starts
start_string = name + " started!"

#This is what will appear in tips and help menus
description = "Like the Nexus android wallpaper"

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
    projectiles = []
    while not stop_event.is_set():
        if random.random() < .05:
            right = random.random() < .5 
            projectiles.append([0 if right else (lights.num_leds-1),
                (1 if right else -1) * (max(.3, random.normalvariate(2, 1))),
                random.random()])

        lights.set_all_pixels(0, 0, 0)
        rgbs = [[0, 0, 0] for _ in range(0, lights.num_leds)]
        count = [0] * lights.num_leds
        for i, v in enumerate(projectiles):
            tail_length = int(15 * abs(v[1]))
            for t in range(0, tail_length):
                tail_pixel = int(v[0] + t * (1 if v[1] < 0 else -1))
                if tail_pixel >=0 and tail_pixel < lights.num_leds:
                    r, g, b = [int(n*255) for n in colorsys.hsv_to_rgb(v[2], 1, (tail_length - 1.0 * t) / tail_length)]
                    rgbs[tail_pixel][0] = ((rgbs[tail_pixel][0] * count[tail_pixel]) + r) / (count[tail_pixel] + 1)
                    rgbs[tail_pixel][1] = ((rgbs[tail_pixel][1] * count[tail_pixel]) + g) / (count[tail_pixel] + 1)
                    rgbs[tail_pixel][2] = ((rgbs[tail_pixel][2] * count[tail_pixel]) + b) / (count[tail_pixel] + 1)
                    count[tail_pixel] = count[tail_pixel] + 1;
            projectiles[i][0] = projectiles[i][0] + projectiles[i][1]
            if v[0] + tail_length < 0 or v[0] - tail_length >= lights.num_leds:
                projectiles.remove(v)
        lights.set_pixels(rgbs)
        lights.show()
        stop_event.wait(.02/speed)
