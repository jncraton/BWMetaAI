var parse = function parse(content) {
    function expandEnemyOwns(units, block) {
        var out = "";
        
        for(var i = 0; i < units.length; i += 1) {
            out += 'enemyowns_jump(' + units[i] + ', ' + block + ')\n';
        }
        
        return out;
    }

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

    content = content.replace(/defense_ground\((.*)\)/g, function(original, unit) {
        return 'defenseuse_gg(1, ' + unit + ')\n' +
               'defensebuild_gg(1, ' + unit + ')\n';
    });

    content = content.replace(/defense_air\((.*)\)/g, function(original, unit) {
        return 'defenseuse_ag(1, ' + unit + ')\n' +
               'defensebuild_ag(1, ' + unit + ')\n';
    });

    return content;
}

exports.parse = parse;
