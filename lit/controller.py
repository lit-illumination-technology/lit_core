import colorsys
import logging

logger = logging.getLogger(__name__)


class ControllerManager:
    def __init__(self, sections):
        """Creates a new Led_Controller Manager.
        sections: The named led sections that can be controlled. 
        """
        self.controllers = []
        self.sections = sections
        self.display_adapters = {
            s.section_adapter.display_adapter for s in self.sections.values()
        }
        self.section_ordered = sorted(
            self.sections, key=lambda e: self.sections[e].end_index
        )
        # Number of leds in all sections
        self.total_leds = sum(s.size for s in self.sections.values())
        # The rendered pixel values to be displayed
        self.pixels = [(0, 0, 0) for _ in range(self.total_leds)]
        # A mapping from absolute index to (local index, controller)
        self.pixel_locations = [None] * self.total_leds
        for section_name in self.section_ordered:
            section = self.sections[section_name]
            for local_i, absolute_i in enumerate(section.absolute_range):
                # TODO named tuple for pixel locations
                self.pixel_locations[absolute_i] = (local_i, section)

    def create_controller(self, sections, overlayed=False, opacity=1):
        """ Creates a new Led_Controller for the specified sections
        If overlayed is False , the sections will be removed from any existing controllers """
        controller = Controller(self, opacity)
        controller.set_sections(sections)
        if not overlayed:
            for c in self.controllers:
                if any(s in sections for s in c.active_section_names):
                    c.set_sections(
                        [s for s in c.active_section_names if s not in sections]
                    )
            # Remove any empty controllers
            self.controllers = [c for c in self.controllers if c.size != 0]
        self.controllers.append(controller)
        return controller

    def remove_controller(self, controller):
        self.controllers.remove(controller)

    def get_controllers(self):
        return self.controllers

    def render(self):
        overlay_pixels = [[] for _ in range(self.total_leds)]
        for controller in self.controllers:
            for abs_i, pixel in controller.abs_pixels():
                r, g, b, a = pixel

                overlay_pixels[abs_i].append((r, g, b, a * controller.opacity))
        for i, overlays in enumerate(overlay_pixels):
            r, g, b, a = 0, 0, 0, 0
            for pixel in overlays:
                if pixel[3] < 0:
                    a = -1
                    r = pixel[0]
                    g = pixel[1]
                    b = pixel[2]
                    break
                else:
                    a += pixel[3]
                    r += pixel[0] * pixel[3]
                    g += pixel[1] * pixel[3]
                    b += pixel[2] * pixel[3]
            if a < 0:
                self.pixels[i] = (r, g, b)
            elif a == 0:
                self.pixels[i] = (0, 0, 0)
            else:
                self.pixels[i] = (int(r // a), int(g // a), int(b // a))
            location = self.pixel_locations[i]
            location[1].section_adapter.set_pixel_color_rgb(
                location[0], *self.pixels[i]
            )

    def show(self, show_lock):
        """Pushes the led array to the actual lights"""
        with show_lock:
            self.render()
        for display_adapter in self.display_adapters:
            display_adapter.show()

    def get_pixels(self):
        """ Returns the list of rgb values as of the last 'show' call """
        return self.pixels

    def __str__(self):
        return "Controller Manager: {}".format(self.controllers)


class Controller:
    """ A grouping of sections that are being controlled as one unit """

    def __init__(self, manager, opacity):
        """Creates a new Led_Controller with no active ranges"""
        self.sections = manager.sections
        self.section_ordered = sorted(
            self.sections, key=lambda e: self.sections[e].end_index
        )
        # Currently active section names sorted by end location
        self.active_section_names = []
        # Number of currently active leds
        self.size = 0
        self.opacity = opacity

    def set_sections(self, new_sections):
        """Sets the currently active sections to new_sections and updates other dependent fields.
        new_sections is a list of section names corresponding to the sections dict keys"""
        self.active_section_names = sorted(
            new_sections, key=lambda e: self.sections[e].end_index
        )
        self.size = sum(self.sections[r].size for r in self.active_section_names)
        self.pixels = [(0, 0, 0, 0)] * self.size

    def abs_pixels(self):
        controller_i = 0
        for sn in self.active_section_names:
            s = self.sections[sn]
            for abs_i in s.absolute_range:
                yield abs_i, self.pixels[controller_i]
                controller_i += 1

    def get_sections(self):
        """Returns a list of currently active sections"""
        return [self.sections[k] for k in self.active_section_names]

    def clear(self):
        """Clear the currently active buffer"""
        self.set_all_pixels(0, 0, 0, 0)

    def off(self):
        """ Turns off all pixels. """
        self.clear()

    def set_pixel(self, n, r, g, b, a=1):
        """Set a single pixel to RGB colour, with index only counting active sections for this controller"""
        self.pixels[n] = (r, g, b, a)

    def set_pixel_hsv(self, n, h, s, v, a=1):
        """Set a single pixel to RGB colour, with index only counting active sections.
        O(s) where s is the size of active sections"""
        r, g, b = [int(n * 255) for n in colorsys.hsv_to_rgb(h, s, v)]
        self.set_pixel(n, r, g, b, a)

    def set_pixels(self, pixels):
        """Set active pixels to corresponding pixels in array of rgb tuples with size 'size'"""
        for n in range(0, len(pixels)):
            if len(pixels[n]) == 4:
                r, g, b, a = pixels[n]
                self.set_pixel(n, r, g, b, a)
            else:
                r, g, b = pixels[n]
                self.set_pixel(n, r, g, b)

    def get_pixels(self):
        return self.pixels

    def set_pixels_hsv(self, pixels):
        """Set active pixels to corresponding pixels in array of hsv tuples with size 'size'"""
        for n in range(0, len(pixels)):
            r, g, b = [int(p * 255) for p in colorsys.hsv_to_rgb(*pixels[n][:3])]
            if len(pixels[n]) == 4:
                self.set_pixel(n, r, g, b, pixels[n][3])
            else:
                self.set_pixel(n, r, g, b)

    def set_all_pixels(self, r, g, b, a=1):
        """Sets all of the pixels to a color in the RGB colorspace"""
        self.pixels = [(r, g, b, a)] * self.size

    def set_all_pixels_hsv(self, h, s, v, a=1):
        """Sets all of the pixels to a color in the HSV colorspace"""
        r, g, b = [int(p * 255) for p in colorsys.hsv_to_rgb(h, s, v)]
        self.set_all_pixels(r, g, b, a)

    def __repr__(self):
        return "Controller: sections={} opacity={}".format(
            self.active_section_names, self.opacity
        )
