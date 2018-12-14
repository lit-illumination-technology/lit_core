name = "Slide"

start_string = name + " started!"

description = "The full color spectrum shifts along the strand."

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
    }
}

def update(lights, step, state):
    for i in range(lights.num_leds):
        lights.set_pixel_hsv(i, (1.0*(i+step)/(lights.num_leds/2))%1, 1, 1)
