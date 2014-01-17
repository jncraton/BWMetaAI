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
            if (line.search('    ') > -1) {
                line = line.replace('    ', '')
            } else {
                indent_level--;
                content += '--' + blocks.pop() + '--\n'
            }
        }
        
        if (line.search('if ') > -1) {
            line = line.replace(/if (.*)\((.*)\)/, function (match, function_name, params) {
                return function_name + '_jump(' + params + ')'
            })
        }
        
        if (line.indexOf(':') > -1) {
            var start_block = nextBlockName()
            var end_block = nextBlockName()
            blocks.push(end_block)
            indent_level++;
            line = line.replace(':', '')
            line = line.replace(')', start_block + ')')
            content += line + '\n'
            content += 'goto(' + end_block + ')\n'
            content += '--' + start_block + '--\n'
        } else {
            content += line + '\n'
        }
    })
    
    while (blocks.length > 0) {
        content += '--' + blocks.pop() + '--\n'
    }
    
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
            'wait(10)\n' +
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
        return 'defenseuse_gg(1, ' + unit + ')\n' +
               'defenseuse_ga(1, ' + unit + ')\n';
    });

    content = content.replace(/defense_air\((.*)\)/g, function(original, unit) {
        return 'defenseuse_ag(1, ' + unit + ')\n' +
               'defenseuse_aa(1, ' + unit + ')\n';
    });

    return content;
}

exports.parse = parse;
