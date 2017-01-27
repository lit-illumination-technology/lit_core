import controls
from os.path import dirname, abspath, basename, isfile
import  math, sys, getopt, threading, atexit, json, importlib, glob
__author__="Nick Pesce"
__email__="npesce@terpmail.umd.edu"

def start(effect_name, **args): 
    global t
    if not is_effect(effect_name):
        #Modify command
        if effect_name.lower() == 'modify':
            if not history:
                return ("There is no current effect", False)
            current = history.pop()
            print current['args'].get('speed', 50)
            if 'speed' in args:
                if args['speed'] == 'faster':
                    args['speed'] = current['args'].get('speed', 50)+10
                if args['speed'] == 'slower':
                    args['speed'] =  current['args'].get('speed', 50)-10

            current['args'].update(args)
            start(current['effect'], **current['args'])
            return ("Effect modified!", True)
        #Back command
        if effect_name.lower() == 'back':
            history.pop()
            prev = history.pop()
            return start(prev['effect'], **prev['args'])
        #Incorrect effect name
        return (help(), False)
    args = {k:get_value_from_string(k, args[k]) for k in args}
    history.append({'effect' : effect_name.lower(), 'args' : args.copy()})
    if 'speed' in args:
        args['speed'] = 10**((args['speed']-50)/50.0)

    #Stop previous effect
    stop_event.set()
    if t is not None:
        t.join()
    stop_event.clear()

    if 'ranges' in args:
        np.set_ranges(get_sections_from_ranges(args['ranges']))
    else:
        np.set_ranges(get_sections_from_ranges([default_range]))

    args['lights'] = np
    args['stop_event'] = stop_event

    try:
        effect = effects[effect_name.lower()]
        t = threading.Thread(target=effect.start, kwargs=args)
        t.daemon = True
        t.start()
        return (effect.start_string,  True)
    except Exception, e:
        history.pop()
        return (str(e), False)

def help():
    return """Effects:\n    ~ """ + ("\n    ~ ".join(d["name"] + " " + modifiers_to_string(d["modifiers"]) for d in commands))

def modifiers_to_string(modifiers):
    ret = ""
    if(modifiers & SPEED):
        ret += "[-s speed]"
    if(modifiers & COLOR):
        ret += "[-c (r,g,b)]"
    return ret

def get_effects():
    return commands

def get_colors():
    return colors

def get_speeds():
    return speeds 

def get_sections():
    return [k for k in sections]

def get_zones():
    return [k for k in zones]
    
def get_sections_from_ranges(lst):
    """converts ranges names (sections or zones), to a list containing ony section names"""
    ret = []
    for r in lst:
        if r in sections:
            ret.append(r)
        elif r in zones:
            ret += zones[r]
    return ret

def get_value_from_string(type, string):
    """Given a attribute represented as a string, convert it to the appropriate value"""
    if not isinstance(string, basestring):
        return string
    if type.lower() == 'color':
        for c in colors:
            if c['name'].lower() == string.lower():
                return c['color']
        return [255, 255, 255]
    elif type.lower() == 'speed':
        return speeds.get(string.lower(), 50)
    elif type.lower() == 'ranges':
        return string.split(",")
    return string

def combine_colors_in_list(list):
    """Takes a list of strings, and combines adjacent strings that are not known to be speeds"""
    ret = []
    cat = None
    for i in range(0, len(list)):
        if speeds.has_key(list[i].lower()):
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

def is_effect(name):
    return name.lower() in effects

def import_effects():
    files = glob.glob(dirname(abspath(__file__))+'/effects/*.py')
    module_names = [ basename(f)[:-3] for f in files if isfile(f) and basename(f) != '__init__.py' and basename(f) != 'template.py']
    package = __import__('effects', globals(), locals(), module_names, -1)
    modules = []

    for m in module_names:
        modules.append(getattr(package, m))

    for m in modules:
        name = getattr(m, 'name')
        modifiers = getattr(m, 'modifiers')
        effects[name.lower()] = m
        commands.append({'name' : name, 'modifiers' : modifiers})

def _clean_shutdown():
    stop_event.set()
    if t is not None:
        t.join()
    np.off()

if __name__ == "__main__":
    print "This is module can not be run. Import it and call start()"
    sys.exit()

SPEED = 0b10
COLOR = 0b1
t = None
stop_event = threading.Event()
effects = {}
commands = []
sections = {}
zones = {}
default_range = None
history = []

with open('configuration/speeds.json') as data_file:    
    speeds = json.load(data_file)

with open('configuration/colors.json') as data_file:    
    colors = json.load(data_file)

with open('configuration/ranges.json') as data_file:    
    rangeJson = json.load(data_file)
    sectionJson = rangeJson['sections']
    zoneJson = rangeJson['zones']
    default_range = rangeJson['default']
    for k in sectionJson:
        r = sectionJson[k]
        sections[k] = range(r['start'], r['end'])
    for k in zoneJson:
        zones[k] = zoneJson[k]

np = controls.Led_Controller(sections)
np.set_ranges(get_sections_from_ranges(default_range))

import_effects()
atexit.register(_clean_shutdown)
