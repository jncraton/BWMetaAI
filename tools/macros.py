import json
import re
import os

# Load config
script_dir = os.path.dirname(os.path.abspath(__file__))

block_counter = 0

def next_block_name():
    """Generate next unique block name"""
    global block_counter
    block_counter += 1
    return f'gen_macro_{block_counter}'

def expand_enemy_owns(units, block):
    """Expand enemy owns check for multiple units"""
    out = ""
    for unit in units:
        out += f'enemyowns_jump({unit}, {block})\n'
    return out

def parse(content):
    """Parse content and expand macros"""
    global block_counter
    
    # Load config if it exists
    config = {}
    config_path = os.path.join(script_dir, 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    
    lines = re.split(r'[\r\n]+', content)
    result = ''
    indent_level = 0
    blocks = []
    
    for line in lines:
        if indent_level > 0:
            for i in range(indent_level, 0, -1):
                if '    ' in line:
                    line = line.replace('    ', '', 1)
                else:
                    indent_level -= 1
                    result += blocks.pop()
        
        if 'if ' in line:
            def replace_if(match):
                function_name = match.group(1)
                params = match.group(2)
                if function_name == 'owned':
                    return f'if_owned({params})'
                elif function_name == 'townpoint':
                    return f'try_townpoint({params})'
                else:
                    return f'{function_name}_jump({params})'
            
            line = re.sub(r'if (.*)\((.*)\)', replace_if, line)
        
        if ':' in line:
            start_block = next_block_name()
            end_block = next_block_name()
            
            if 'multirun_loop' in line:
                line = line.replace('multirun_loop', 'multirun()')
                blocks.append(f'wait(75)\ngoto({start_block})\n--{end_block}--\n')
            elif 'multirun' in line:
                line = line.replace('multirun', 'multirun()')
                blocks.append(f'stop()\n--{end_block}--\n')
            elif 'loop' in line:
                line = line.replace('loop', 'goto()')
                blocks.append(f'wait(75)\ngoto({start_block})\n--{end_block}--\n')
            else:
                blocks.append(f'--{end_block}--\n')
            
            indent_level += 1
            line = line.replace(':', '')
            if re.search(r'[a-zA-Z0-9]\)', line):
                line = re.sub(r'\)', f', {start_block})', line)
            else:
                line = re.sub(r'\)', f'{start_block})', line)
            result += line + '\n'
            result += f'goto({end_block})\n'
            result += f'--{start_block}--\n'
        else:
            result += line + '\n'
    
    while blocks:
        result += blocks.pop()
    
    # attack_async
    def replace_attack_async(match):
        start = next_block_name()
        escape = next_block_name()
        
        return (f'multirun({start})\n'
                f'goto({escape})\n'
                f'--{start}--\n'
                f'attack_do()\n'
                f'attack_clear()\n'
                f'stop()\n'
                f'--{escape}--\n')
    
    result = re.sub(r'attack_async\(\)', replace_attack_async, result)
    
    # attack_simple
    def replace_attack_simple(match):
        return 'attack_do()\nattack_prepare()\nattack_clear()'
    
    result = re.sub(r'attack_simple\(\)', replace_attack_simple, result)
    
    # wait_resources
    def replace_wait_resources(match):
        minerals = match.group(1)
        gas = match.group(2)
        loop_start = next_block_name()
        loop_escape = next_block_name()
        
        return (f'--{loop_start}--\n'
                f'resources_jump({minerals},{gas},{loop_escape})\n'
                f'wait(10)\n'
                f'goto({loop_start})\n'
                f'--{loop_escape}--\n')
    
    result = re.sub(r'wait_resources\((.*),(.*)\)', replace_wait_resources, result)
    
    # wait_until
    def replace_wait_until(match):
        time = match.group(1)
        loop_start = next_block_name()
        loop_escape = next_block_name()
        
        return (f'--{loop_start}--\n'
                f'time_jump({time},{loop_escape})\n'
                f'wait(300)\n'
                f'goto({loop_start})\n'
                f'--{loop_escape}--\n')
    
    result = re.sub(r'wait_until\((.*)\)', replace_wait_until, result)
    
    # wait_owned
    def replace_wait_owned(match):
        unit = match.group(1)
        loop_start = next_block_name()
        loop_escape = next_block_name()
        
        return (f'--{loop_start}--\n'
                f'if_owned({unit},{loop_escape})\n'
                f'wait(300)\n'
                f'goto({loop_start})\n'
                f'--{loop_escape}--\n')
    
    result = re.sub(r'wait_owned\((.*)\)', replace_wait_owned, result)
    
    # message
    def replace_message(match):
        message = match.group(1)
        next_block = next_block_name()
        
        return (f'debug({next_block},{message})\n'
                f'--{next_block}--\n')
    
    result = re.sub(r'message\((.*)\)', replace_message, result)
    
    # enemyownscloaked_jump
    def replace_enemyownscloaked_jump(match):
        block = match.group(1)
        units = ['Zerg Lurker', 'Protoss Arbiter', 'Protoss Templar Archives', 
                 'Protoss Dark Templar', 'Terran Ghost', 'Terran Wraith']
        return expand_enemy_owns(units, block)
    
    result = re.sub(r'enemyownscloaked_jump\((.*)\)', replace_enemyownscloaked_jump, result)
    
    # rush_jump
    def replace_rush_jump(match):
        block = match.group(1)
        too_late_for_buildings = next_block_name()
        too_late_for_units = next_block_name()
        
        return (f'time_jump(2, {too_late_for_buildings})\n'  # 2 is roughly 1:20
                + expand_enemy_owns(['Zerg Spawning Pool', 'Terran Barracks', 'Protoss Gateway'], block) + '\n'
                f'--{too_late_for_buildings}--\n'
                f'time_jump(4, {too_late_for_units})\n'  # 4 is roughly 2:50
                + expand_enemy_owns(['Zerg Zergling', 'Terran Marine', 'Protoss Zealot'], block) + '\n'
                f'--{too_late_for_units}--')
    
    result = re.sub(r'rush_jump\((.*)\)', replace_rush_jump, result)
    
    # enemyownsairtech_jump
    def replace_enemyownsairtech_jump(match):
        block = match.group(1)
        units = ['Terran Starport', 'Protoss Stargate', 'Zerg Spire']
        return expand_enemy_owns(units, block)
    
    result = re.sub(r'enemyownsairtech_jump\((.*)\)', replace_enemyownsairtech_jump, result)
    
    # enemyownsair_jump
    def replace_enemyownsair_jump(match):
        block = match.group(1)
        units = ['Terran Science Vessel', 'Terran Wraith', 'Terran Valkyrie', 'Terran Battlecruiser',
                 'Zerg Mutalisk', 'Zerg Scourge', 'Zerg Guardian', 'Zerg Devourer', 'Zerg Queen',
                 'Protoss Scout', 'Protoss Corsair', 'Protoss Carrier', 'Protoss Arbiter']
        return expand_enemy_owns(units, block)
    
    result = re.sub(r'enemyownsair_jump\((.*)\)', replace_enemyownsair_jump, result)
    
    # build_start
    def replace_build_start(match):
        args = match.group(1).split(',')
        amount = args[0]
        building = args[1]
        priority = args[2] if len(args) > 2 else '80'
        return (f'build({amount}, {building}, {priority})\n'
                f'wait_buildstart({amount}, {building})')
    
    result = re.sub(r'build_start\((.*)\)', replace_build_start, result)
    
    # build_finish
    def replace_build_finish(match):
        args = match.group(1).split(',')
        amount = args[0]
        building = args[1]
        priority = args[2] if len(args) > 2 else '80'
        return (f'build({amount}, {building}, {priority})\n'
                f'wait_buildstart({amount}, {building})\n'
                f'wait_build({amount}, {building})')
    
    result = re.sub(r'build_finish\((.*)\)', replace_build_finish, result)
    
    # build_separately
    def replace_build_separately(match):
        args = match.group(1).split(',')
        amount = int(args[0])
        building = args[1]
        priority = args[2] if len(args) > 2 else '80'
        ret = ''
        
        for i in range(1, amount + 1):
            ret += (f'build({i}, {building}, {priority})\n'
                   f'wait_buildstart({i}, {building})\n'
                   f'wait_build({i}, {building})\n')
        
        return ret
    
    result = re.sub(r'build_separately\((.*)\)', replace_build_separately, result)
    
    # attack_train
    def replace_attack_train(match):
        args = match.group(1).split(',')
        amount = args[0]
        unit = args[1]
        return (f'do_morph({amount}, {unit})\n'
                f'attack_add({amount}, {unit})')
    
    result = re.sub(r'attack_train\((.*)\)', replace_attack_train, result)
    
    # defenseclear
    def replace_defenseclear(match):
        return ('defenseclear_gg()\n'
                'defenseclear_ga()\n'
                'defenseclear_ag()\n'
                'defenseclear_aa()\n')
    
    result = re.sub(r'defenseclear\(\)', replace_defenseclear, result)
    
    # defense_ground
    def replace_defense_ground(match):
        unit = match.group(1)
        do_build = next_block_name()
        skip_build = next_block_name()
        
        return (f'defenseuse_gg(1, {unit})\n'
                f'defenseuse_ga(1, {unit})\n'
                f'time_jump(6, {do_build})\n'
                f'goto({skip_build})\n'
                f'--{do_build}--\n'
                f'defensebuild_gg(1, {unit})\n'
                f'defensebuild_ga(1, {unit})\n'
                f'--{skip_build}--\n')
    
    result = re.sub(r'defense_ground\((.*)\)', replace_defense_ground, result)
    
    # defense_air
    def replace_defense_air(match):
        unit = match.group(1)
        do_build = next_block_name()
        skip_build = next_block_name()
        
        return (f'defenseuse_ag(1, {unit})\n'
                f'defenseuse_aa(1, {unit})\n'
                f'time_jump(6, {do_build})\n'
                f'goto({skip_build})\n'
                f'--{do_build}--\n'
                f'defensebuild_ag(1, {unit})\n'
                f'defensebuild_aa(1, {unit})\n'
                f'--{skip_build}--\n')
    
    result = re.sub(r'defense_air\((.*)\)', replace_defense_air, result)
    
    # defense_ground_train
    def replace_defense_ground_train(match):
        unit = match.group(1)
        return (f'defenseuse_gg(1, {unit})\n'
                f'defenseuse_ga(1, {unit})\n'
                f'defensebuild_gg(1, {unit})\n'
                f'defensebuild_ga(1, {unit})\n')
    
    result = re.sub(r'defense_ground_train\((.*)\)', replace_defense_ground_train, result)
    
    # defense_air_train
    def replace_defense_air_train(match):
        unit = match.group(1)
        return (f'defenseuse_ag(1, {unit})\n'
                f'defenseuse_aa(1, {unit})\n'
                f'defensebuild_ag(1, {unit})\n'
                f'defensebuild_aa(1, {unit})\n')
    
    result = re.sub(r'defense_air_train\((.*)\)', replace_defense_air_train, result)
    
    # (difficulty
    def replace_difficulty(match):
        difficulty = config.get('difficulty', 0) if config else 0
        return f'({difficulty}'
    
    result = re.sub(r'\(difficulty', replace_difficulty, result)
    
    # create_bonus_workers
    def replace_create_bonus_workers(match):
        bonus_workers = config.get('bonusWorkers', 0) if config else 0
        ret = ''
        for i in range(bonus_workers):
            ret += 'create_unit(Peon, 2000, 2000)\n'
        return ret
    
    result = re.sub(r'create_bonus_workers\(\)', replace_create_bonus_workers, result)
    
    # attack_multiple
    def replace_attack_multiple(match):
        mul = int(match.group(1))
        params = match.group(2)
        ret = ''
        
        unit_strs = params.split(',')
        units = []
        
        for unit_str in unit_strs:
            unit_str = unit_str.strip()
            parts = unit_str.split(' ')
            quantity = parts[0]
            name = ' '.join(parts[1:])
            units.append({'quantity': quantity, 'name': name})
        
        more_units_prob = 256 // mul
        done_block = next_block_name()
        
        for i in range(1, mul + 1):
            more_units = next_block_name()
            
            for unit in units:
                ret += f'train({int(unit["quantity"]) * i}, {unit["name"]})\n'
            
            ret += f'random_jump({more_units_prob},{more_units})\n'
            
            for unit in units:
                ret += f'attack_add({int(unit["quantity"]) * i}, {unit["name"]})\n'
            
            ret += f'goto({done_block})\n'
            ret += f'--{more_units}--\n'
        
        ret += f'--{done_block}--\n'
        
        return ret
    
    result = re.sub(r'attack_multiple\((.*?), (.*)\)', replace_attack_multiple, result)
    
    return result
