from neopixel import *
import colorsys, ConfigParser, socket

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


config = ConfigParser.ConfigParser()
config.read("configuration/config.ini")
# LED strip configuration:
LED_COUNT	= config.getint("General", "leds")     # Total number of LED pixels physically connected to this Pi
LED_PIN		= config.getint("General", "pin")      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ	= 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA		= 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS	= 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT	= False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL	= 0
LED_STRIP	= ws.WS2812_STRIP	#Uses GBR instead of RGB
#Comment the above line and uncomment line that matches your model
#LED_STRIP	= ws.WS2811_STRIP_RGB
#LED_STRIP	= ws.SK6812_STRIP
#LED_STRIP	= ws.SK6812W_STRIP

ws2812 = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
ws2812.begin()


def show():
    """Update lights with the contents of the display buffer"""
    ws2812.show()

class Led_Controller:
    def __init__(self, ranges = {'default' : range(0, 60)}, virtual_ranges = {}):
        """Creates a new Led_Controller.
        ranges: The named led ranges that can be controlled
        virtual_ranges: The names of the ranges that are not connected to this device
        and their respective controller modules.
        """
        self.ranges = sorted(ranges, key=lambda e: self.ranges[e][-1])
        self.virtual_ranges = virtual_ranges
        #Currently active ranges sorted by end location
        self.active_ranges = []
        self.inactive_ranges = list(ranges)
        #Number of currently active leds
        self.num_leds = 0
        #Number of leds in all ranges, local and virtual
        self.total_leds = max(r[-1]+1 for r in self.ranges.itervalues())
        self.pixels = [0]*self.total_leds
        #A mapping from absolute index to (local index, controller)
        #"Local pixels" will be formatted as (index, ws2182)
        self.pixel_locations = [-1]*self.total_leds
        for range_name in self.ranges:
            local_index = 0
            if virtual_ranges.has_key(range_name):
                virtual_index = 0
                for i in self.virtual_ranges[range_name].range:
                    self.pixel_locations[i] = (virtual_index, self.virtual_ranges[range_name])
            else:
                for i in self.ranges[range_name]:
                    self.pixel_locations[i] = (local_index, ws2812)
                    local_index += 1

        print self.pixel_locations


    def set_ranges(self, new_ranges):
        """Sets the currently active ranges to new_ranges and updates other dependent fields"""
        self.active_ranges = sorted(new_ranges, key=lambda e: self.ranges[e][-1])
        self.inactive_ranges = [x for x in self.ranges if x not in self.active_ranges]
        self.num_leds = sum(len(self.ranges[r]) for r in self.active_ranges)

    def get_ranges(self):
        """Returns a list of currently active ranges"""
        return [self.ranges[k] for k in self.active_ranges]

    def all_lights(self):
        """Generator for all currently active light indicies"""
        for ri in self.active_ranges:
            for n in self.ranges[ri]:
                yield n

    def all_lights_with_count(self):
        """Generator for all currently active light indicies
        with count for relative light position in currently
        active lights"""
        n = 0
        for ri in self.active_ranges:
            for i in self.ranges[ri]:
                yield (i, n)
                n += 1

    def all_other_lights(self):
        """Generator for all lights that are not in an active range"""
        for ri in self.inactive_ranges:
            for n in self.ranges[ri]:
                yield n

    def all_other_lights_with_count(self):
        """Generator for all lights that are not in an active range
        with count for relative light position"""
        n = 0
        for ri in self.inactive_ranges:
            for i in self.ranges[ri]:
                yield (i, n)
                n += 1

    def clear(self):
        """Clear the buffer"""
        self.set_all_pixels(0, 0, 0)
        self.set_all_other_pixels(0, 0, 0)

    def off(self):
        """Clear the buffer and immediately update lights
        Turns off all pixels."""
        self.clear()
        show()

    def set_pixel_hsv(self, index, h, s, v):
        """Set a single pixel to a colour using HSV"""
        if index is not None:
            r, g, b = [int(n*255) for n in colorsys.hsv_to_rgb(h, s, v)]
            self.set_pixel(index, r, g, b)

    def set_pixel(self, n, r, g, b):
        """Set a single pixel to RGB colour"""
        self.pixels[n] = (r, g, b)
        location = self.pixel_locations[n]
        location[1].setPixelColorRGB(location[0], GAMMA[r], GAMMA[g], GAMMA[b])


    def get_pixel(self, n):
        """Get the RGB value of a single pixel"""
        if n is not None:
            return self.pixels[n]


    def set_pixels(self, pixels):
        """Sets the pixels to corresponding pixels in an array of pixel tuples. Pixel array must be >= than the string length"""
        self.clear()
        for n in range(0, len(pixels)):
            r, g, b = pixels[n]
            self.set_pixel(n, r, g, b)

    def set_pixels_hsv(self, pixels):
        """Sets the pixels to corresponding pixels in an array of pixel tuples. Pixel array must be >= than the string length"""
        self.clear()
        for n in range(0, len(pixels)):
            r, g, b = [int(p*255) for p in colorsys.hsv_to_rgb(*pixels[n])]
            self.set_pixel(n, r, g, b)

    def set_all_pixels(self, r, g, b):
        """Sets all of the pixels to a color in the RGB colorspace"""
        for n in self.all_lights():
            self.set_pixel(n, r, g, b)

    def set_all_other_pixels(self, r, g, b):
        """Sets all of the pixels to a color in the RGB colorspace"""
        for n in self.all_other_lights():
            self.set_pixel(n, r, g, b)

    def set_all_pixels_hsv(self, h, s, v):
        """Sets all of the pixels to a color in the HSV colorspace"""
        for n in self.all_lights():
            self.set_pixel_hsv(n, h, s, v)

    def set_all_other_pixels_hsv(self, h, s, v):
        """Sets all of the pixels to a color in the HSV colorspace"""
        for n in self.all_other_lights():
            self.set_pixel_hsv(n, h, s, v)
            
    def get_pixels(self):
        """Get the RGB value of all pixels in a 1d array of 3d tuples"""
        return self.pixels

    def show(self):
        """Pushes the led array to the actual lights"""
        show()

class Virtual_Range:
    def __init__(self, num_pixels, ip, port):
        self.range = range(0, num_pixels) 
        self.ip = ip
        self.port = port
        self.pixels = [(0, 0, 0)]*num_pixels
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def setPixelColorRGB(n, r, g, b):
        self.pixels[n] = (r, g, b)

    def show():
        self.socket.sendto(bytes(self.pixels), (self.ip, self.port))
