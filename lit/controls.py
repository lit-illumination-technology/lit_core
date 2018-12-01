from neopixel import *
import colorsys
import socket
import logging

"""Mapping to make RGB values appear more natural"""
GAMMA = [
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
    10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
    17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
    25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
    37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
    51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
    69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
    90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
    115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
    144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
    177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
    215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255 ];


# LED strip configuration:
LED_FREQ_HZ	= 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA		= 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS	= 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT	= False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL	= 0
LED_STRIP	= ws.WS2812_STRIP	#Uses GBR instead of RGB
#TODO add to config
#Comment the above line and uncomment line that matches your model
#LED_STRIP	= ws.WS2811_STRIP_RGB
#LED_STRIP	= ws.SK6812_STRIP
#LED_STRIP	= ws.SK6812W_STRIP

logger = logging.getLogger(__name__)

class Led_Controller_Manager:
    def __init__(self, led_count = 60, led_pin = 18, sections= {'default' : range(0, 60)}, virtual_sections= {}):
        """Creates a new Led_Controller Manager.
        led_count: Total number of LED pixels physically connected to this Pi
        led_pin: GPIO pin connected to the pixels (must support PWM!)
        sections: The named led sections that can be controlled
        virtual_sections: The names of the sections that are not connected to this device
        and their respective controller modules.
        """
        self.ws2812 = Adafruit_NeoPixel(led_count, led_pin, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
        self.ws2812.begin()
        self.led_count = led_count
        self.led_pin = led_pin
        self.controllers = []
        self.sections = sections
        self.section_ordered = sorted(self.sections, key=lambda e: self.sections[e][-1])
        self.virtual_sections = virtual_sections
        #Number of leds in all sections, local and virtual
        self.total_leds = max(r[-1]+1 for r in self.sections.values())
        #A mapping from absolute index to (local index, controller)
        #"Local pixels" will be formatted as (index, self.ws2182)
        self.pixel_locations = [-1]*self.total_leds
        local_index = 0
        for section_name in self.section_ordered:
            if section_name in virtual_sections:
                virtual_index = 0
                for i in self.sections[section_name]:
                    self.pixel_locations[i] = (virtual_index, self.virtual_sections[section_name])
                    virtual_index += 1
            else:
                for i in self.sections[section_name]:
                    self.pixel_locations[i] = (local_index, self.ws2812)
                    local_index += 1

    # Creates a new Led_Controller for the sections, and removes intersecting sections from other controllers
    def create_controller(self, sections):
        controller = Led_Controller(self)
        controller.set_sections(sections)
        for c in self.controllers:
            if any(s in sections for s in c.active_sections):
                c.set_sections([s for s in c.active_sections if s not in sections])
        self.controllers.append(controller)
        # Remove any empty controllers
        self.controllers = [c for c in self.controllers if c.num_leds != 0]
        return controller

    def get_controllers(self):
        return self.controllers

class Led_Controller:
    def __init__(self, manager):
        """Creates a new Led_Controller with no active ranges"""
        self.ws2812 = manager.ws2812
        self.sections = manager.sections
        self.section_ordered = sorted(self.sections, key=lambda e: self.sections[e][-1])
        self.virtual_sections = manager.virtual_sections
        #Currently active sections sorted by end location
        self.active_sections = []
        self.inactive_sections = list(self.sections)
        #Number of currently active leds
        self.num_leds = 0
        #Number of leds in all sections, local and virtual
        self.total_leds = manager.total_leds
        self.pixels = [(0, 0, 0)]*self.total_leds
        #A mapping from absolute index to (local index, controller)
        #"Local pixels" will be formatted as (index, self.ws2182)
        self.pixel_locations = manager.pixel_locations

    def set_sections(self, new_sections):
        """Sets the currently active sections to new_sections and updates other dependent fields.
        new_sections is a list of section names corresponding to the sections dict keys"""
        self.active_sections = sorted(new_sections, key=lambda e: self.sections[e][-1])
        self.inactive_sections = [x for x in self.sections if x not in self.active_sections]
        self.num_leds = sum(len(self.sections[r]) for r in self.active_sections)

    def get_sections(self):
        """Returns a list of currently active sections"""
        return [self.sections[k] for k in self.active_sections]

    def all_lights(self):
        """Generator for all currently active light indicies"""
        for ri in self.active_sections:
            for n in self.sections[ri]:
                yield n

    def all_lights_with_count(self):
        """Generator for all currently active light indicies
        with count for relative light position in currently
        active lights"""
        n = 0
        for ri in self.active_sections:
            for i in self.sections[ri]:
                yield (i, n)
                n += 1

    # Deprecated. DO NOT USE
    def all_other_lights(self):
        """Generator for all lights that are not in an active section"""
        for ri in self.inactive_sections:
            for n in self.sections[ri]:
                yield n

    # Deprecated. DO NOT USE
    def all_other_lights_with_count(self):
        """Generator for all lights that are not in an active section
        with count for relative light position"""
        n = 0
        for ri in self.inactive_sections:
            for i in self.sections[ri]:
                yield (i, n)
                n += 1

    def clear(self):
        """Clear the currently active buffer"""
        self.set_all_pixels(0, 0, 0)

    def clear_absolute(self):
        """Clear the buffer for entire strip"""
        self.set_all_absolute_pixels(0, 0, 0)

    def off(self):
        """Clear the buffer and immediately update lights
        Turns off all pixels."""
        self.clear()
        self.show()

    def set_absolute_pixel_hsv(self, index, h, s, v):
        """Set a single pixel to a colour using HSV"""
        if index is not None:
            r, g, b = [int(n*255) for n in colorsys.hsv_to_rgb(h, s, v)]
            self.set_absolute_pixel(index, r, g, b)

    def set_absolute_pixel(self, n, r, g, b):
        """Set a single pixel to RGB colour"""
        self.pixels[n] = (r, g, b)
        location = self.pixel_locations[n]
        location[1].setPixelColorRGB(location[0], GAMMA[r], GAMMA[g], GAMMA[b])

    def set_pixel(self, n, r, g, b):
        """Set a single pixel to RGB colour, with index only counting active sections.
        O(s) where s is the number of active sections"""
        if n >= self.num_leds:
            return
        remaining = n
        i = 0
        for section_name in self.active_sections:
            if remaining < len(self.sections[section_name]):
                i = self.sections[section_name][0] + remaining
                break
            else:
                remaining -= len(self.sections[section_name])
        self.pixels[i] = (r, g, b)
        location = self.pixel_locations[i]
        location[1].setPixelColorRGB(location[0], GAMMA[r], GAMMA[g], GAMMA[b])

    def set_pixel_hsv(self, n, h, s, v):
        """Set a single pixel to RGB colour, with index only counting active sections.
        O(s) where s is the number of active sections"""
        r, g, b = [int(n*255) for n in colorsys.hsv_to_rgb(h, s, v)]
        self.set_pixel(n, r, g, b)

    def get_absolute_pixel(self, n):
        """Get the RGB value of a single pixel"""
        if n is not None:
            return self.pixels[n]

    def set__all_absolute_pixels(self, r, g, b):
        """Sets all pixels to the same RGB color"""
        for n in range(0, len(pixels)):
            self.set_absolute_pixel(n, r, g, b)

    def set__all_absolute_pixels_hsv(self, h, s, v):
        """Sets all pixels to the same RGB color"""
        r, g, b = [int(n*255) for n in colorsys.hsv_to_rgb(h, s, v)]
        self.set_all_absolute_pixels(r, g, b)

    def set_absolute_pixels(self, pixels):
        """Sets the pixels to corresponding pixels in an array of pixel tuples."""
        self.clear_absolute()
        for n in range(0, len(pixels)):
            r, g, b = pixels[n]
            self.set_absolute_pixel(n, r, g, b)

    def set_absolute_pixels_hsv(self, pixels):
        """Sets the pixels to corresponding pixels in an array of pixel tuples."""
        self.clear()
        for n in range(0, len(pixels)):
            r, g, b = [int(p*255) for p in colorsys.hsv_to_rgb(*pixels[n])]
            self.set_absolute_pixel(n, r, g, b)

    def set_pixels(self, pixels):
        """Set active pixels to corresponding pixels in array of rgb tuples with size num_leds"""
        self.clear()
        for n in range(0, len(pixels)):
            r, g, b = pixels[n]
            self.set_pixel(n, r, g, b)

    def set_pixels_hsv(self, pixels):
        """Set active pixels to corresponding pixels in array of hsv tuples with size num_leds"""
        self.clear()
        for n in range(0, len(pixels)):
            r, g, b = [int(p*255) for p in colorsys.hsv_to_rgb(*pixels[n])]
            self.set_pixel(n, r, g, b)

    def set_all_pixels(self, r, g, b):
        """Sets all of the pixels to a color in the RGB colorspace"""
        for n in self.all_lights():
            self.set_absolute_pixel(n, r, g, b)


    # Deprecated: DO NOT USE
    def set_all_other_pixels(self, r, g, b):
        """Sets all of the pixels to a color in the RGB colorspace"""
        for n in self.all_other_lights():
            self.set_absolute_pixel(n, r, g, b)

    def set_all_pixels_hsv(self, h, s, v):
        """Sets all of the pixels to a color in the HSV colorspace"""
        for n in self.all_lights():
            self.set_absolute_pixel_hsv(n, h, s, v)

    # Deprecated: DO NOT USE
    def set_all_other_pixels_hsv(self, h, s, v):
        """Sets all of the pixels to a color in the HSV colorspace"""
        for n in self.all_other_lights():
            self.set_absolute_pixel_hsv(n, h, s, v)
            
    def get_absolute_pixels(self):
        """Get the RGB value of all pixels in a 1d array of 3d tuples"""
        return self.pixels

    def show(self):
        """Pushes the led array to the actual lights"""
        self.ws2812.show()
        for vr in self.virtual_sections:
            self.virtual_sections[vr].show()

class Virtual_Range:
    def __init__(self, num_pixels, ip, port):
        self.section = range(0, num_pixels) 
        self.ip = ip
        self.port = port
        self.pixels = [(0, 0, 0)]*num_pixels*3
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def setPixelColorRGB(self, n, r, g, b):
        self.pixels[3 * n] = r
        self.pixels[3 * n + 1] = g
        self.pixels[3 * n + 2] = b

    def show(self):
        self.socket.sendto(bytearray(self.pixels), (self.ip, self.port))
