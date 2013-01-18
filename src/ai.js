var fs = require('fs');
var Race = require('./race');

function AI (race_name) {
    var race = new Race(race_name);
    var src = "";
    
    function append(text) {
        src += text + '\n';
    }

    this.build = function() {
        // Default boilerplate
        append(race.loadContents('header'));
        append(race.loadContents('intro'));
        append(race.loadContents('define_max'));
        
        // Opening builds
        append("--gen_opening--")
        var builds = fs.readdirSync(race_name + '/builds');
        
        for(var i = 0; i < builds.length; i += 1) {
            if(builds[i][0] == '_') {
                append("goto(gen_builds" + builds[i].replace('.pyai','').replace(/ /g,'_') + ")");
            } else {
                append("random_jump(1, " + "gen_builds_" + builds[i].replace('.pyai','').replace(/ /g,'_') + ")");
            }
        }

        append('goto(gen_opening)');
        
        for(var i = 0; i < builds.length; i += 1) {
            append(race.loadContents(race_name + '/builds/' + builds[i]));
            append('multirun(gen_adapt)');
            append('multirun(gen_expand_loop)');
            append('goto(gen_styles)');
        }
        
        // Strategies
        append("--gen_styles--")
        append("farms_timing()")
        append(race.loadContents(race_name + '/defenseuse'));
        var styles = fs.readdirSync(race_name + '/styles');

        for(var i = 0; i < styles.length; i += 1) {
            if(styles[i][0] == '_') {
                append("goto(gen_styles_" + styles[i].replace('.pyai','').replace(/ /g,'_').replace(/^_/, '') + ")");
            } else {
                append("random_jump(1, " + "gen_styles_" + styles[i].replace('.pyai','').replace(/ /g,'_').replace(/^_/, '') + ")");
            }
        }

        append('goto(gen_styles)');
        
        for(var i = 0; i < styles.length; i += 1) {
            append(race.loadContents(race_name + '/styles/' + styles[i]));
            append('stop()');
        }
        
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