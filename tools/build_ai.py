#!/usr/bin/env python3
import sys
import os
import json
import subprocess
from datetime import datetime

# Add tools directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai import AI

def build(input_race, output_file):
    """Build the AI script for the given race"""
    # Load config
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Build the AI
    ai = AI(input_race, config)
    src = ai.build()
    
    # Get git commit hash
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, check=True)
        commit = result.stdout.strip()[:6]
    except:
        commit = '000000'
    
    # Replace placeholders
    src = src.replace('{commit}', commit)
    src = src.replace('{now}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(src)

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        build(sys.argv[1], sys.argv[2])
    else:
        print(f'Usage: python3 {sys.argv[0]} race output')
        sys.exit(1)
