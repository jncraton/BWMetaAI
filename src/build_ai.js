var fs = require('fs');
var AI = require('./ai');

var src;
if(process.argv[3]) {
    src = AI(process.argv[2]).build();
    fs.writeFileSync(process.argv[3], src);
} else {
    console.log('Usage: node ' + process.argv[1] + ' race output');
}

