import random

name = "Nexus"

start_message = name + " started!"

description = "Like the Nexus android wallpaper"

schema = {
    "projectiles": {
        "value": {"type": "int list", "default_gen": lambda lights, args: list()},
        "user_input": False,
    },
}


def update(lights, step, state):
    # TODO constant number of projectiles. Reuse when go fall off strip. Avoids O(n) remove and inserts.
    projectiles = state["projectiles"]
    if random.random() < 0.05:
        right = random.random() < 0.5
        projectiles.append(
            [
                0 if right else (lights.size - 1),
                (1 if right else -1) * (max(0.3, random.normalvariate(2, 1))),
                random.random(),
            ]
        )

    hsvs = [[0, 0, 0, 0] for _ in range(0, lights.size)]
    # Total of value(HSV) at each position
    count = [0] * lights.size
    for i, val in enumerate(projectiles):
        tail_length = int(15 * abs(val[1]))
        for t in range(0, tail_length):
            tail_pixel = int(val[0] + t * (1 if val[1] < 0 else -1))
            if tail_pixel >= 0 and tail_pixel < lights.size:
                (h, s, v) = (val[2], 1, (tail_length - 1.0 * t) / tail_length)
                hsvs[tail_pixel][0] = (
                    hsvs[tail_pixel][0] * count[tail_pixel] + (h * v)
                ) / (count[tail_pixel] + v)
                hsvs[tail_pixel][1] = s
                hsvs[tail_pixel][2] = max(hsvs[tail_pixel][2], v)
                hsvs[tail_pixel][3] = max(
                    hsvs[tail_pixel][3], (tail_length - 1.0 * t) / tail_length
                )
                # rgbs[tail_pixel] = ((rgbs[tail_pixel][0] * count[tail_pixel]) + r) / (count[tail_pixel] + 1)
                # rgbs[tail_pixel][1] = ((rgbs[tail_pixel][1] * count[tail_pixel]) + g) / (count[tail_pixel] + 1)
                # rgbs[tail_pixel][2] = ((rgbs[tail_pixel][2] * count[tail_pixel]) + b) / (count[tail_pixel] + 1)
                count[tail_pixel] = count[tail_pixel] + v
        projectiles[i][0] = projectiles[i][0] + projectiles[i][1]
        if val[0] + tail_length < 0 or val[0] - tail_length >= lights.size:
            projectiles.remove(val)
    lights.set_pixels_hsv(hsvs)
