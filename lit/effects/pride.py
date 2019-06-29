name = "Pride"

start_string = name + " started!"

description = "Displays rainbow pride flag colors"

COLORS = [(231, 0, 0), (255, 85, 0), (255, 239, 0), (0, 129, 0), (0, 68, 255), (74, 0, 118)]

schema = {
    'speed': {
        'value': {
            'type': 'number',
            'min': 0,
            'max': 100,
            'default': 0
        },
        'user_input': True,
        'required': False
    }
}

def update(lights, step, state):
    stripe_width = (lights.num_leds/len(COLORS))
    start = (step*stripe_width)%lights.num_leds
    end = ((step+1)*stripe_width)%lights.num_leds
    for n, color in enumerate(COLORS):
        for i in range(int(start), int(end)): 
            lights.set_pixel(i, *color)
        start += stripe_width
        start %= lights.num_leds
        end += stripe_width
        end %= (lights.num_leds+1)
