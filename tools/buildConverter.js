var units = require('./units.json');
var abbrevs = require('./abbrevs.js');

function isUnit(unit) {
    return units.some(function (u) {
        return u.unit === unit;
    });
}

function getUnitInfo(unit) {
    return units.filter(function (u) {
        return u.unit === unit;
    })[0];
}

var parse = function parse(content) {
    var owned = {};
    var supplyFromUnits = 0;
    
    content = content.replace(/^(\d+) (.*)$/mg, function(original, supply, unit) {
        var ret = "";
        
        unit = abbrevs.expand(unit);
        
        if(!owned[unit]) {
            owned[unit] = 0;
        }
        owned[unit] += 1;

        var waitForWorker = supply - supplyFromUnits;
        
        ret += 'build(' + waitForWorker + ', Peon, 80)\n' +
               'wait_buildstart(' + waitForWorker + ', Peon)\n';
        
        if (isUnit(unit)) {
            supplyFromUnits += parseInt(getUnitInfo(unit).supply);
            
            ret += 'train(' + owned[unit] + ', ' + unit + ')\n';
        } else {
            ret += 'build(' + owned[unit] + ', ' + unit + ', 80)\n' +
                   'wait_buildstart(' + owned[unit] + ', ' + unit + ')\n';
        }
        
        return ret;
    });
    
    return content;
};

exports.parse = parse;

