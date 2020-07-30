import random

name = "Collision"

start_message = name + " started!"

description = "Two projectiles are sent from opposite ends and collide in the center"


def create_projectiles(lights, args):
    return [[0, 1, random.random()], [lights.size - 1, -1, random.random()]]


schema = {
    "projectiles": {
        "value": {"type": "tuple list", "default_gen": create_projectiles},
        "user_input": False,
    },
}

TRAIL_LENGTH = 15


def update(lights, step, state):
    # NOTE WIP
    projectiles = state["projectiles"]
    if random.random() < 0.01:
        projectiles.append([0, 1, random.random()])
        projectiles.append([lights.size - 1, -1, random.random()])
    for i, v in enumerate(projectiles):
        projectiles[i][0] = projectiles[i][0] + projectiles[i][1]
        for t in range(0, TRAIL_LENGTH):
            if v[0] - v[1] * t >= 0 and v[0] - v[1] * t < lights.size:
                lights.set_pixel_hsv(
                    v[0] - v[1] * t, v[2], 1, (TRAIL_LENGTH - 1.0 * t) / TRAIL_LENGTH
                )
    for i1, p1 in enumerate(projectiles):
        for i2, p2 in enumerate(projectiles):
            if p1 is not p2:
                prev1 = p1[0] - p1[1]
                prev2 = p2[0] - p2[1]
                if (prev1 - prev2 < 0) != (p1[0] - p2[0] < 0):
                    # explode(lights, p1[0], p1[2], p2[2]) TODO
                    projectiles.remove(p1)
                    projectiles.remove(p2)


def explode(lights, n, color1, color2):
    radius = lights.size // 20
    for d in range(0, radius):
        for pixel in range(n - d, n + d):
            if pixel >= 0 and pixel < lights.size:
                lights.set_pixel_hsv(
                    pixel,
                    random.choice([color1, color2]),
                    1,
                    (1.0 * radius - d) / radius,
                )
