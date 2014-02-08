var block_counter = 0;

var parse = function parse(content) {
    function expandEnemyOwns(units, block) {
        var out = "";
        
        for(var i = 0; i < units.length; i += 1) {
            out += 'enemyowns_jump(' + units[i] + ', ' + block + ')\n';
        }
        
        return out;
    }
    
    function nextBlockName() {
        block_counter++;
        return 'gen_macro_' + block_counter;
    }
    
    var lines = content.split(/[\r\n]+/);
    
    content = '';
    
    var indent_level = 0;
    var blocks = [];
    lines.forEach(function (line) {
        if (indent_level > 0) {
            for(var i = indent_level; i > 0; i--) {
                if (line.search('    ') > -1) {
                    line = line.replace('    ', '')
                } else {
                    indent_level--;
                    content += blocks.pop()
                }
            }
        }
        
        if (line.search('if ') > -1) {
            line = line.replace(/if (.*)\((.*)\)/, function (match, function_name, params) {
                if (function_name == 'owned') {
                    return 'if_owned(' + params + ')'
                } else {
                    return function_name + '_jump(' + params + ')'
                }
            })
        }
        
        if (line.indexOf(':') > -1) {
            var start_block = nextBlockName()
            var end_block = nextBlockName()

            if (line.search('multirun_loop') > -1) {
                line = line.replace('multirun_loop', 'multirun()')
                blocks.push('wait(75)\ngoto(' + 
                    start_block + 
                    ')\n' + 
                    '--' + end_block + '--\n')
            } else if (line.search('multirun') > -1) {
                line = line.replace('multirun', 'multirun()')
                blocks.push('stop()\n' + 
                    '--' + end_block + '--\n')
            } else {
                blocks.push('--' + end_block + '--\n')
            }
        
            indent_level++;
            line = line.replace(':', '')
            if (line.search(/[a-zA-Z0-9]\)/) > -1) {
                line = line.replace(')', ', ' + start_block + ')')
            } else {
                line = line.replace(')', start_block + ')')
            }
            content += line + '\n'
            content += 'goto(' + end_block + ')\n'
            content += '--' + start_block + '--\n'
        } else {
            content += line + '\n'
        }
    })
    
    while (blocks.length > 0) {
        content += blocks.pop()
    }
    
    content = content.replace(/attack_async\(\)/g, function(original) {
        var start = nextBlockName();
        var escape = nextBlockName();
        
        return 'multirun(' + start + ')\n' + 
            'goto(' + escape + ')\n' +
            '--' + start + '--\n' +
            'attack_do()\n' +
            'attack_clear()\n' +
            'stop()\n' +
            '--' + escape + '--\n';
    });
    
    content = content.replace(/attack_simple\(\)/g, function(original) {
        return 'attack_do()\n' +
                'attack_prepare()\n' +
                'attack_clear()'
    });
    
    content = content.replace(/wait_resources\((.*),(.*)\)/g, function(original, minerals, gas) {
        var loop_start = nextBlockName();
        var loop_escape = nextBlockName();
        
        return '--' + loop_start + '--\n' +
            'resources_jump(' + minerals + ',' + gas + ',' + loop_escape + ')\n' +
            'wait(10)\n' +
            'goto(' + loop_start + ')\n' +
            '--' + loop_escape + '--\n';
    });
    
    content = content.replace(/wait_until\((.*)\)/g, function(original, time) {
        var loop_start = nextBlockName();
        var loop_escape = nextBlockName();
        
        return '--' + loop_start + '--\n' +
            'time_jump(' + time + ',' + loop_escape + ')\n' +
            'wait(300)\n' +
            'goto(' + loop_start + ')\n' +
            '--' + loop_escape + '--\n';
    });
    
    content = content.replace(/wait_owned\((.*)\)/g, function(original, unit) {
        var loop_start = nextBlockName();
        var loop_escape = nextBlockName();
        
        return '--' + loop_start + '--\n' +
            'if_owned(' + unit + ',' + loop_escape + ')\n' +
            'wait(300)\n' +
            'goto(' + loop_start + ')\n' +
            '--' + loop_escape + '--\n';
    });

    content = content.replace(/message\((.*)\)/g, function(original, message) {
        var next_block = nextBlockName();
        
        return 'debug(' + next_block + ',' + message + ')\n' +
            '--' + next_block + '--\n';
    });

    content = content.replace(/enemyownscloaked_jump\((.*)\)/g, function(original, block) {
        var units = ['Zerg Lurker', 'Protoss Templar Archives', 'Protoss Dark Templar', 'Terran Ghost', 'Terran Wraith'];
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

    content = content.replace(/build_separately\((.*)\)/g, function(original, args) {
        args = args.split(',');
        var amount = args[0];
        var building = args[1];
        var priority = args[2] || '80';
        var ret = '';
        
        for (var i = 1; i <= amount; i++) {
            ret += 'build(' + i + ', ' + building + ', ' + priority + ')\n' +
               'wait_buildstart(' + i + ', ' + building + ')\n' +
               'wait_build(' + i + ', ' + building + ')\n';
        }
        
        return ret
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

    content = content.replace(/defense_ground\((.*)\)/g, function(original, unit) {
        var do_build = nextBlockName()
        var skip_build = nextBlockName()
        
        return 'defenseuse_gg(1, ' + unit + ')\n' +
               'defenseuse_ga(1, ' + unit + ')\n' +
               'time_jump(6, ' + do_build + ')\n' +
               'goto(' + skip_build + ')\n' +
               '--' + do_build + '--\n' +
               'defensebuild_gg(1, ' + unit + ')\n' +
               'defensebuild_ga(1, ' + unit + ')\n' +
               '--' + skip_build + '--\n'
    });

    content = content.replace(/defense_air\((.*)\)/g, function(original, unit) {
        var do_build = nextBlockName()
        var skip_build = nextBlockName()
        
        return 'defenseuse_ag(1, ' + unit + ')\n' +
               'defenseuse_aa(1, ' + unit + ')\n' +
               'time_jump(6, ' + do_build + ')\n' +
               'goto(' + skip_build + ')\n' +
               '--' + do_build + '--\n' +
               'defensebuild_ag(1, ' + unit + ')\n' +
               'defensebuild_aa(1, ' + unit + ')\n' +
               '--' + skip_build + '--\n'
    });

    content = content.replace(/defense_ground_train\((.*)\)/g, function(original, unit) {
        var do_build = nextBlockName()
        var skip_build = nextBlockName()
        
        return 'defenseuse_gg(1, ' + unit + ')\n' +
               'defenseuse_ga(1, ' + unit + ')\n' +
               'defensebuild_gg(1, ' + unit + ')\n' +
               'defensebuild_ga(1, ' + unit + ')\n';
    });

    content = content.replace(/defense_air_train\((.*)\)/g, function(original, unit) {
        var do_build = nextBlockName()
        var skip_build = nextBlockName()
        
        return 'defenseuse_ag(1, ' + unit + ')\n' +
               'defenseuse_aa(1, ' + unit + ')\n' +
               'defensebuild_ag(1, ' + unit + ')\n' +
               'defensebuild_aa(1, ' + unit + ')\n'
        });

    content = content.replace(/attack_train_ratio\((.*)\)/g, function(original, params) {
        var ret = ''
        
        units = params.split(',')
        
        units = units.map(function (unit) {
            unit = unit.replace(/^ /g, '')
            
            return {
                quantity: unit.split(' ')[0],
                name: unit.split(' ')[1]
            }
        })
        
        var mul = 3;
        
        for (var i = 1; i <= mul; i++) {
            units.forEach(function (unit) {
                ret += 'train(' + unit.quantity * i + ', ' + unit.name + ')\n'
            })
        }
        
        units.forEach(function (unit) {
            ret += 'attack_add(' + unit.quantity * mul + ', ' + unit.name + ')\n'
        })
        
        return ret
    });
    
    return content;
}

exports.parse = parse;
