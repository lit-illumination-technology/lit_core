import random
import logging

logger = logging.getLogger(__name__)
name = "Heartbeat"

start_message = name + " started!"

description = "La-dub la-dub"

schema = {
    "color": {
        "value": {"type": "color", "default": [255, 0, 0]},
        "user_input": True,
        "required": False,
    }
}


def update(lights, step, state):
    color = state["color"]
    sub_step = step % 60
    lub = sub_step in range(0, 3) or sub_step in range(9, 12)
    brightness = 1 if lub else 0.4
    lights.set_all_pixels(*tuple(map(lambda x: int(x * brightness), color)))
