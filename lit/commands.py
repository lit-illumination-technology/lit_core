import atexit
import configparser
import getopt
import glob
import importlib
import json
import logging
import math
import os
import sys
import time
import threading

from . import controls
from . import effects
__author__="Nick Pesce"
__email__="nickpesce22@gmail.com"

SPEED = 0b10
COLOR = 0b1
DEFAULT_SPEED = 50
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
BASE_CONFIG = os.path.join(BASE_PATH, 'config')
logger = logging.getLogger(__name__)

class commands:
    def __init__(self, base_path=None):
        self.base_path = base_path
        self.config_path = os.path.join(base_path, 'config') if base_path else None
        logger.info('Using config directories: {}'.format(', '.join(filter(None, [BASE_CONFIG, self.config_path]))))
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(self.config_path or BASE_CONFIG, 'config.ini')) 
        self.t = None
        self.stop_event = threading.Event()
        self.effects = {}
        self.commands = []
        self.sections = {}
        self.virtual_sections = {}
        self.zones = {}
        self.default_range = None
        self.history = []

        # Load config files
        with open(os.path.join(self.config_path or BASE_CONFIG, 'speeds.json')) as data_file:    
            self.speeds = json.load(data_file)

        with open(os.path.join(self.config_path or BASE_CONFIG, 'colors.json')) as data_file:    
            self.colors = json.load(data_file)

        with open(os.path.join(self.config_path or BASE_CONFIG, 'ranges.json')) as data_file:    
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
        self.controller_effects = {initial_controller:{'effect': self.effects['off'], 'args': {}, 'speed': DEFAULT_SPEED, 'step': 0}}
        atexit.register(self._clean_shutdown)
        self.start_loop()

    def start_loop(self):
        self.stop_event.clear()
        def loop(self):
            total_steps = 0
            while not self.stop_event.is_set():
                try:
                    # Remove empty controllers
                    self.controller_effects = {c:self.controller_effects[c] for c in self.controller_effects if c.num_leds != 0}
                    for controller, effect in self.controller_effects.items():
                        if total_steps % (101-effect['speed']) == 0:
                            effect['effect'].update(controller, effect['step'], **effect['args'])
                            effect['step'] += 1
                            controller.show()
                    self.stop_event.wait(1/100) #TODO time 100/sec
                    total_steps += 1
                except Exception as e:
                    logger.error(e)
        self.loop_thread = threading.Thread(target=loop, args=(self,))
        self.loop_thread.start()
    
    def stop_loop(self):
        self.stop_event.set()
        self.loop_thread.join()

    def start_effect(self, effect_name, **args): 
        effect_name = effect_name.lower()
        if effect_name not in self.effects:
            return (self.help(), 2)
        # remove any 'None' args
        args = {k:v for (k,v) in args.items() if v!=None}
        # attempt to parse arg values
        args = {k:self.get_value_from_string(k, args[k]) for k in args}
        self.history.append({'effect' : effect_name.lower(), 'args' : args.copy()})

        sections = self.get_sections_from_ranges(args.get('ranges', [self.default_range]))

        controller = self.controller_manager.create_controller(sections)

        effect = self.effects[effect_name.lower()]
        self.controller_effects[controller] = {'effect': effect, 'args': args.copy(), 'step': 0, 'speed': args.get('speed', DEFAULT_SPEED)}
        return (effect.start_string,  0)

    def modify(self, range):
        #Modify command
        if not history:
            return ("There is no current effect", 1)
        current = self.history.pop()
        if 'speed' in args:
            if args['speed'] == 'faster':
                args['speed'] = current['args'].get('speed', 50)+10
            if args['speed'] == 'slower':
                args['speed'] =  current['args'].get('speed', 50)-10

        current['args'].update(args)
        self.start(current['effect'], **current['args'])
        return ("Effect modified!", 0)

    def back(self, range):
        #Back command
        if len(self.history) < 2:
            return ("There are no previous effects!", 1)
        self.history.pop()
        prev = self.history.pop()
        return self.start(prev['effect'], **prev['args'])

    def help(self):
        return """Effects:\n    ~ """ + ("\n    ~ ".join(d["name"] + " " + self.modifiers_to_string(d["modifiers"]) for d in self.commands))

    def modifiers_to_string(self, modifiers):
        ret = ""
        if(modifiers & SPEED):
            ret += "[-s speed]"
        if(modifiers & COLOR):
            ret += "[-c (r,g,b)]"
        return ret

    def get_effects(self):
        return self.commands

    def get_colors(self):
        return self.colors

    def get_speeds(self):
        return self.speeds 

    def get_sections(self):
        return self.sections

    def get_zones(self):
        return self.zones
        
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
            for c in self.colors:
                if c['name'].lower() == string.lower():
                    return c['color']
            return [255, 255, 255]
        elif type.lower() == 'speed':
            return self.speeds.get(string.lower(), DEFAULT_SPEED)
        elif type.lower() == 'ranges':
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
        files = glob.glob(os.path.join(BASE_PATH, 'effects', '*.py'))
        #if self.base_path:
        #    files += glob.glob(os.path.join(self.base_path, 'effects', '*.py'))
        ignored = ['__init__', 'template']
        module_names = [m for m in effects.__all__ if m not in ignored]
        modules = []
        for m in module_names:
            try:
                module = importlib.import_module('lit.effects.{}'.format(m))
                modules.append(module)
            except Exception as e:
                print("Could not import {} because {}".format(m, e))

        for m in modules:
            name = getattr(m, 'name')
            modifiers = getattr(m, 'modifiers')
            self.effects[name.lower()] = m
            self.commands.append({'name' : name, 'modifiers' : modifiers})

    def _clean_shutdown(self):
        logger.info('Shutting down')
        self.stop_loop()
        for c in self.controller_manager.get_controllers():
            c.off()

if __name__ == "__main__":
    logger.error("This is module can not be run. Import it and call start()")
    sys.exit()

