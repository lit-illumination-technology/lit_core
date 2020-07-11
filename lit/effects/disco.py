name = "Disco"

start_string = name + " started!"

description = "Color spectrum is repeatedly 'squished' to one side."

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
    off = step/10
    for i in range(lights.size):
        lights.set_pixel_hsv(i, ((i*off)/float(lights.size))%1, 1, 1)

