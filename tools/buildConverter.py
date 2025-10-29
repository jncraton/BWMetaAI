import json
import re
import os
import sys

# Add tools directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abbrevs

# Load units from JSON file
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, 'units.json'), 'r') as f:
    units = json.load(f)

def is_unit(unit):
    """Check if the given string is a unit"""
    return any(u['unit'] == unit for u in units)

def get_unit_info(unit):
    """Get information for a specific unit"""
    for u in units:
        if u['unit'] == unit:
            return u
    return None

def parse(content):
    """Parse build orders and convert them to script commands"""
    owned = {}
    supply_from_units = 0
    
    def replace_build(match):
        nonlocal supply_from_units
        supply = int(match.group(1))
        unit = match.group(2)
        
        unit = abbrevs.expand(unit)
        
        if unit not in owned:
            owned[unit] = 0
        owned[unit] += 1
        
        wait_for_worker = int(supply - supply_from_units)
        
        ret = f'build({wait_for_worker}, Peon, 80)\n'
        ret += f'wait_buildstart({wait_for_worker}, Peon)\n'
        
        if is_unit(unit):
            unit_info = get_unit_info(unit)
            # Use int() to match JavaScript's parseInt() behavior which truncates decimals
            supply_from_units += int(float(unit_info['supply']))
            
            ret += f'train({owned[unit]}, {unit})\n'
        elif unit == 'Expand' or unit == 'expand':
            ret += 'expand(1, gen_expansions_expansion)\n'
        else:
            ret += f'build({owned[unit]}, {unit}, 80)\n'
            ret += f'wait_buildstart({owned[unit]}, {unit})\n'
        
        return ret
    
    content = re.sub(r'^(\d+) (.*)$', replace_build, content, flags=re.MULTILINE)
    
    return content
