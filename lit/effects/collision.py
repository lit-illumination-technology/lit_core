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

#This is the function that updates the effect.
#Params:
#   lights: A reference to the light controls (the only way to make anything happen).
#   step: The number of times that this effect has been updated
#   state: Dict with information about the state of the effect
def update(lights, step, state):
    if step == 0:
        # Setup
        state['projectiles'] = [[0, 1, random.random()], [lights.num_leds-1, -1, random.random()]]
    trail_length = 15

    projectiles = state['projectiles']

    if random.random() < .01:
        projectiles.append([0, 1, random.random()])
        projectiles.append([lights.num_leds-1, -1, random.random()])
    lights.set_all_pixels(0, 0, 0)
    for i, v in enumerate(projectiles):
        projectiles[i][0] = projectiles[i][0]+projectiles[i][1]
        for t in range(0, trail_length):
            if v[0]-v[1]*t >=0 and v[0] - v[1]*t < lights.num_leds:
                lights.set_active_pixel_hsv(v[0] - v[1]*t, v[2], 1, (trail_length - 1.0*t)/trail_length)
    for i1, p1 in enumerate(projectiles):
        for i2, p2 in enumerate(projectiles):
            if (p1 is not p2):
                prev1 = p1[0] - p1[1]
                prev2 = p2[0] - p2[1]
                if (prev1 - prev2 < 0) != (p1[0] - p2[0] < 0):
                    #explode(lights, p1[0], p1[2], p2[2]) TODO
                    projectiles.remove(p1)
                    projectiles.remove(p2)


def explode(lights, n, color1, color2):
    radius = lights.num_leds // 20
    for d in range(0, radius):
        for pixel in range(n - d, n + d):
            if pixel >= 0 and pixel < lights.num_leds:
                lights.set_active_pixel_hsv(pixel, random.choice([color1, color2]) , 1, (1.0 * radius - d) / radius)
        lights.show()
