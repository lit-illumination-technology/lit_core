name = "Off"

start_string = "The lights have been turned off."

description = "Turns the lights off"

schema = {
    'speed': {
        'value': {
            'type': 'number',
            'min': 0,
            'max': 5,
            'default': 1
        },
        'user_input': False,
        'required': False
    }
}

def update(lights, step, state):
    lights.clear()
