class ColorType:
    def __init__(self, module):
        self.name = getattr(module, "name", "Unnamed")
        self.schema = getattr(module, "schema", {})
        self.module = module

    def new_generator(self, args, lights):
        return ColorGenerator(self, args, lights)

    def __str__(self):
        return str({"name": self.name, "schema": self.schema})


class ColorGenerator:
    def __init__(self, color_type, args, lights):
        self.generator_func = color_type.module.get_generator(args)
        self.args = args
        self.color_type = color_type
        self.lights_size = lights.size

    def get_color(self, step=0, position=0):
        return self.generator_func(step, position / self.lights_size)

    def get_palette(self, size):
        if hasattr(self.color_type.module, "get_palette"):
            return self.color_type.module.get_palette(size)
        return [self.get_color(i) for i in range(size)]

    def __str__(self):
        return str({"name": self.color_type.name, "args": self.args})
