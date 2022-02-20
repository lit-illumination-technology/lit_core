# This is what will appear in all interfaces
name = "On"

# This is what the user will see after the effect starts
start_message = "The lights have been turned on!"

# This is what will appear in tips and help menus
description = "Turns all of the lights on to a specfied color"

default_speed = 0

# This defines the format of update's 'state' parameter
schema = {
    "color": {
        "value": {"type": "color", "default": (255, 255, 255)},
        "user_input": True,
        "required": False,
    },
}

# This is the function that updates the effect.
# Params:
#   lights: A reference to the light controls (the only way to make anything happen).
#   step: The number of times that this effect has been updated
#   state: Dict with information about the state of the effect
def update(lights, step, state):
    colors = [state["color"].get_color(step, i) for i in range(lights.size)]
    lights.set_pixels(colors)
