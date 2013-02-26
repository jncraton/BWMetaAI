var abbrevs = require('./abbrevs.json');
var abbrevsReplacements = [];

Object.keys(abbrevs).forEach(function(key) {
    for (var i = 0; i < abbrevs[key].length; i += 1) {
        abbrevsReplacements.push({
            'short': abbrevs[key][i],
            'long': key,
        });
    }
});

var expand = function expand(abbrev) {
    abbrevsReplacements.forEach(function(a) {
        abbrev = abbrev.replace(RegExp('^' + a.short + '$', 'i'), a.long);
    });
    
    return abbrev;
}

var parse = function parse(content) {
    content = content.replace(/([,\(] *)([A-Za-z ']*?)([,\)])/g, function(original, prefix, arg, postfix) {
        arg = expand(arg);
        
        return prefix + arg + postfix;
    });
    
    return content;
}

exports.parse = parse;
exports.expand = expand;