name = "Throb"

start_message = name + " started!"

description = "Shifts through brighness levels repeatedly"

schema = {
    "color": {
        "value": {"type": "color", "default": (255, 0, 0)},
        "user_input": True,
        "required": False,
    },
    "brightness": {"value": {"type": "number", "default": 0}, "user_input": False},
    "delta": {"value": {"type": "number", "default": 0.05}, "user_input": False},
}


def update(lights, step, state):
    brightness = state["brightness"]
    color = state["color"]
    lights.set_all_pixels(
        int(color[0] * brightness),
        int(color[1] * brightness),
        int(color[2] * brightness),
    )
    if brightness + state["delta"] > 1 or brightness + state["delta"] < 0:
        state["delta"] *= -1
    state["brightness"] += state["delta"]
