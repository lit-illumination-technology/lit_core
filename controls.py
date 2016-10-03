from neopixel import *
import signal
import atexit
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

    
def _clean_shutdown():
    """Registered at exit to ensure ws2812 cleans up after itself
    and all pixels are turned off.
    """
    #off()

def show():
    """Update lights with the contents of the display buffer"""
    ws2812.show()

class Led_Controller:
    def __init__(self, start_i = 0, end_i = 60):
        self.start = start_i
        self.end = end_i
        self.num_leds = end_i - start_i

    def set_range(self, start_i, end_i):
        self.start = start_i
        self.end = end_i
        self.num_leds = end_i - start_i

    def clear(self):
        """Clear the buffer"""
        for n in range(self.start, self.end):
            ws2812.setPixelColorRGB(n, 0, 0, 0)

    def off(self):
        """Clear the buffer and immediately update lights
        Turns off all pixels."""
        self.clear()
        show()

    def set_pixel_hsv(self, index, h, s, v):
        """Set a single pixel to a colour using HSV"""
        if index is not None:
            r, g, b = [int(n*255) for n in colorsys.hsv_to_rgb(h, s, v)]
            ws2812.setPixelColorRGB(index + self.start, r, g, b)


    def set_pixel(self, n, r, g, b):
        """Set a single pixel to RGB colour"""
        ws2812.setPixelColorRGB(n + self.start, r, g, b)


    def get_pixel(self, n):
        """Get the RGB value of a single pixel"""
        if n is not None:
            pixel = ws2812.getPixelColorRGB(n + self.start)
            return int(pixel.r), int(pixel.g), int(pixel.b)


    def set_pixels(self, pixels):
        """Sets the pixels to corresponding picels in an array of pixel tuples. Pixel array must be >= than the string length"""
        self.clear()
        for n in range(0, len(pixels)):
            r, g, b = pixels[n]
            self.set_pixel(n, r, g, b)

    def set_all_pixels(self, r, g, b):
        """Sets all of the pixels to a color in the RGB colorspace"""
        for n in range(0, self.num_leds):
            self.set_pixel(n, r, g, b)

    def set_all_pixels_hsv(self, h, s, v):
        """Sets all of the pixels to a color in the HSV colorspace"""
        for n in range(0, self.num_leds):
            self.set_pixel_hsv(n, h, s, v)
            
    def get_pixels(self):
        """Get the RGB value of all pixels in a 1d array of 3d tuples"""
        return [get_pixel(n) for n in range(0, self.num_leds)]

    def show(self):
        show()

signal.signal( signal.SIGHUP, _clean_shutdown )
signal.signal( signal.SIGTERM, _clean_shutdown )
atexit.register(_clean_shutdown)
