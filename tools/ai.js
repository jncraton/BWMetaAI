var Race = require('./race');
var config = require('./config.json');

function AI (race_name) {
    var race = new Race(race_name);
    var src = "";

    this.build = function() {
        // Default boilerplate
        switch (race_name) {
            case 'terran':
                src = 'TMCx(1342, 101, aiscript):\n';
                break;
            case 'protoss':
                src = 'PMCx(1343, 101, aiscript):\n';
                break;
            case 'zerg':
                src = 'ZMCx(1344, 101, aiscript):\n';
                break;
        }
        
        src += race.loadContents('main');
        
        if (config.verbosity >= 10 || config[race_name].verbosity >= 10) {
            debug_count = 0
            
            src = src.replace(/^(?!(TMCx|ZMCx|PMCx|\-\-|#|debug)).+$/mg, function(original) {
                function getCode(num) {
                    var valid_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_'
                    
                    var tens = Math.floor(num / valid_chars.length)
                    var remainder = num - (tens * valid_chars.length)
                    
                    tens -= 1
                    
                    return '' +  (tens >= 0 ? valid_chars[tens] : '') + valid_chars[remainder]
                }
                
                debug_count += 1;
                var block_name = 'd10_' + debug_count;
                return 'debug(' + block_name + ', ' + getCode(debug_count) + ')\n' +
                    '--' + block_name + '--\n' +
                    'wait(1)\n' +
                    original + '\n';
            });
        }
        
        return src;
    }
    
    return this;
}

module.exports = AI;