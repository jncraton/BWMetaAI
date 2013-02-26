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

var parse = function parse(content) {
    content = content.replace(/([,\(] *)([A-Za-z ']*?)([,\)])/g, function(original, prefix, arg, postfix) {
        abbrevsReplacements.forEach(function(abbrev) {
            arg = arg.replace(RegExp('^' + abbrev.short + '$', 'i'), abbrev.long);
        });
        return prefix + arg + postfix;
    });
    
    return content;
}

exports.parse = parse;