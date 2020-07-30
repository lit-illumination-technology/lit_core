import random
import logging

logger = logging.getLogger(__name__)
name = "Rainbow Fireflies"

start_message = name + " started!"

description = "The most fabulous fireflies"

COLORS = [
    (231, 0, 0),
    (255, 85, 0),
    (255, 239, 0),
    (0, 129, 0),
    (0, 68, 255),
    (74, 0, 118),
]


def setup_start_durations(lights, args):
    return [(-1, 1, (0, 0, 0))] * lights.size


schema = {
    "density": {
        "value": {"type": "number", "min": 1, "max": 100, "default": 50},
        "user_input": True,
        "required": False,
    },
    "start_duration_colors": {
        "value": {
            "type": "(int, int, color) list",
            "default_gen": setup_start_durations,
        },
        "user_input": False,
    },
}

# Average time a led is on
AVG_ON_TIME = 100
MIN_ON_TIME = 10


def update(lights, step, state):
    start_durations = state["start_duration_colors"]
    """ MATH:
    DENSITY = OnTime/(Ontime+OffTime)
    OnTime(1-DENSITY) = Density*OffTime
    Offtime = ((1-Density)*OnTime)/Density 
    """
    density = state["density"] / 100
    avg_off_time = ((1 - density) * AVG_ON_TIME) / density
    for i in range(lights.size):
        sd = start_durations[i]
        if sd[0] + sd[1] <= step:
            color = COLORS[random.randint(0, len(COLORS) - 1)]
            state["start_duration_colors"][i] = (
                step + random.randint(0, int(2 * avg_off_time)),
                MIN_ON_TIME + random.randint(0, (AVG_ON_TIME - MIN_ON_TIME) * 2),
                color,
            )
        brightness = (step - sd[0]) / (sd[1] / 2)
        if brightness > 1:
            brightness = 2 - brightness
        brightness = max(brightness, 0)
        lights.set_pixel(
            i,
            int(sd[2][0] * brightness),
            int(sd[2][1] * brightness),
            int(sd[2][2] * brightness),
        )
