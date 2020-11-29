name = "Static Color"
description = "A constant color"
schema = {"color": {"value": {"type": "rgb"}, "user_input": True, "required": True,}}


def get_generator(args):
    def generator(_step, _position):
        return args["color"]

    return generator
