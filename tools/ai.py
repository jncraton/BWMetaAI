import re
import sys
import os

# Add tools directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from race import Race

class AI:
    def __init__(self, race_name, config):
        self.race_name = race_name
        self.race = Race(race_name, config)
        self.src = ""
        self.config = config
        
    def build(self):
        """Build the AI script for the race"""
        # Default boilerplate
        if self.race_name == 'terran':
            self.src = 'TMCx(1342, 101, aiscript):\n'
        elif self.race_name == 'protoss':
            self.src = 'PMCx(1343, 101, aiscript):\n'
        elif self.race_name == 'zerg':
            self.src = 'ZMCx(1344, 101, aiscript):\n'
        
        self.src += self.race.load_contents('main')
        
        # Add wait(1) before non-special lines
        def add_wait(match):
            return 'wait(1)\n' + match.group(0) + '\n'
        
        self.src = re.sub(r'^(?!(TMCx|ZMCx|PMCx|\-\-|#|debug|random)).+$', 
                         add_wait, self.src, flags=re.MULTILINE)
        
        # Add debug blocks for verbosity >= 10
        verbosity = self.config.get('verbosity', 0)
        race_verbosity = self.config.get(self.race_name, {}).get('verbosity', 0)
        
        if verbosity >= 10 or race_verbosity >= 10:
            debug_count = 0
            
            def get_code(num):
                """Generate a short code from a number"""
                valid_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_'
                
                tens = num // len(valid_chars)
                remainder = num - (tens * len(valid_chars))
                
                tens -= 1
                
                tens_char = valid_chars[tens] if tens >= 0 else ''
                return tens_char + valid_chars[remainder]
            
            def add_debug(match):
                nonlocal debug_count
                debug_count += 1
                block_name = f'd10_{debug_count}'
                code = get_code(debug_count)
                
                return (f'debug({block_name}, {code})\n'
                       f'--{block_name}--\n'
                       + match.group(0) + '\n')
            
            self.src = re.sub(r'^(?!(TMCx|ZMCx|PMCx|\-\-|#|debug|wait)).+$',
                            add_debug, self.src, flags=re.MULTILINE)
        
        return self.src
