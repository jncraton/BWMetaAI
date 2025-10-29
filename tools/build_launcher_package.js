var fs = require('fs')
var exec = require('child_process').exec;
var build_ai = require('./build_ai')

races = ['zerg','terran','protoss']

races.forEach(function (race) {
    builds = fs.readdirSync('src/' + race + '/builds')
    
    builds.forEach(function (build) {
        console.log(race, build)
        config = JSON.parse(fs.readFileSync('tools/config_default.json'))
        config[race].useBuild = build
        fs.writeFileSync('tools/config.json', JSON.stringify(config))
        build_ai.build(race.replace('.pyai'), 'dist/BWAILauncher_package/' + race + '/' + build.replace('pyai', 'txt'))
    })
})
