var fs = require('fs');
var AI = require('./ai');
var exec = require('child_process').exec;

var src;
if(process.argv[3]) {
    src = AI(process.argv[2]).build();
    
exec('git rev-parse HEAD', function (error, commit) {
    commit = commit.replace('\n', '').substring(0,6);
    src = src.replace(/{commit}/g, commit);
    fs.writeFileSync(process.argv[3], src);
});
    
} else {
    console.log('Usage: node ' + process.argv[1] + ' race output');
}

