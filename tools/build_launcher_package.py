#!/usr/bin/env python3
import os
import json
import sys

# Add tools directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ai

races = ['zerg', 'terran', 'protoss']

for race in races:
    builds_dir = os.path.join('src', race, 'builds')
    
    if not os.path.exists(builds_dir):
        continue
    
    builds = [f for f in os.listdir(builds_dir) if f.endswith('.pyai')]
    
    for build in builds:
        print(race, build)
        
        # Load default config
        with open('tools/config_default.json', 'r') as f:
            config = json.load(f)
        
        # Set the specific build
        if race not in config:
            config[race] = {}
        config[race]['useBuild'] = build
        
        # Write temporary config
        with open('tools/config.json', 'w') as f:
            json.dump(config, f)
        
        # Build the AI
        output_dir = os.path.join('dist', 'BWAILauncher_package', race)
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, build.replace('.pyai', '.txt'))
        build_ai.build(race, output_file)
