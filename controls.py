from neopixel import *
import colorsys

# LED strip configuration:
LED_COUNT	= 120     # Total number of LED pixels.
LED_PIN		= 18      # GPIO pin connected to the pixels (must support PWM!).
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
    def __init__(self, ranges = {'default' : range(0, 60)}):
        self.ranges = ranges
        self.active_ranges = []
        self.inactive_ranges = list(ranges)
        self.num_leds = 0
        self.total_leds = sum(len(r) for r in self.ranges.itervalues())

    def set_ranges(self, new_ranges):
        self.active_ranges = new_ranges
        self.inactive_ranges = [x for x in self.ranges if x not in self.active_ranges]
        self.num_leds = sum(len(self.ranges[r]) for r in self.active_ranges)

    def get_ranges(self):
        return [self.ranges[k] for k in self.active_ranges]

    def all_lights(self):
        for ri in self.active_ranges:
            for n in self.ranges[ri]:
                yield n

    def all_lights_with_count(self):
        n = 0
        for ri in self.active_ranges:
            for i in self.ranges[ri]:
                yield (i, n)
                n += 1

    def all_other_lights(self):
        for ri in self.inactive_ranges:
            for n in self.ranges[ri]:
                yield n

    def all_other_lights_with_count(self):
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
            ws2812.setPixelColorRGB(index, r, g, b)


    def set_pixel(self, n, r, g, b):
        """Set a single pixel to RGB colour"""
        ws2812.setPixelColorRGB(n, r, g, b)


    def get_pixel(self, n):
        """Get the RGB value of a single pixel"""
        if n is not None:
            pixel = ws2812.getPixelColor(n)
            return (pixel>>16)&0xff, (pixel>>8)&0xff, pixel&0xff


    def set_pixels(self, pixels):
        """Sets the pixels to corresponding pixels in an array of pixel tuples. Pixel array must be >= than the string length"""
        self.clear()
        for n in range(0, len(pixels)):
            r, g, b = pixels[n]
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
        return [self.get_pixel(n) for n in range(0, self.total_leds)]

    def show(self):
        show()
