import random
#DO NOT CHANGE THESE#
SPEED = 0b10        #
COLOR = 0b1         #
NONE = 0b0          #
#####################

#This is what will appear in all interfaces
name = "Collision"

#This is what the user will see after the effect starts
start_string = name + " started!"

#This is what will appear in tips and help menus
description = "Two projectiles are sent from opposite ends and collide in the center"

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
    projectiles = [[0, 1, random.random()], [lights.num_leds-1, -1, random.random()]]
    trail_length = 15
    while not stop_event.is_set():
        if random.random() < .01:
            projectiles.append([0, 1, random.random()])
            projectiles.append([lights.num_leds-1, -1, random.random()])
        lights.set_all_pixels(0, 0, 0)
        for i, v in enumerate(projectiles):
            projectiles[i][0] = projectiles[i][0]+projectiles[i][1]
            for t in range(0, trail_length):
                if v[0]-v[1]*t >=0 and v[0] - v[1]*t < lights.num_leds:
                    lights.set_pixel_hsv(v[0] - v[1]*t, v[2], 1, (trail_length - 1.0*t)/trail_length)
        lights.show()
        for i1, p1 in enumerate(projectiles):
            for i2, p2 in enumerate(projectiles):
                if (p1 is not p2):
                    prev1 = p1[0] - p1[1]
                    prev2 = p2[0] - p2[1]
                    print prev1-prev2
                    print p1[0] - p2[0]
                    if (prev1 - prev2 < 0) != (p1[0] - p2[0] < 0):
                        explode(lights, stop_event, speed, p1[0], p1[2], p2[2])
                        projectiles.remove(p1)
                        projectiles.remove(p2)

        stop_event.wait(.02/speed)

def explode(lights, stop_event, speed, n, color1, color2):
    radius = lights.num_leds // 20
    for d in range(0, radius):
        for pixel in range(n - d, n + d):
            if pixel >= 0 and pixel < lights.num_leds:
                lights.set_pixel_hsv(pixel, random.choice([color1, color2]) , 1, (1.0 * radius - d) / radius)
        stop_event.wait(.2/speed)
        lights.show()
