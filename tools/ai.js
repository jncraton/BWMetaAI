var fs = require('fs');
var Race = require('./race');
var config = require('./config.json');

function AI (race_name) {
    var race = new Race(race_name);
    var src = "";
    
    function append(text) {
        src += text + '\n';
    }

    function chooseFromDir(dir, callbacks) {
        if (!callbacks) callbacks = {};
        
        append('--gen_' + dir + '--')
        var files = fs.readdirSync(config.srcPath + race_name + '/' + dir);

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
            if (callbacks.afterEach) callbacks.afterEach();
            append('goto(' + 'gen_end_' + dir + ')');
        }
        
        append('--gen_end_' + dir + '--');
    }
    
    this.build = function() {
        // Default boilerplate
        append(race.loadContents('header'));
        append(race.loadContents('intro'));
        append(race.loadContents('define_max'));
        
        chooseFromDir('builds');
        
        append("farms_timing()")
        append('multirun(gen_adapt)');
        append('multirun(gen_expand_loop)');
        append(race.loadContents(race_name + '/defenseuse'));

        append("--end_midgame--")
        chooseFromDir('lategame', {
            afterEach: function() {
                append('stop()');
            }
        });
        
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
    
        return src;
    }
    
    return this;
}

module.exports = AI;