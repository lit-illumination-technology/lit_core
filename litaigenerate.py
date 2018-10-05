import json
import os
import commands as np

def api_ai_list_format(l):
    return map(lambda x: {'value':x['name'],'synonyms':[x['name']]}, l)

def api_ai_dict_format(d):
    return map(lambda k: {'value':k,'synonyms':[k]}, d.keys())

if not os.path.exists('api-ai'):
    os.mkdir('api-ai')
#API.AI colors
colors = api_ai_list_format(np.get_colors())
color_file = open('api-ai/colors.json', 'w')
color_file.write(json.dumps({'name': 'Colors', 'entries': colors}))

#API.AI effects
effects = api_ai_list_format(np.get_effects())
effects_file = open('api-ai/effects.json', 'w')
effects_file.write(json.dumps({'name': 'Effects', 'entries': effects}))

#API.AI speeds
speeds = api_ai_dict_format(np.get_speeds())
speeds_file = open('api-ai/speeds.json', 'w')
speeds_file.write(json.dumps({'name': 'Speeds', 'entries': speeds}))

#API.AI sections
sections = api_ai_dict_format(dict(np.get_sections(), **np.get_zones()))
sections_file = open('api-ai/ranges.json', 'w')
sections_file.write(json.dumps({'name': 'Ranges', 'entries': sections}))
