import controls

def on(lights, stop_event, color = [255, 255, 255], **extras):
    """Turns the entire string on.
    Param r, g, b: Default white. RGB values for light color. [0, 255]"""

    lights.set_all_pixels(color[0], color[1], color[2])
    lights.show()
    stop_event.wait()

