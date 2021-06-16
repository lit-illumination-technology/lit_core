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
    "delta": {"value": {"type": "number", "default": -0.05}, "user_input": False},
    "lower_bound": {"value": {"type": "number", "default": 0.1}, "user_input": False},
    "current_color": {"value": {"type": "color", "default": (0, 0, 0)}, "user_input": False},
}


def update(lights, step, state):
    brightness = state["brightness"]
    color = state["current_color"]
    lower_bound = state["lower_bound"]
    if brightness + state["delta"] > 1:
        state["delta"] *= -1
    elif brightness + state["delta"] < lower_bound:
        state["delta"] *= -1 
        state["current_color"] = state["color"].get_color(step)

    state["brightness"] += state["delta"]

    lights.set_all_pixels(
        int(color[0] * brightness),
        int(color[1] * brightness),
        int(color[2] * brightness),
    )
