var fs = require('fs');

exports.build = function(input, output) {
    var AI = require('./ai');
    var exec = require('child_process').exec;

    var src = AI(input).build();
    
    exec('git rev-parse HEAD', function (error, commit) {
        commit = commit.replace('\n', '').substring(0,6);
        src = src.replace(/{commit}/g, commit);
        fs.writeFileSync(output, src);
    });
    
    src = src.replace(/{now}/g, new Date().toISOString().replace(/T/, ' ').replace(/\..+/, ''));
}

if(process.argv[3]) {
    exports.build(process.argv[2], process.argv[3])
} else {
    console.log('Usage: node ' + process.argv[1] + ' race output');
}

