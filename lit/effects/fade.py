name = "Fade"

start_string = "Fading!"

description = "Lights fade from one color to another"

TOTAL_STEPS = 1000

schema = {
    'speed': {
        'value': {
            'type': 'number',
            'min': 0,
            'max': 100,
            'default': 50
        },
        'user_input': True,
        'required': False
    },
    'start color': {
        'value': {
            'type': 'color',
            'default': (0, 0, 0)
        },
        'user_input': True,
        'required': False
    },
    'end color': {
        'value': {
            'type': 'color',
            'default': (0, 0, 0)
        },
        'user_input': True,
        'required': False
    }
}

def update(lights, step, state):
    start_color = state['start color']
    end_color = state['end color']
    if step >= TOTAL_STEPS:
        #TODO hotswap effects
        lights.set_all_pixels(*end_color)
        return
    ar, ag, ab = start_color
    br, bg, bb = end_color
    ds = ((br-ar)/TOTAL_STEPS, (bg-ag)/TOTAL_STEPS, (bb-ab)/TOTAL_STEPS)
    nr = ar+ds[0]*step
    ng = ag+ds[1]*step
    nb = ab+ds[2]*step
    lights.set_all_pixels(max(0,int(nr)), max(0,int(ng)), max(0,int(nb)))
