import atexit
import colorsys
import importlib
import json
import logging
import os
import random
import sys
import time
import threading

from .controller import ControllerManager
from .error import InvalidEffectException
from .section import Section, SectionAdapter
from .device import DeviceAdapter
from . import effects
from .history import History
from .effect import Effect

__author__ = "Nick Pesce"
__email__ = "nickpesce22@gmail.com"

FPS = 40
SPEED = 0b10
COLOR = 0b1
MAX_SHOW_SPEED = 60  # hertz
TIME_WARN_COOLDOWN = 10  # seconds
logger = logging.getLogger(__name__)


class commands:
    def __init__(self, base_path):
        self.base_path = base_path
        self.config_path = os.path.join(base_path, "config")
        logger.info("Using config directory: %s", self.config_path)
        self.sleep_event = threading.Event()

        self.effects = {}
        self.effects_by_id = {}
        self.transactions = {}
        self.sections = {}
        self.zones = {}
        self.default_range = None
        self.singleton_args = {}
        self.history = History(self)

        # Load config files
        with open(os.path.join(self.config_path, "speeds.json")) as data_file:
            self.speeds = json.load(data_file)

        with open(os.path.join(self.config_path, "presets.json")) as data_file:
            self.presets = json.load(data_file)

        with open(os.path.join(self.config_path, "colors.json")) as data_file:
            self.colors = json.load(data_file)

        with open(os.path.join(self.config_path, "ranges.json")) as data_file:
            range_json = json.load(data_file)
            section_json = range_json["sections"]
            adapters_json = range_json["adapters"]
            zone_json = range_json["zones"]
            self.default_range = range_json["default"]

            devices = {}
            for adapter in adapters_json:
                name = adapter["name"]
                if name in devices:
                    raise SyntaxError(
                        "Adapter name {name} was defined more than once. "
                        "Adapter names must be unique.".format(name=name)
                    )
                devices[name] = {
                    "adapter": DeviceAdapter.from_config(adapter),
                    "used_indexes": 0,
                }

            section_start_index = 0
            for section in section_json:
                device = devices.get(section["adapter"])
                if not device:
                    raise SyntaxError(
                        "Error in ranges.json: Section '{section}' references "
                        "adapter '{adapter}', but that adapter is not defined".format(
                            section=section["name"], adapter=section["adapter"]
                        )
                    )
                next_used_indexes = device["used_indexes"] + section["size"]
                if next_used_indexes > device["adapter"].size:
                    raise SyntaxError(
                        "Adapter '{name}' has {size} pixels available (adapter size), "
                        "but at least {used} were used by sections".format(
                            name=device["adapter"].name,
                            size=device["adapter"].size,
                            used=next_used_indexes,
                        )
                    )
                section_adapter = SectionAdapter(
                    device["used_indexes"], device["adapter"]
                )
                self.sections[section["name"]] = Section(
                    section["name"],
                    section_start_index,
                    section["size"],
                    section_adapter,
                )
                section_start_index += section["size"]
                device["used_indexes"] = next_used_indexes

            for zone in zone_json:
                self.zones[zone["name"]] = zone["sections"]

        self.controller_manager = ControllerManager(self.sections)
        self.import_effects()
        atexit.register(self._clean_shutdown)
        self.start_loop()
        logger.info("Started effect loop")

    def start_loop(self):
        self.should_run = True
        self.show_lock = threading.Lock()

        def loop(self):
            total_steps = 0
            last_warn_time = 0
            while self.should_run:
                next_upd_time = float("inf")
                start_time = time.time()
                try:
                    with self.show_lock:
                        for effect in self.effects_by_id.values():
                            if effect.next_upd_time <= start_time:
                                start_upd = time.time()
                                try:
                                    effect.update()
                                except Exception:
                                    logger.exception(
                                        'Error in effect "%s"', effect.effect.name
                                    )
                                end_upd = time.time()
                                logger.debug(
                                    "Took %dms to update %s",
                                    (end_upd - start_upd) * 1000,
                                    str(effect),
                                )
                                next_upd_time = min(next_upd_time, effect.next_upd_time)

                    if next_upd_time == float("inf"):
                        continue
                    wait_time = next_upd_time - time.time()
                    if wait_time < 0:
                        if last_warn_time < time.time() - TIME_WARN_COOLDOWN:
                            logger.warning(
                                "Can't keep up! Did the system time change, "
                                "or is the server overloaded? Running %d ms behind.",
                                (wait_time * -1000),
                            )
                            logger.debug(
                                "Behind while running effect(s) %s",
                                str(self.effects_by_id.values()),
                            )
                            last_warn_time = time.time()
                    else:
                        self.sleep_event.wait(wait_time)
                    total_steps += 1
                except Exception as e:
                    if self.show_lock.locked():
                        self.show_lock.release()
                    logger.exception("Error in effect loop")

        def show_loop(self):
            start_time = time.time()
            while self.should_run:
                try:
                    self.controller_manager.show(self.show_lock)
                    end_time = time.time()
                    show_time = end_time - start_time
                    logger.debug("Show took %dms", show_time * 1000)
                    wait_time = max(0, (1 / MAX_SHOW_SPEED) - show_time)
                    self.sleep_event.wait(wait_time)
                    start_time = end_time
                except Exception:
                    logger.exception("Error in show loop")
                    if self.show_lock.locked():
                        self.show_lock.release()

        self.show_thread = threading.Thread(target=show_loop, args=(self,))
        self.show_thread.start()
        self.loop_thread = threading.Thread(target=loop, args=(self,))
        self.loop_thread.start()

    def stop_loop(self):
        self.sleep_event.set()
        self.should_run = False
        self.loop_thread.join()
        self.show_thread.join()

    def start_preset(self, preset_name, properties, transaction_id):
        preset = self.presets.get(preset_name, None)
        if not preset:
            msg = "The preset {} does not exist".format(preset_name)
            return Response(msg, 2)
        if "commands" not in preset:
            msg = "The preset {} does not specify commands".format(preset_name)
            return Response(msg, 3)
        for command in preset["commands"]:
            if "effect" not in command:
                msg = "The preset {} must specify an effect for all commands".format(
                    preset_name
                )
                return Response(msg, 3)
            effect_instance = self._start_effect(
                command["effect"],
                command.get("args", {}),
                command.get("properties", {}),
                transaction_id,
            )
            if not effect_instance:
                return Response("Invalid effect: {}".format(command["effect"]), 1)
        self.history.save(self.get_state())
        return Response(
            preset.get("start_message", "{} started!".format(preset_name)),
            0,
            transaction_id,
        )

    def start_effect(self, effect_name, args, properties, transaction_id):
        if not self.is_effect(effect_name):
            raise InvalidEffectException()
        effect_instance = self._start_effect(
            effect_name, args, properties, transaction_id
        )
        self.history.save(self.get_state())
        return Response(effect_instance.effect.start_message, 0, transaction_id)

    def _start_effect(self, effect_name, args, properties, transaction_id):
        if not self.is_effect(effect_name):
            return None
        effect = self.effects[effect_name.lower()]
        # remove any 'None' args
        args = {k: v for (k, v) in args.items() if v is not None}
        # attempt to parse arg values
        args = {k: self.get_value_from_string(k, args[k]) for k in args}
        sections = self.get_sections_from_ranges(
            properties.get("ranges", [self.default_range])
        )
        self.show_lock.acquire()
        opacity = properties.get("opacity", 1)
        if not isinstance(opacity, (int, float)):
            logger.warning("Invalid 'opacity' property received: %s", str(opacity))
            opacity = 1
        overlayed = properties.get("overlayed", False)
        if not isinstance(overlayed, bool):
            logger.warning("Invalid 'overlayed' property received: %s", str(overlayed))
            overlayed = False
        controller = self.controller_manager.create_controller(
            sections, overlayed=overlayed, opacity=opacity
        )
        self.effects_by_id = {
            effect_id: effect
            for effect_id, effect in self.effects_by_id.items()
            if effect.controller.size > 0
        }

        # fill in default args from schema
        schema = effect.schema
        self.complete_args_with_schema(args, schema, controller)

        default_speed = effect.default_speed
        speed = properties.get("speed", default_speed)
        effect_instance = effect.create(args, speed, controller, transaction_id)
        self.transactions.setdefault(transaction_id, []).append(effect_instance.id)
        self.effects_by_id[effect_instance.id] = effect_instance
        self.show_lock.release()
        self.sleep_event.set()
        logger.info("New controller manager: %s", str(self.controller_manager))
        return effect_instance

    def get_transaction(self, transaction_id):
        return self.transactions.get(transaction_id)

    def stop_all(self):
        effect_ids = [effect_id for effect_id in self.effects_by_id]
        for effect_id in effect_ids:
            self.stop_effect(effect_id)

    def stop_effect(self, effect_id):
        effect = self.effects_by_id.get(effect_id)
        if effect:
            self.controller_manager.remove_controller(effect.controller)
            del self.effects_by_id[effect_id]
            return True
        return False

    def complete_args_with_schema(self, args, schema, controller):
        for k, v in sorted(
            schema.items(), key=lambda x: x[1].get("index", float("inf"))
        ):
            if (not k in args or not v.get("user_input", False)) and (
                "default" in v["value"] or "default_gen" in v["value"]
            ):
                # If this arg is a singleton that was already set, give a reference
                if v.get("singleton", False) and k in self.singleton_args:
                    args[k] = self.singleton_args[k]
                # Otherwise, get the default value
                else:
                    if "default_gen" in v["value"]:
                        args[k] = v["value"]["default_gen"](controller, args)
                    else:
                        args[k] = v["value"]["default"]
                    if v.get("singleton", False):
                        self.singleton_args[k] = args[k]

    def help(self):
        return """Effects:\n    ~ """ + (
            "\n    ~ ".join(
                effect.name + " " + self.schema_to_string(effect.command_schema)
                for effect in self.effects.values()
            )
        )

    def schema_to_string(self, schema):
        ret = str(schema)
        # ret = ""
        # if(& SPEED):
        #    ret += "[-s speed]"
        # if(modifiers & COLOR):
        #    ret += "[-c (r,g,b)]"
        return ret

    def get_effects(self):
        return [
            {
                "name": effect.name,
                "schema": effect.command_schema,
                "default_speed": effect.default_speed,
            }
            for effect in self.effects.values()
        ]

    def get_presets(self):
        return self.presets

    def get_colors(self):
        return self.colors

    def get_speeds(self):
        return self.speeds

    def get_sections(self):
        return self.sections

    def get_zones(self):
        return self.zones

    def get_pixels(self):
        return self.controller_manager.get_pixels()

    def get_state(self):
        state = []

        def state_schema(state, schema):
            return {k: v for k, v in state.items() if k in schema}

        for effect in self.effects_by_id.values():
            controller = effect.controller
            state.append(
                {
                    "sections": controller.active_section_names,
                    "opacity": controller.opacity,
                    "effect_name": effect.effect.name,
                    "effect_state": state_schema(
                        effect.state, effect.effect.command_schema
                    ),
                    "effect_id": effect.id,
                    "transaction_id": effect.transaction_id,
                }
            )
        return state

    def get_sections_from_ranges(self, lst):
        """converts ranges names (sections or zones), to a list containing ony section names"""
        ret = []
        for r in lst:
            if r in self.sections:
                ret.append(r)
            elif r in self.zones:
                ret += self.zones[r]
        return ret

    def get_value_from_string(self, type, string):
        """Given a attribute represented as a string, convert it to the appropriate value"""
        if not isinstance(string, str):
            return string
        if type.lower() == "color":
            if string.lower() == "random":
                return list(
                    map(
                        lambda x: int(255 * x),
                        colorsys.hsv_to_rgb(random.random(), 1, 1),
                    )
                )
            for c in self.colors:
                if c["name"].lower() == string.lower():
                    return c["rgb"]
            # TODO throw invalid color name error
            return [255, 255, 255]
        elif type.lower() == "speed":
            return self.speeds.get(string.lower())
        elif type.lower() == "ranges":
            if string.lower() == "all":
                return self.sections.keys()
            return string.split(",")
        return string

    def is_effect(self, name):
        return name.lower() in self.effects

    def import_effects(self):
        module_names = effects.effects
        modules = []
        for m in module_names:
            try:
                module = importlib.import_module(m)
                modules.append(module)
            except Exception as e:
                logger.exception("Could not import %s", m)

        logger.info("Parsing effects")
        for module in modules:
            try:
                logger.info("loading %s", str(module))
                effect = Effect(module)
                self.effects[effect.name.lower()] = effect
            except Exception as e:
                logger.exception("Error loading effect %s", str(module))

    def _clean_shutdown(self):
        logger.info("Shutting down")
        self.stop_loop()
        for controller in self.controller_manager.get_controllers():
            controller.clear()
        self.controller_manager.show(self.show_lock)


class Response:
    def __init__(self, message, rc, transaction_id=None):
        self.message = message
        self.rc = rc
        self.transaction_id = transaction_id

    def as_dict(self):
        return {
            "message": self.message,
            "code": self.rc,
            "transaction_id": self.transaction_id,
        }


if __name__ == "__main__":
    logger.error("This is module can not be run. Import it and call start()")
    sys.exit()
