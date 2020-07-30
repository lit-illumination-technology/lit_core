import logging
import time
import socket

logger = logging.getLogger(__name__)


class DeviceAdapter:
    """ A DeviceAdapter represents a physical display device.
    Many Sections can share one DeviceAdapter 
    Indexing is relative to the device
    """

    def __init__(self, name, size):
        self.size = size
        self.name = name

    @staticmethod
    def from_config(config):
        adapter_type = config.get("type")
        if adapter_type == "ws2812":
            adapter = WS2812Adapter(config["name"], config["size"], config["pin"])
        elif adapter_type == "udp":
            adapter = UDPAdapter(
                config["name"], config["size"], config["ip"], config["port"]
            )
        return adapter

    def set_pixel_color_rgb(self, n, r, g, b):
        pass

    def show(self):
        pass

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        # Device adapters are unique by name
        return hash(self.name)


class UDPAdapter(DeviceAdapter):
    def __init__(self, name, size, ip, port):
        super().__init__(name, size)
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.pixels = [0] * size * 3

    def set_pixel_color_rgb(self, n, r, g, b):
        self.pixels[3 * n] = r
        self.pixels[3 * n + 1] = g
        self.pixels[3 * n + 2] = b

    def show(self):
        payload = bytearray(self.pixels) + int(time.time() * 100).to_bytes(8, "little")
        self.socket.sendto(payload, 0, (self.ip, self.port))


class WS2812Adapter(DeviceAdapter):

    created = False

    def __init__(self, name, size, pin):
        if WS2812Adapter.created:
            raise Exception("There can only be one adapter of type ws2812")
        super().__init__(name, size)
        self.pin = pin
        self.size = size
        self.ws2812 = self._init_ws2812()
        WS2812Adapter.created = True

    def set_pixel_color_rgb(self, n, r, g, b):
        super().set_pixel_color_rgb(n, r, g, b)
        self.ws2812.setPixelColorRGB(n, r, g, b)

    def show(self):
        self.ws2812.show()

    def _init_ws2812(self):
        from rpi_ws281x import Adafruit_NeoPixel, WS2812_STRIP

        LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA = 10  # DMA channel to use for generating signal (try 5)
        LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
        # True to invert the signal (when using NPN transistor level shift)
        LED_INVERT = False
        LED_CHANNEL = 0

        LED_STRIP = WS2812_STRIP
        ws2812 = Adafruit_NeoPixel(
            self.size,
            self.pin,
            LED_FREQ_HZ,
            LED_DMA,
            LED_INVERT,
            LED_BRIGHTNESS,
            LED_CHANNEL,
            LED_STRIP,
        )
        ws2812.begin()
        return ws2812
