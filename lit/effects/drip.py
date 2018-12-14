import random
name = "Drip"

start_string = name + " started!"

description = "Mimics water droplets accumulating and falling"

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
    'color': {
        'value': {
            'type': 'color',
            'default': (0, 20, 175)
        },
        'user_input': True,
        'required': False
    }
}

def update(lights, step, state):
    if step == 0:
        state['dullness'] = [15]*lights.num_leds
    color = state['color'];
    dullness = state['dullness']
    for i in range(lights.num_leds):
        lights.set_pixel(i, int(color[0]/dullness[i]), int(color[1]/dullness[i]), int(color[2]/dullness[i]))
        dullness[i] -= random.random()/20
        if dullness[i]<=1 or random.randint(0, int(dullness[i]*20)) == 0:
            dullness[i] = (random.random()*2)+4
