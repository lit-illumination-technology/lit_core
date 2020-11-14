import random

name = "Nexus"

start_message = name + " started!"

description = "Like the Nexus android wallpaper"


def gen_projectile(lights_size):
    right = random.random() < 0.5
    distance_from_start = random.randint(0, lights_size // 2)
    return [
        -distance_from_start
        if right
        else (lights_size - 1 + distance_from_start),  # Head position
        (1 if right else -1) * (max(0.3, random.normalvariate(2, 1))),  # Speed
        random.random(),  # Hue
    ]


def gen_starting_projectiles(lights, args):
    projectiles = []
    for _ in range(args["number"]):
        projectiles.append(gen_projectile(lights.size))
    return projectiles


schema = {
    "number": {
        "value": {
            "type": "number",  # TODO integer type (or step)
            "min": 1,
            "max": 50,
            "default": 10,
        },
        "user_input": True,
        "required": False,
        "index": 0,
    },
    "projectiles": {
        "value": {"type": "int list", "default_gen": gen_starting_projectiles},
        "user_input": False,
    },
}


def update(lights, step, state):
    projectiles = state["projectiles"]
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
                count[tail_pixel] += v
        projectiles[i][0] = projectiles[i][0] + projectiles[i][1]
        if (val[0] + tail_length < 0 and val[1] < 0) or (
            val[0] - tail_length >= lights.size and val[1] > 0
        ):
            projectiles[i] = gen_projectile(lights.size)
    lights.set_pixels_hsv(hsvs)
