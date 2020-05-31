import colorsys
import socket
import time
import logging

# LED strip configuration:
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0
# TODO add to config
# Comment the above line and uncomment line that matches your model
# LED_STRIP	= ws.WS2811_STRIP_RGB
# LED_STRIP	= ws.SK6812_STRIP
# LED_STRIP	= ws.SK6812W_STRIP

logger = logging.getLogger(__name__)


class Led_Controller_Manager:
    def __init__(
        self,
        led_count=60,
        led_pin=18,
        sections={"default": range(0, 60)},
        virtual_sections={},
    ):
        """Creates a new Led_Controller Manager.
        led_count: Total number of LED pixels physically connected to this Pi
        led_pin: GPIO pin connected to the pixels (must support PWM!)
        sections: The named led sections that can be controlled
        virtual_sections: The names of the sections that are not connected to this device
        and their respective controller modules.
        """
        if led_count > 0:
            from rpi_ws281x import Adafruit_NeoPixel, WS2812_STRIP

            LED_STRIP = WS2812_STRIP  # Uses GBR instead of RGB
            self.ws2812 = Adafruit_NeoPixel(
                led_count,
                led_pin,
                LED_FREQ_HZ,
                LED_DMA,
                LED_INVERT,
                LED_BRIGHTNESS,
                LED_CHANNEL,
                LED_STRIP,
            )
            self.ws2812.begin()
        self.controllers = []
        self.sections = sections
        self.section_ordered = sorted(self.sections, key=lambda e: self.sections[e][-1])
        self.virtual_sections = virtual_sections
        # Number of leds in all sections, local and virtual
        self.total_leds = max(r[-1] + 1 for r in self.sections.values())
        # A mapping from absolute index to (local index, controller)
        # "Local pixels" will be formatted as (index, self.ws2182)
        self.pixel_locations = [-1] * self.total_leds
        local_index = 0
        for section_name in self.section_ordered:
            if section_name in virtual_sections:
                virtual_index = 0
                for i in self.sections[section_name]:
                    self.pixel_locations[i] = (
                        virtual_index,
                        self.virtual_sections[section_name],
                    )
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

    def show(self):
        """Pushes the led array to the actual lights"""
        for controller in self.controllers:
            controller.render()

        if len(self.sections) > len(self.virtual_sections):
            self.ws2812.show()
        for vr in self.virtual_sections:
            self.virtual_sections[vr].show()

    def get_pixels(self):
        r = []
        for c in self.controllers:
            logger.info(c)
            for p in c.get_pixels():
                r += [p]
        logger.info(r)
        return r
        # return [p for c in self.controllers for p in c.get_pixels()]


class Led_Controller:
    def __init__(self, manager):
        """Creates a new Led_Controller with no active ranges"""
        if len(manager.sections) > len(manager.virtual_sections):
            self.ws2812 = manager.ws2812
        self.sections = manager.sections
        self.section_ordered = sorted(self.sections, key=lambda e: self.sections[e][-1])
        self.virtual_sections = manager.virtual_sections
        # Currently active sections sorted by end location
        self.active_sections = []
        self.inactive_sections = list(self.sections)
        # Number of currently active leds
        self.num_leds = 0
        # Number of leds in all sections, local and virtual
        self.total_leds = manager.total_leds
        self.pixels = [(0, 0, 0)] * self.total_leds
        # A mapping from absolute index to (local index, controller)
        # "Local pixels" will be formatted as (index, self.ws2182)
        self.absolute_pixel_locations = manager.pixel_locations
        # Mapping from "controller index" to pixel location
        self.pixel_locations = []

    def set_sections(self, new_sections):
        """Sets the currently active sections to new_sections and updates other dependent fields.
        new_sections is a list of section names corresponding to the sections dict keys"""
        self.active_sections = sorted(new_sections, key=lambda e: self.sections[e][-1])
        self.inactive_sections = [
            x for x in self.sections if x not in self.active_sections
        ]
        self.num_leds = sum(len(self.sections[r]) for r in self.active_sections)
        self.pixel_locations = []
        for sn in self.active_sections:
            s = self.sections[sn]
            self.pixel_locations += self.absolute_pixel_locations[s[0] : s[-1] + 1]

    def get_sections(self):
        """Returns a list of currently active sections"""
        return [self.sections[k] for k in self.active_sections]

    def clear(self):
        """Clear the currently active buffer"""
        self.set_all_pixels(0, 0, 0)

    def off(self):
        """Clear the buffer and immediately update lights
        Turns off all pixels."""
        self.clear()
        self.show()

    def set_pixel(self, n, r, g, b):
        """Set a single pixel to RGB colour, with index only counting active sections for this controller"""
        self.pixels[n] = (r, g, b)

    def set_pixel_hsv(self, n, h, s, v):
        """Set a single pixel to RGB colour, with index only counting active sections.
        O(s) where s is the number of active sections"""
        r, g, b = [int(n * 255) for n in colorsys.hsv_to_rgb(h, s, v)]
        self.set_pixel(n, r, g, b)

    def set_pixels(self, pixels):
        """Set active pixels to corresponding pixels in array of rgb tuples with size num_leds"""
        for n in range(0, len(pixels)):
            r, g, b = pixels[n]
            self.set_pixel(n, r, g, b)

    def get_pixels(self):
        return self.pixels

    def set_pixels_hsv(self, pixels):
        """Set active pixels to corresponding pixels in array of hsv tuples with size num_leds"""
        for n in range(0, len(pixels)):
            r, g, b = [int(p * 255) for p in colorsys.hsv_to_rgb(*pixels[n])]
            self.set_pixel(n, r, g, b)

    def set_all_pixels(self, r, g, b):
        """Sets all of the pixels to a color in the RGB colorspace"""
        self.pixels = [(r, g, b)] * self.num_leds

    def set_all_pixels_hsv(self, h, s, v):
        """Sets all of the pixels to a color in the HSV colorspace"""
        r, g, b = [int(p * 255) for p in colorsys.hsv_to_rgb(h, s, v)]
        self.set_all_pixels(r, g, b)

    def render(self):
        """Thread-safe transfer of pixels from controller to 'locations'"""
        for i in range(0, self.num_leds):
            r, g, b = self.pixels[i]
            location = self.pixel_locations[i]
            location[1].setPixelColorRGB(location[0], r, g, b)

    def show(self):
        """Pushes the led array to the actual lights"""
        self.render()
        if len(self.sections) > len(self.virtual_sections):
            self.ws2812.show()
        for vr in self.virtual_sections:
            self.virtual_sections[vr].show()

    def __repr__(self):
        return "Controller: {}".format(self.active_sections)


class Virtual_Range:
    def __init__(self, num_pixels, ip, port):
        self.section = range(0, num_pixels)
        self.ip = ip
        self.port = port
        self.pixels = [(0, 0, 0)] * num_pixels * 3
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def setPixelColorRGB(self, n, r, g, b):
        self.pixels[3 * n] = r
        self.pixels[3 * n + 1] = g
        self.pixels[3 * n + 2] = b

    def show(self):
        self.socket.sendto(bytearray(self.pixels) + int(time.time() * 100).to_bytes(8, 'little'), (self.ip, self.port))
