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
import threading

from . import controls
from . import effects
__author__="Nick Pesce"
__email__="npesce@terpmail.umd.edu"

SPEED = 0b10
COLOR = 0b1
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

        self.np = controls.Led_Controller(led_count=self.config.getint('General','leds') , led_pin=self.config.getint('General', 'pin'), sections=self.sections, virtual_sections=self.virtual_sections)
        self.np.set_sections(self.get_sections_from_ranges(self.default_range))

        self.import_effects()
        atexit.register(self._clean_shutdown)

    def start(self, effect_name, **args): 
        args = {k:v for (k,v) in args.items() if v!=None}
        if not self.is_effect(effect_name):
            #Modify command
            if effect_name.lower() == 'modify':
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
            #Back command
            if effect_name.lower() == 'back':
                if len(self.history) < 2:
                    return ("There are no previous effects!", 1)
                self.history.pop()
                prev = self.history.pop()
                return self.start(prev['effect'], **prev['args'])
            #Incorrect effect name
            return (self.help(), 1)

        args = {k:self.get_value_from_string(k, args[k]) for k in args}
        self.history.append({'effect' : effect_name.lower(), 'args' : args.copy()})
        if 'speed' in args:
            args['speed'] = 10**((args['speed']-50)/50.0)

        #Stop previous effect
        self.stop_event.set()
        if self.t is not None:
            self.t.join()
        self.stop_event.clear()

        if 'ranges' in args:
            self.np.set_sections(self.get_sections_from_ranges(args['ranges']))
        else:
            self.np.set_sections(self.get_sections_from_ranges([self.default_range]))

        args['lights'] = self.np
        args['stop_event'] = self.stop_event

        try:
            effect = self.effects[effect_name.lower()]
            self.t = threading.Thread(target=effect.start, kwargs=args)
            self.t.daemon = True
            self.t.start()
            return (effect.start_string,  0)
        except Exception as e:
            self.history.pop()
            return (str(e), 1)

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
            return self.speeds.get(string.lower(), 50)
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
        #TODO effects -> json with script as string. use exec()
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
        self.stop_event.set()
        if self.t is not None:
            self.t.join()
        self.np.off()

if __name__ == "__main__":
    logger.error("This is module can not be run. Import it and call start()")
    sys.exit()
