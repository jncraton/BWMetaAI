var Race = require('./race');

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
        
        return src;
    }
    
    return this;
}

module.exports = AI;