var fs = require('fs');
var Race = require('./race');
var config = require('./config.json');

function AI (race_name) {
    var race = new Race(race_name);
    var src = "";
    
    function append(text) {
        src += text + '\n';
    }

    function chooseFromDir(dir) {
        append('--gen_' + dir + '--')
        
        var files = [];
            
        try {
            var files = fs.readdirSync(config.srcPath + race_name + '/' + dir);
        } catch (e) {
            console.log('Missing directory');
        }

        if (files.length) {
            for(var i = 0; i < files.length; i += 1) {
                if(files[i][0] == '_') {
                    append("goto(gen_" + dir + "_" + files[i].replace('.pyai','').replace(/ /g,'_').replace(/^_/, '') + ")");
                } else {
                    append("random_jump(1, " + "gen_" + dir + "_" + files[i].replace('.pyai','').replace(/ /g,'_').replace(/^_/, '') + ")");
                }
            }

            append('goto(gen_' + dir + ')');
            
            for(var i = 0; i < files.length; i += 1) {
                append(race.loadContents(race_name + '/' + dir + '/' + files[i]));
                append('goto(' + 'gen_end_' + dir + ')');
            }
        }
        
        append('--gen_end_' + dir + '--');
    }
    
    this.build = function() {
        // Default boilerplate
        switch (race_name) {
            case 'terran':
                append('TMCx(1342, 101, aiscript):\n');
                break;
            case 'protoss':
                append('PMCx(1343, 101, aiscript):\n');
                break;
            case 'zerg':
                append('ZMCx(1344, 101, aiscript):\n');
                break;
        }
        
        append(race.loadContents('main'));
        /*
        append(race.loadContents('header'));
        append(race.loadContents('intro'));
        append(race.loadContents('define_max'));
        
        chooseFromDir('builds');
        
        append("farms_timing()")
        append('multirun(gen_adapt)');
        append('multirun(gen_expand_loop)');
        append(race.loadContents(race_name + '/defenseuse'));

        chooseFromDir('midgame');

        chooseFromDir('lategame');
        
        append(race.loadContents('adapt'))
        append("stop()")

        append(race.loadContents('expand_loop'))
        append("stop()")

        append(race.loadContents('expansion'))
        append("stop()")
        append(race.loadContents('fortified_expansion'))
        append("stop()")
        append(race.loadContents('fast_expansion'))
        append("stop()")
    */
        return src;
    }
    
    return this;
}

module.exports = AI;