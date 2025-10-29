import json
import re
import os

# Load abbreviations from JSON file
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, 'abbrevs.json'), 'r') as f:
    abbrevs = json.load(f)

# Build abbreviation replacements
abbrevs_replacements = []

for key in abbrevs:
    for short in abbrevs[key]:
        abbrevs_replacements.append({
            'short': short,
            'long': key,
        })

def expand(abbrev):
    """Expand a single abbreviation to its full form"""
    for a in abbrevs_replacements:
        abbrev = re.sub(r'^' + a['short'] + r'$', a['long'], abbrev, flags=re.IGNORECASE)
    return abbrev

def parse(content):
    """Parse content and expand abbreviations in function arguments"""
    def replace_abbrev(match):
        prefix = match.group(1)
        arg = match.group(2)
        postfix = match.group(3)
        arg = expand(arg)
        return prefix + arg + postfix
    
    content = re.sub(r"([,\(] *)([A-Za-z ']*?)([,\)])", replace_abbrev, content)
    return content
