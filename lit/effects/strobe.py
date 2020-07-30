name = "Strobe"

start_string = name + " started!"

description = "Lights flash rapidly"

schema = {
    'speed': {
        'value': {
            'type': 'number',
            'min': 0,
            'max': 50,
            'default': 10 
        },
        'user_input': True,
        'required': False
    },
    'color': {
        'value': {
            'type': 'color',
            'default': (255, 255, 255)
        },
        'user_input': True,
        'required': False
    }
}

def update(lights, step, state):
    color = state['color']
    if step % 2 == 0:
        lights.set_all_pixels(color[0], color[1], color[2])
    else:
        lights.clear()

