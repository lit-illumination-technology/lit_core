name = "Fade"

start_string = "Fading!"

description = "Lights fade from their current color to a new color"

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
            'default': (0, 0, 0)
        },
        'user_input': True,
        'required': False
    },
    'steps_left': {
        'value': {
            'type': 'number',
            'default': 0
        },
        'user_input': False
    }
}

def update(lights, step, state):
    state['steps_left'] -= 1
    n = state['steps_left']
    color = state['color']
    if n < 0:
        #TODO hotswap effects
        lights.set_all_pixels(*color)
        return
    pixels = lights.get_pixels()
    ds = [(0, 0, 0)]*lights.num_leds

    for i in range(lights.num_leds):
        r, g, b = lights.get_pixels()[i]
        pixels[i] = (float(r), float(g), float(b))
        ds[i] = ((color[0]-r)/n, (color[1]-g)/n, (color[2]-b)/n)
        r = pixels[p][0]+ds[p][0]
        g = pixels[p][1]+ds[p][1]
        b = pixels[p][2]+ds[p][2]
        pixels[p] = (max(0,int(r)), max(0,int(g)), max(0,int(b)))

    lights.set_pixels(pixels)
