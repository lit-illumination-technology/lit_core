import itertools
import time

DEFAULT_SPEED = 50  # hertz
EFFECT_IDS = itertools.count(0, 1)


class Effect:
    def __init__(self, module):
        self.name = getattr(module, "name", "Unnamed")
        self.schema = getattr(module, "schema", {})
        self.start_message = getattr(module, "start_message", "{self.name} started")
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

    def update(self):
        self.effect.module.update(self.controller, self.step, self.state)
        # Speed is in units of updates/second
        # If speed is 0, update at DEFAULT_SPEED, but don't increment step
        self.next_upd_time += 1 / (self.speed or self.effect.default_speed)
        if self.speed > 0:
            self.step += 1

    def __str__(self):
        return str(
            {
                "name": self.effect.name,
                "state": self.state,
                "default_speed": self.speed,
            }
        )
