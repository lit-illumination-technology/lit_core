import logging

logger = logging.getLogger(__name__)

# This is what will appear in all interfaces
name = "Effect Display Name"

# This is what the user will see after the effect starts
start_message = name + " started!"

# This is what will appear in tips and help menus
description = "A light effect"

# Schema defines what information the effect needs. This includes all arguments
# that the effect requires as well as any other state that the effect may need.
# All keys in the 'schema' dict will have a corresponding key in the 'state' dict below.
# All schema elements must have a 'value' and 'user_input' field.
# 'value' defines the what data should look like. The fields are:
#'type': {'number', 'color'} required if user_input=True
#'min': minimum allowed value. required if type=number
#'max': maximum allowed value. required if type=number
# *One of the following two fields are required
#'default': The default value. Must be a primitive
#'default_gen': A function that returns a default value.
# 'user_input': True if this field is meant to be an argument passed by the user

schema = {
    "speed": {
        "value": {"type": "number", "min": 0, "max": 100, "default": 50},
        "user_input": True,
    },
    "color": {"value": {"type": "color", "default": (255, 0, 255)}, "user_input": True},
    "custom": {"value": {"default_gen": lambda x: list()}, "user_input": False},
}

# default_speed is the update frequency (in hertz) that the update function will be called
# if no other rate is specified.
default_speed = 20

# This is the function that controls the effect. Look at the included effects for examples.
# Params:
#    lights: A reference to the light controls (A LED_Controller object)
#    step: The number of iterations since starting the effect
#    state: A dictionary that corresponds to the schema above
def update(lights, step, state):
    # Called repeatedy, with step increasing by 1 each call and state persisting
    state["my_list"].append(step)
    lights.set_all_pixels(*state["color"])
