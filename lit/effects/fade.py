name = "Fade"

start_message = "Fading!"

description = "Lights fade from one color to another"

TOTAL_STEPS = 1000


def calc_delta(lights, args):
    ar, ag, ab = args["start color"]
    br, bg, bb = args["end color"]
    return ((br - ar) / TOTAL_STEPS, (bg - ag) / TOTAL_STEPS, (bb - ab) / TOTAL_STEPS)


schema = {
    "start color": {
        "value": {"type": "color", "default": (0, 0, 0)},
        "user_input": True,
        "required": False,
        "index": 0,
    },
    "end color": {
        "value": {"type": "color", "default": (255, 255, 255)},
        "user_input": True,
        "required": False,
        "index": 0,
    },
    "delta": {
        "value": {"type": "number tuple", "default_gen": calc_delta},
        "user_input": False,
    },
}


def update(lights, step, state):
    if step >= TOTAL_STEPS:
        # TODO hotswap effects
        end_color = state["end color"]
        lights.set_all_pixels(*end_color)
        return
    ar, ag, ab = state["start color"]
    dr, dg, db = state["delta"]
    nr = ar + dr * step
    ng = ag + dg * step
    nb = ab + db * step
    lights.set_all_pixels(max(0, int(nr)), max(0, int(ng)), max(0, int(nb)))
