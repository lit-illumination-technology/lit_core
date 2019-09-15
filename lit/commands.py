import atexit
import configparser
import colorsys
import getopt
import importlib
import json
import logging
import math
import os
import random
import sys
import time
import threading

from . import controls
from . import effects
__author__="Nick Pesce"
__email__="nickpesce22@gmail.com"

FPS = 40
SPEED = 0b10
COLOR = 0b1
DEFAULT_SPEED = 50 # hertz
TIME_WARN_COOLDOWN = 10 # seconds
logger = logging.getLogger(__name__)

class commands:
    def __init__(self, base_path):
        self.base_path = base_path
        self.config_path = os.path.join(base_path, 'config')
        logger.info('Using config directory: {}'.format(self.config_path))
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(self.config_path, 'config.ini')) 
        self.t = None
        self.stop_event = threading.Event()
        self.effects = {}
        self.commands = {}
        self.sections = {}
        self.virtual_sections = {}
        self.zones = {}
        self.default_range = None
        self.history = []
        self.singleton_args = {}

        # Load config files
        with open(os.path.join(self.config_path, 'speeds.json')) as data_file:    
            self.speeds = json.load(data_file)

        with open(os.path.join(self.config_path, 'presets.json')) as data_file:    
            self.presets = json.load(data_file)

        with open(os.path.join(self.config_path, 'colors.json')) as data_file:    
            self.colors = json.load(data_file)

        with open(os.path.join(self.config_path, 'ranges.json')) as data_file:    
            rangeJson = json.load(data_file)
            sectionJson = rangeJson['sections']
            zoneJson = rangeJson['zones']
            virtualSectionJson = rangeJson['virtual_sections']
            self.default_range = rangeJson['default']
            for k in sectionJson:
                r = sectionJson[k]
                self.sections[k] = range(r['start'], r['end'])
            for k in zoneJson:
                self.zones[k] = zoneJson[k]
            for k in virtualSectionJson:
                v = virtualSectionJson[k]
                self.virtual_sections[k] = controls.Virtual_Range(v['num_pixels'], v['ip'], v['port'])

        self.controller_manager = controls.Led_Controller_Manager(led_count=self.config.getint('General','leds') , led_pin=self.config.getint('General', 'pin'), sections=self.sections, virtual_sections=self.virtual_sections)
        initial_controller = self.controller_manager.create_controller(self.sections.keys())

        self.import_effects()
        self.controller_effects = {initial_controller: self.create_effect(self.effects['off'], {}, DEFAULT_SPEED)}
        atexit.register(self._clean_shutdown)
        self.start_loop()
        logger.info('Started effect loop')


    def start_loop(self):
        self.stop_event.clear()
        def loop(self):
            total_steps = 0
            next_show = time.time()
            next_upd_time = time.time()
            last_warn_time = 0
            while not self.stop_event.is_set():
                start_time = time.time()
                try:
                    for controller, effect in self.controller_effects.items():
                        if effect['next_upd_time'] <= start_time:
                            su = time.time()
                            try:
                                effect['effect'].update(controller, effect['step'], effect['state'])
                            except Exception as e:
                                logger.error('Error in effect "{}": {}'.format(getattr(effect['effect'], 'name', 'NONAME'), e))
                            eu = time.time()
                            logger.debug("Took {}ms to update {}".format((eu - su)*1000, effect))
                            # Speed is in units of updates/second
                            # If speed is 0, update at DEFAULT_SPEED, but don't increment step
                            effect['next_upd_time'] += 1/(effect['speed'] or DEFAULT_SPEED)
                            next_upd_time = min(next_upd_time, effect['next_upd_time'])
                            if effect['speed'] > 0:
                                effect['step'] += 1
                    end = time.time()
                    took = (end - start_time)
                    d = next_upd_time - time.time()
                    if d < 0 and last_warn_time > time.time() + TIME_WARN_COOLDOWN:
                        logger.warning("Can't keep up! Did the system time change, or is the server overloaded? Running {} ms behind.".format(d*-1000))
                        logger.debug("Behind while running effect(s) {}".format(self.controller_effects.values()))
                        last_warn_time = time.time()
                    else:
                        self.stop_event.wait(d)
                    total_steps += 1
                except Exception as e:
                    logger.error(e)

        def show_loop(self):
            start_time = time.time()
            while not self.stop_event.is_set():
                try:
                    self.controller_manager.show()
                    end_time = time.time()
                    logger.debug('Show took {}ms'.format((end_time - start_time)*1000))
                    start_time = end_time
                except Exception as e:
                    logger.error('Error in show loop: {}'.format(e))
        threading.Thread(target=show_loop, args=(self,)).start()
        self.loop_thread = threading.Thread(target=loop, args=(self,))
        self.loop_thread.start()
    
    def stop_loop(self):
        self.stop_event.set()
        self.loop_thread.join()

    def start_preset(self, preset_name):
        preset = self.presets.get(preset_name, None) 
        if not preset:
            msg = "The preset {} does not exist".format(preset_name)
            return (msg, 2)
        if "commands" not in preset:
            msg = "The preset {} does not specify commands".format(preset_name)
            return (msg, 3)
        for command in preset["commands"]:
            if "effect" not in command:
                msg = "The preset {} must specify an effect for all commands".format(preset_name)
                return (msg, 3)
            result, rc = self.start_effect(command["effect"], command.get("args", {}))
            if rc != 0:
                self.start_effect("off")
                return (result, rc)
        return (preset.get("start_string", "{} started!".format(preset_name)), 0)

    def start_effect(self, effect_name, args): 
        effect_name = effect_name.lower()
        if effect_name not in self.effects:
            return (self.help(), 2)
        effect = self.effects[effect_name.lower()]
        # remove any 'None' args
        args = {k:v for (k,v) in args.items() if v!=None}
        # attempt to parse arg values
        args = {k:self.get_value_from_string(k, args[k]) for k in args}
        sections = self.get_sections_from_ranges(args.get('ranges', [self.default_range]))
        controller = self.controller_manager.create_controller(sections)
        # fill in default args from schema
        schema = getattr(effect, 'schema', {})
        self.complete_args_with_schema(args, schema, controller)

        self.history.append({'effect' : effect_name.lower(), 'state' : args.copy()})

        speed = args.get('speed', DEFAULT_SPEED)
        self.controller_effects[controller] = self.create_effect(effect, args, speed)
        # Remove empty controllers
        self.controller_effects = {c:self.controller_effects[c] for c in self.controller_effects if c.num_leds != 0}
        return (effect.start_string,  0)

    def complete_args_with_schema(self, args, schema, controller):
        for k, v in sorted(schema.items(), key=lambda x: x[1].get('index', float('inf'))):
            if ((not k in args or not v.get('user_input', False)) and 
                ('default' in v['value'] or 'default_gen' in v['value'])):
                # If this arg is a singleton that was already set, give a reference
                if v.get('singleton', False) and k in self.singleton_args:
                    args[k] = self.singleton_args[k]
                # Otherwise, get the default value
                else:
                    if 'default_gen' in v['value']:
                        args[k] = v['value']['default_gen'](controller, args)
                    else:
                        args[k] = v['value']['default']
                    if v.get('singleton', False):
                        self.singleton_args[k] = args[k]

    def create_effect(self, effect, state, speed):
        return {'effect': effect, 'state': state.copy(), 'step': 0, 'speed': speed, 'next_upd_time': time.time()}

    def modify(self, range):
        #Modify command
        if not history:
            return ("There is no current effect", 1)
        current = self.history.pop()
        if 'speed' in args:
            if args['speed'] == 'faster':
                args['speed'] = current['state'].get('speed', 50)+10
            if args['speed'] == 'slower':
                args['speed'] =  current['state'].get('speed', 50)-10

        current['state'].update(args)
        self.start(current['effect'], current['state'])
        return ("Effect modified!", 0)

    def back(self, range):
        #Back command
        if len(self.history) < 2:
            return ("There are no previous effects!", 1)
        self.history.pop()
        prev = self.history.pop()
        return self.start(prev['effect'], prev['state'])

    def help(self):
        return """Effects:\n    ~ """ + ("\n    ~ ".join(name + " " + self.schema_to_string(schema) for name, schema in self.commands))

    def schema_to_string(self, schema):
        ret = str(schema)
        #ret = ""
        #if(& SPEED):
        #    ret += "[-s speed]"
        #if(modifiers & COLOR):
        #    ret += "[-c (r,g,b)]"
        return ret

    def get_effects(self):
        return [{'name': n, 'schema': s} for n, s in self.commands.items()]

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
            return {k:v for k, v in state.items() if k in schema}
                 
        for c, e in self.controller_effects.items():
            effect_name = getattr(e['effect'], 'name', 'Unnamed')
            state.append({
                'sections': c.active_sections, 
                'effect_name': effect_name,
                'effect_state': state_schema(e['state'], self.commands[effect_name])
            })
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
        if type.lower() == 'color':
            if string.lower() == 'random':
                return list(map(lambda x: int(255*x), colorsys.hsv_to_rgb(random.random(), 1, 1)))
            for c in self.colors:
                if c['name'].lower() == string.lower():
                    return c['color']
            # TODO throw invalid color name error
            return [255, 255, 255]
        elif type.lower() == 'speed':
            return self.speeds.get(string.lower(), DEFAULT_SPEED)
        elif type.lower() == 'ranges':
            if string.lower() == 'all':
                return self.sections.keys()
            return string.split(",")
        return string

    def combine_colors_in_list(self, list):
        """Takes a list of strings, and combines adjacent strings that are not known to be speeds"""
        ret = []
        cat = None
        for i in range(0, len(list)):
            if self.speeds.has_key(list[i].lower()):
                if not cat is None:
                    ret.append(cat)
                    cat = None
                ret.append(list[i].lower())
            else:
                if cat is None:
                    cat = list[i].lower()
                else:
                    cat += " " + list[i].lower()
        if not cat is None:
            ret.append(cat)
        return ret

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
                logger.error("Could not import {} because {}".format(m, e))

        logger.info('Parsing effects')
        for m in modules:
            try:
                logger.info("loading {}".format(str(m)))
                name = getattr(m, 'name', 'Unnamed')
                schema= getattr(m, 'schema', {})
                command_schema = {k: {k2: v2 for k2, v2 in v.items() if k2 != 'user_input'} 
                        for k, v in schema.items() if v.get('user_input', False)}
                self.effects[name.lower()] = m
                self.commands[name] = command_schema
            except Exception as e:
                logger.error('Error loading effect {}. {}'.format(str(m), e))

    def _clean_shutdown(self):
        logger.info('Shutting down')
        self.stop_loop()
        for c in self.controller_manager.get_controllers():
            c.clear()
        self.controller_manager.show()

if __name__ == "__main__":
    logger.error("This is module can not be run. Import it and call start()")
    sys.exit()

