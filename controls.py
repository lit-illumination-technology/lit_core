from neopixel import *
import signal
import atexit
import colorsys

# LED strip configuration:
LED_COUNT      = 60      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

ws2812 = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
ws2812.begin()

    
def _clean_shutdown():
    """Registered at exit to ensure ws2812 cleans up after itself
    and all pixels are turned off.
    """
    off()

def brightness(b=0.2):
    """Set the display brightness between 0.0 and 1.0"""

    if b > 1 or b < 0:
        raise ValueError('Brightness must be between 0.0 and 1.0')

    ws2812.setBrightness(int(b*255.0))


def get_brightness():
    """Get the display brightness value
    Returns a float between 0.0 and 1.0
    """
    return 0#ws2812.getBrightness()


def clear():
    """Clear the buffer"""
    for n in range(LED_COUNT):
        ws2812.setPixelColorRGB(n, 0, 0, 0)


def off():
    """Clear the buffer and immediately update lights
    Turns off all pixels."""
    clear()
    show()

def set_pixel_hsv(index, h, s, v):
    """Set a single pixel to a colour using HSV"""
    if index is not None:
        r, g, b = [int(n*255) for n in colorsys.hsv_to_rgb(h, s, v)]
        ws2812.setPixelColorRGB(index, r, g, b)


def set_pixel(n, r, g, b):
    """Set a single pixel to RGB colour"""
    ws2812.setPixelColorRGB(n, r, g, b)


def get_pixel(n):
    """Get the RGB value of a single pixel"""
    if n is not None:
        pixel = ws2812.getPixelColorRGB(n)
        return int(pixel.r), int(pixel.g), int(pixel.b)


def set_pixels(pixels):
    """Sets the pixels to corresponding picels in an array of pixel tuples. Pixel array must be >= than the string length"""
    clear()
    for n in range(0, len(pixels)):
        r, g, b = pixels[n]
        set_pixel(n, r, g, b)

def set_all_pixels(r, g, b):
    """Sets all of the pixels to a color in the RGB colorspace"""
    for n in range(0, 60):
        set_pixel(n, r, g, b)

def set_all_pixels_hsv(h, s, v):
    """Sets all of the pixels to a color in the HSV colorspace"""
    for n in range(0, 60):
        set_pixel_hsv(n, h, s, v)
        
def get_pixels():
    """Get the RGB value of all pixels in a 1d array of 3d tuples"""
    return [get_pixel(n) for n in range(LED_COUNT)]


def show():
    """Update lights with the contents of the display buffer"""
    ws2812.show()

signal.signal( signal.SIGHUP, _clean_shutdown )
signal.signal( signal.SIGTERM, _clean_shutdown )
atexit.register(_clean_shutdown)
