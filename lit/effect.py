import itertools
import time

DEFAULT_SPEED = 30  # hertz
EFFECT_IDS = itertools.count(0, 1)


class Effect:
    def __init__(self, module):
        self.name = getattr(module, "name", "Unnamed")
        self.schema = getattr(module, "schema", {})
        self.start_message = getattr(module, "start_message", f"{self.name} started")
        self.command_schema = {
            k: {k2: v2 for k2, v2 in v.items() if k2 != "user_input"}
            for k, v in self.schema.items()
            if v.get("user_input", False)
        }
        self.default_speed = getattr(module, "default_speed", DEFAULT_SPEED)
        self.module = module

    def create(self, args, speed, controller, transaction_id):
        return EffectInstance(self, args, speed, controller, transaction_id)

    def __str__(self):
        return str(
            {
                "name": self.name,
                "schema": self.schema,
                "default_speed": self.default_speed,
            }
        )


class EffectInstance:
    def __init__(self, effect, initial_state, speed, controller, transaction_id):
        self.effect = effect
        self.state = initial_state.copy()
        self.step = 0
        self.speed = speed
        self.next_upd_time = time.time()
        self.id = next(EFFECT_IDS)
        self.controller = controller
        self.transaction_id = transaction_id
        self.static_pixels = []

    def update(self):
        # Speed is in units of updates/second
        if self.speed > 0:
            self.effect.module.update(self.controller, self.step, self.state)
            self.step += 1
            self.next_upd_time += 1 / self.speed
        else:
            if not self.static_pixels:
                self.effect.module.update(self.controller, self.step, self.state)
            self.static_pixels = self.controller.get_pixels()
            self.controller.set_pixels(self.static_pixels)
            self.next_upd_time += 1 / DEFAULT_SPEED


    def __str__(self):
        return str(
            {
                "name": self.effect.name,
                "state": self.state,
                "default_speed": self.speed,
            }
        )
