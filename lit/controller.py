import colorsys
import logging

logger = logging.getLogger(__name__)


class ControllerManager:
    def __init__(
        self,
        sections
    ):
        """Creates a new Led_Controller Manager.
        sections: The named led sections that can be controlled. 
        """
        self.controllers = []
        self.sections = sections
        self.display_adapters = {s.section_adapter.display_adapter for s in self.sections.values()}
        self.section_ordered = sorted(self.sections, key=lambda e: self.sections[e].end_index)
        # Number of leds in all sections
        self.total_leds = sum(s.size for s in self.sections.values())
        # A mapping from absolute index to (local index, controller)
        self.pixel_locations = [None] * self.total_leds
        for section_name in self.section_ordered:
            section = self.sections[section_name]
            for local_i, absolute_i in enumerate(section.absolute_range):
                self.pixel_locations[absolute_i] = (
                    local_i,
                    section
                )

    # Creates a new Led_Controller for the sections, and removes intersecting sections from other controllers
    def create_controller(self, sections):
        controller = Controller(self)
        controller.set_sections(sections)
        for c in self.controllers:
            if any(s in sections for s in c.active_sections):
                c.set_sections([s for s in c.active_sections if s not in sections])
        self.controllers.append(controller)
        # Remove any empty controllers
        self.controllers = [c for c in self.controllers if c.size != 0]
        return controller

    def get_controllers(self):
        return self.controllers

    def show(self):
        """Pushes the led array to the actual lights"""
        for controller in self.controllers:
            controller.render()

        for display_adapter in self.display_adapters:
            display_adapter.show()

    def get_pixels(self):
        r = []
        for c in self.controllers:
            logger.info(c)
            for p in c.get_pixels():
                r += [p]
        logger.info(r)
        return r


class Controller:
    """ A grouping of sections that are being controlled as one unit """
    def __init__(self, manager):
        """Creates a new Led_Controller with no active ranges"""
        self.sections = manager.sections
        self.section_ordered = sorted(self.sections, key=lambda e: self.sections[e].end_index)
        # Currently active section names sorted by end location
        self.active_sections = []
        self.inactive_sections = list(self.sections)
        # Number of currently active leds
        self.size  = 0
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
        self.active_sections = sorted(new_sections, key=lambda e: self.sections[e].end_index)
        self.inactive_sections = [
            x for x in self.sections if x not in self.active_sections
        ]
        self.size  = sum(self.sections[r].size for r in self.active_sections)
        self.pixel_locations = []
        for sn in self.active_sections:
            s = self.sections[sn]
            self.pixel_locations += self.absolute_pixel_locations[s.start_index : s.end_index]

    def get_sections(self):
        """Returns a list of currently active sections"""
        return [self.sections[k] for k in self.active_sections]

    def clear(self):
        """Clear the currently active buffer"""
        self.set_all_pixels(0, 0, 0)

    def off(self):
        """ Turns off all pixels. """
        self.clear()

    def set_pixel(self, n, r, g, b):
        """Set a single pixel to RGB colour, with index only counting active sections for this controller"""
        self.pixels[n] = (r, g, b)

    def set_pixel_hsv(self, n, h, s, v):
        """Set a single pixel to RGB colour, with index only counting active sections.
        O(s) where s is the size of active sections"""
        r, g, b = [int(n * 255) for n in colorsys.hsv_to_rgb(h, s, v)]
        self.set_pixel(n, r, g, b)

    def set_pixels(self, pixels):
        """Set active pixels to corresponding pixels in array of rgb tuples with size 'size'"""
        for n in range(0, len(pixels)):
            r, g, b = pixels[n]
            self.set_pixel(n, r, g, b)

    def get_pixels(self):
        return self.pixels

    def set_pixels_hsv(self, pixels):
        """Set active pixels to corresponding pixels in array of hsv tuples with size 'size'"""
        for n in range(0, len(pixels)):
            r, g, b = [int(p * 255) for p in colorsys.hsv_to_rgb(*pixels[n])]
            self.set_pixel(n, r, g, b)

    def set_all_pixels(self, r, g, b):
        """Sets all of the pixels to a color in the RGB colorspace"""
        self.pixels = [(r, g, b)] * self.size

    def set_all_pixels_hsv(self, h, s, v):
        """Sets all of the pixels to a color in the HSV colorspace"""
        r, g, b = [int(p * 255) for p in colorsys.hsv_to_rgb(h, s, v)]
        self.set_all_pixels(r, g, b)

    def render(self):
        """Thread-safe transfer of pixels from controller to 'locations'"""
        for i in range(0, self.size):
            r, g, b = self.pixels[i]
            location = self.pixel_locations[i]
            location[1].section_adapter.set_pixel_color_rgb(location[0], r, g, b)

    def __repr__(self):
        return "Controller: {}".format(self.active_sections)
