import os
import re
import json
import sys

# Add tools directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abbrevs
import macros
import buildConverter

debug_count = 0
block_count = 0
nonce = 0

class Race:
    def __init__(self, name, config):
        self.name = name
        self.config = config
        
    def get_full_path(self, filename):
        """Get the full path for a given filename"""
        filename = filename.replace('.pyai', '') + '.pyai'
        
        src_path = self.config.get('srcPath', 'src/')
        
        paths_to_check = [
            os.path.join(src_path, self.name, filename),
            os.path.join(src_path, self.name, 'managers', filename),
            os.path.join(src_path, 'managers', filename),
            os.path.join(src_path, self.name, 'expansions', filename),
            os.path.join(src_path, 'expansions', filename),
            os.path.join(src_path, filename),
        ]
        
        for path in paths_to_check:
            if os.path.exists(path):
                return path
        
        # Return the first guess if file doesn't exist
        return paths_to_check[0]
    
    def load_contents(self, filename, skip_block_header=False):
        """Load and parse template file contents"""
        filename = self.get_full_path(filename)
        return self.parse_template(filename, skip_block_header) + "\n"
    
    def get_file_block(self, filename):
        """Generate a block name from a filename"""
        src_path = self.config.get('srcPath', 'src/')
        block = 'gen_' + filename.replace(src_path, '')
        block = re.sub(r'[-_ /]', '_', block)
        block = block.replace('.pyai', '')
        block = block.replace(self.name, '')
        block = re.sub(r'__', '_', block)
        return block
    
    def parse_template(self, filename, skip_block_header=False):
        """Parse a template file and return the processed content"""
        global debug_count, block_count, nonce
        
        comment = f"\n#{filename}\n"
        
        if not skip_block_header:
            file_block = self.get_file_block(filename)
        else:
            file_block = self.get_file_block(filename) + str(nonce)
            nonce += 1
        
        if 'header' in filename:
            block = ''
        else:
            block = f'--{file_block}--\n'
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace repeat()
        content = re.sub(r'repeat\(\)', f'wait(75)\ngoto({file_block})', content)
        
        # Replace include()
        def replace_include(match):
            inc_filename = match.group(1)
            if inc_filename == 'freemoney' and self.config.get('difficulty', 0) == 0:
                return ""
            return self.load_contents(inc_filename, True)
        
        content = re.sub(r'include\((.*)\)', replace_include, content)
        
        # Replace include_block()
        def replace_include_block(match):
            inc_filename = match.group(1)
            return self.load_contents(inc_filename) + "stop()\n"
        
        content = re.sub(r'include_block\((.*)\)', replace_include_block, content)
        
        # Replace expand()
        def replace_expand(match):
            num = match.group(1)
            block = match.group(2)
            if 'gen_expansions' in block:
                return f'expand({num}{block})'
            else:
                return f'expand({num}gen_expansions_{block})'
        
        content = re.sub(r'expand\(([\d, ]+)(.*)\)', replace_expand, content)
        
        # Replace panic()
        def replace_panic(match):
            block = match.group(1)
            return f'panic(gen_expansions_{block})'
        
        content = re.sub(r'panic\((.*)\)', replace_panic, content)
        
        # Replace multirun_file()
        def replace_multirun_file(match):
            global block_count
            
            relative_filename = match.group(1)
            block_count += 1
            
            # Note: Using "undefined" to match JavaScript bug where 'block' variable
            # is used before being reassigned in the replacement function
            done_block = "undefined_done_" + str(block_count)
            multirun_block = self.get_file_block(self.get_full_path(relative_filename))
            
            return (f"multirun({multirun_block})\n"
                   f"goto({done_block})\n"
                   + self.load_contents(relative_filename) + "\n"
                   f"stop()\n"
                   f"--{done_block}--")
        
        content = re.sub(r'multirun_file\((.*)\)', replace_multirun_file, content)
        
        # Replace choose_from_dir()
        def replace_choose_from_dir(match):
            dir_name = match.group(1)
            return self.choose_from_dir(dir_name, file_block)
        
        content = re.sub(r'choose_from_dir\((.*)\)', replace_choose_from_dir, content)
        
        # Replace build_weight()
        def replace_build_weight(match):
            weight = float(match.group(1))
            skip_chance = int((1 - weight) * 255)
            return f'random_jump({skip_chance}, gen_builds)'
        
        content = re.sub(r'build_weight\((.*)\)', replace_build_weight, content)
        
        # Replace style_weight()
        def replace_style_weight(match):
            weight = float(match.group(1))
            skip_chance = int((1 - weight) * 255)
            return f'random_jump({skip_chance}, gen_lategame)'
        
        content = re.sub(r'style_weight\((.*)\)', replace_style_weight, content)
        
        # Replace use_build_vs()
        def replace_use_build_vs(match):
            races = match.group(1)
            message = ''
            
            verbosity = self.config.get('verbosity', 0)
            race_verbosity = self.config.get(self.name, {}).get('verbosity', 0)
            
            if verbosity >= 5 or race_verbosity >= 5:
                build_name = re.sub(r'[\-\n ]', '', block)
                build_name = build_name.replace('gen_builds_', '').replace('_', ' ')
                message = self.debug(f'Using {build_name} build')
            
            return self.race_skip(races, 'gen_builds', file_block) + message
        
        content = re.sub(r'use_build_vs\((.*)\)', replace_use_build_vs, content)
        
        # Replace use_attack_vs()
        def replace_use_attack_vs(match):
            races = match.group(1)
            message = ''
            
            verbosity = self.config.get('verbosity', 0)
            race_verbosity = self.config.get(self.name, {}).get('verbosity', 0)
            
            if verbosity >= 5 or race_verbosity >= 5:
                style_name = re.sub(r'[\-\n ]', '', block)
                style_name = style_name.replace('gen_attack_', '').replace('_', ' ')
                message = self.debug(f'Using {style_name} attack')
            
            return 'wait(50)\n' + self.race_skip(races, 'gen_attacks', file_block) + message
        
        content = re.sub(r'use_attack_vs\((.*)\)', replace_use_attack_vs, content)
        
        # Apply buildConverter, macros, and abbrevs
        content = buildConverter.parse(content)
        content = macros.parse(content)
        content = abbrevs.parse(content)
        
        # Replace race-specific placeholders
        if self.name == 'terran':
            content = content.replace('Town Hall', "Terran Command Center")
            content = content.replace('Peon', "Terran SCV")
            content = content.replace('Gas', "Terran Refinery")
        elif self.name == 'zerg':
            content = content.replace('Town Hall', "Zerg Hatchery")
            content = content.replace('Peon', "Zerg Drone")
            content = content.replace('Gas', "Zerg Extractor")
        elif self.name == 'protoss':
            content = content.replace('Town Hall', "Protoss Nexus")
            content = content.replace('Peon', "Protoss Probe")
            content = content.replace('Gas', "Protoss Assimilator")
        
        return comment + block + content
    
    def choose_from_dir(self, dir_name, file_block):
        """Generate code to randomly choose from files in a directory"""
        ret = ""
        ret += f'--gen_{dir_name}--\n'
        ret += f'--gen_jump_loop{dir_name}--\n'
        
        files = []
        src_path = self.config.get('srcPath', 'src/')
        dir_path = os.path.join(src_path, self.name, dir_name)
        
        try:
            if os.path.exists(dir_path):
                files = sorted([f for f in os.listdir(dir_path) if f.endswith('.pyai')])
        except Exception as e:
            print(f'Missing directory {dir_path}')
        
        def get_build_contents(build):
            build = build.replace('.pyai', '')
            contents = self.load_contents(os.path.join(self.name, dir_name, build + '.pyai'))
            return contents
        
        race_config = self.config.get(self.name, {})
        use_build = race_config.get('useBuild')
        
        if dir_name == 'builds' and use_build:
            ret += get_build_contents(use_build)
        else:
            if files:
                for file in files:
                    file_name = file.replace('.pyai', '').replace(' ', '_')
                    if file[0] == '_':
                        ret += f"goto(gen_{dir_name}_{file_name.replace('_', '', 1)})\n"
                    else:
                        ret += f"random_jump(2, gen_{dir_name}_{file_name})\n"
                
                ret += f'goto(gen_jump_loop{dir_name})\n'
                
                for file in files:
                    ret += get_build_contents(file)
                    ret += f'goto(gen_end_{dir_name})\n'
        
        ret += f'--gen_end_{dir_name}--\n'
        
        return ret
    
    def race_skip(self, races, skip_block, file_block):
        """Generate race detection code"""
        races = races.replace(' ', '')
        race_list = races.split(',')
        
        valid_enemies = {}
        for race in race_list:
            valid_enemies[race.lower()[0]] = True
        
        complete = file_block + '_race_checked'
        
        result = (f'enemyowns_jump(command center, {complete if valid_enemies.get("t") else skip_block})\n'
                 f'enemyowns_jump(hatchery, {complete if valid_enemies.get("z") else skip_block})\n'
                 f'enemyowns_jump(nexus, {complete if valid_enemies.get("p") else skip_block})\n'
                 f'--{complete}--\n')
        
        return result
    
    def debug(self, message):
        """Generate debug message code"""
        global block_count
        block_count += 1
        block_name = f'd_{block_count}'
        
        return (f'\ndebug({block_name}, {message})\n'
               f'--{block_name}--\n')
