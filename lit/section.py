import logging

logger = logging.getLogger(__name__)


class Section:
    def __init__(self, name, start_index, size, section_adapter):
        self.name = name
        self.start_index = start_index
        self.size = size
        self.end_index = start_index + size
        self.section_adapter = section_adapter
        self.absolute_range = range(start_index, self.end_index)


class SectionAdapter:
    """ A SectionAdapter represents a Section's view of its display device.
    Each Section has it's own SectionAdapter
    Indexing as relative to the Section
    """

    def __init__(self, offset, display_adapter):
        self.offset = offset
        self.display_adapter = display_adapter

    def set_pixel_color_rgb(self, n, r, g, b):
        self.display_adapter.set_pixel_color_rgb(n + self.offset, r, g, b)
