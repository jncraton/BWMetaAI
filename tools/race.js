var fs = require('fs');

var debug_count = 0;

var config = require('./config.json');

function Race(name) {
    function loadContents(filename, skip_block_header) {
        var raw;
        
        filename = filename.replace('.pyai', '')
        filename += '.pyai'
        
        if(fs.existsSync(config.srcPath + name + '/' + filename)) {
            filename = config.srcPath + name + '/' + filename;
        } else {
            filename = config.srcPath + filename;
        }
        
        return parseTemplate(filename, skip_block_header);
    }

    function expandEnemyOwns(units, block) {
        var out = "";
        
        for(var i = 0; i < units.length; i += 1) {
            out += 'enemyowns_jump(' + units[i] + ', ' + block + ')\n';
        }
        
        return out;
    }

    this.loadContents = loadContents;

    function parseTemplate(filename, skip_block_header) {
        var comment = "\n#" + filename + '\n';
        var block;
        
        var owned = {};
            
        if(!skip_block_header) {
            block = (filename.indexOf('header') > -1 ? '' : '--' + getFileBlock(filename) + '--\n');
        } else {
            block = "";
        }
        
        var content = fs.readFileSync(filename, 'utf-8');
    
        content = content.replace(/repeat\(\)/g, 'wait(300)\ngoto(' + getFileBlock(filename) + ')');
        
        content = content.replace(/include\((.*)\)/g, function(command, filename) {
            return loadContents(filename, true);
        });
        
        function race_skip(races, skip_block) {
            races = races.replace(/ /g, '');
            races = races.split(',');
            
            valid_enemies = {};
            
            for(var i = 0; i < races.length; i +=1) {
                valid_enemies[races[i].toLowerCase()[0]] = true;
            }
            
            var complete = getFileBlock(filename) + '_race_checked';
            
            return('race_jump(' +
                (valid_enemies.t ? complete : skip_block) + ',' +
                (valid_enemies.z ? complete : skip_block) + ',' +
                (valid_enemies.p ? complete : skip_block) +
                ')\n' +
                '--' + complete + '--\n');
        }
        
        content = content.replace(/build_weight\((.*)\)/g, function(original, weight) {
            var skip_chance = parseInt((1 - weight) * 255);
            
            return 'random_jump(' + skip_chance + ', gen_opening)';
        });
        
        content = content.replace(/style_weight\((.*)\)/g, function(original, weight) {
            var skip_chance = parseInt((1 - weight) * 255);
            
            return 'random_jump(' + skip_chance + ', gen_styles)';
        });
        
        content = content.replace(/valid_build_against\((.*)\)/g, function(original, races) {
            var message = '';
            
            if (config.verbosity >= 5) {
                var buildName = block.replace(/[\-\n ]/g, '').replace('gen_builds_', '').replace(/_/g, ' ');
                message = debug('Using ' + buildName + ' build');
            }

            return race_skip(races, 'gen_opening') + message;
        });
        
        content = content.replace(/valid_style_against\((.*)\)/g, function(original, races) {
            var message = '';
            
            if (config.verbosity >= 5) {
                var styleName = block.replace(/[\-\n ]/g, '').replace('gen_styles_', '').replace(/_/g, ' ');
                message = debug('Using ' + styleName + ' style');
            }

            return race_skip(races, 'gen_styles') + message;
        });

        content = content.replace(/enemyownscloaked_jump\((.*)\)/g, function(original, block) {
            var units = ['Zerg Lurker', 'Protoss Dark Templar', 'Terran Ghost', 'Terran Wraith'];
            return expandEnemyOwns(units, block);
        });

        content = content.replace(/enemyownsairtech_jump\((.*)\)/g, function(original, block) {
            var units = ['Terran Starport', 'Protoss Stargate', 'Zerg Spire'];
            return expandEnemyOwns(units, block);
        });
        
        content = content.replace(/build_start\((.*)\)/g, function(original, args) {
            args = args.split(',');
            var amount = args[0];
            var building = args[1];
            var priority = args[2] || '80';
            return 'build(' + amount + ', ' + building + ', ' + priority + ')\n' +
                   'wait_buildstart(' + amount + ', ' + building + ')';
        });

        content = content.replace(/build_finish\((.*)\)/g, function(original, args) {
            args = args.split(',');
            var amount = args[0];
            var building = args[1];
            var priority = args[2] || '80';
            return 'build(' + amount + ', ' + building + ', ' + priority + ')\n' +
                   'wait_buildstart(' + amount + ', ' + building + ')\n' +
                   'wait_build(' + amount + ', ' + building + ')';
        });

        content = content.replace(/attack_train\((.*)\)/g, function(original, args) {
            args = args.split(',');
            var amount = args[0];
            var unit = args[1];
            return 'train(' + amount + ', ' + unit + ')\n' +
                   'attack_add(' + amount + ', ' + unit + ')';
        });

        content = content.replace(/defenseclear\(()\)/g, function(original) {
            return 'defenseclear_gg()\n' +
                   'defenseclear_ga()\n' +
                   'defenseclear_ag()\n' +
                   'defenseclear_aa()\n';
        });

        content = content.replace(/^(\d+) (.*)$/mg, function(original, supply, building) {
            if(!owned[building]) {
                owned[building] = 0;
            }
            owned[building] += 1;
            
            return 'build(' + supply + ', Peon, 80)\n' +
                      'wait_buildstart(' + supply + ', Peon)\n' +
                      'build(' + owned[building] + ', ' + building + ', 80)\n' +
                      'wait_buildstart(' + owned[building] + ', ' + building + ')\n';
        });

        if (name === 'terran') {
            content = content.replace(/Town Hall/g, "Terran Command Center");
            content = content.replace(/Peon/g, "Terran SCV");
            content = content.replace(/Gas/g, "Terran Refinery");
        }
        
        if (name === 'zerg') {
            content = content.replace(/Town Hall/g, "Zerg Hatchery");
            content = content.replace(/Peon/g, "Zerg Drone");
            content = content.replace(/Gas/g, "Zerg Extractor");
        }
        
        if (name === 'protoss') {
            content = content.replace(/Town Hall/g, "Protoss Nexus");
            content = content.replace(/Peon/g, "Protoss Probe");
            content = content.replace(/Gas/g, "Protoss Assimilator");
        }
        
        function debug(message) {
            debug_count += 1;
            var block_name = 'd_' + debug_count;
            
            return ('\ndebug(' + block_name + ', ' + message + ')\n' +
                    '--' + block_name + '--\n');
        }
        
        if (config.verbosity >= 10) {
            content = content.replace(/^(?!(TMCx|ZMCx|PMCx|\-\-)).+$/mg, function(original) {
                debug_count += 1;
                var block_name = 'd_' + debug_count;
                return '\ndebug(' + block_name + ', ' + debug_count + ')\n' +
                    '--' + block_name + '--\n' +
                    original + '\n';
            });
        }
        
        return comment + block + content;
    }
    function getFileBlock(filename) {
        var block = 'gen_' + filename.replace(config.srcPath, '');
        block = block.replace(/[-_ \/]/g, '_');
        block = block.replace('.pyai', '')
        block = block.replace(name, '');
        block = block.replace(/__/g, '_');
        return block;
    }

    return this;
}

module.exports = Race;