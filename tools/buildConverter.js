var parse = function parse(content) {
    var owned = {};
    
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
    
    return content;
};

exports.parse = parse;

