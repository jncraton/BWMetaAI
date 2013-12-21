var fs = require('fs');

var debug_count = 0;

var config = require('./config.json');

var abbrevs = require('./abbrevs.js');
var macros = require('./macros.js');
var buildConverter = require('./buildConverter.js');

function Race(name) {
    function loadContents(filename, skip_block_header) {
        var raw;
        
        filename = filename.replace('.pyai', '')
        filename += '.pyai'
        
        if(fs.existsSync(config.srcPath + name + '/' + filename)) {
            filename = config.srcPath + name + '/' + filename;
        } else {
            filename = config.srcPath + filename;
        }
        
        return parseTemplate(filename, skip_block_header) + "\n";
    }

    this.loadContents = loadContents;

    function parseTemplate(filename, skip_block_header) {
        var comment = "\n#" + filename + '\n';
        var block;
        
        if(!skip_block_header) {
            block = (filename.indexOf('header') > -1 ? '' : '--' + getFileBlock(filename) + '--\n');
        } else {
            block = "";
        }
        
        var content = fs.readFileSync(filename, 'utf-8');
        
        content = content.replace(/repeat\(\)/g, 'wait(300)\ngoto(' + getFileBlock(filename) + ')');
        
        content = content.replace(/include\((.*)\)/g, function(command, filename) {
            return loadContents(filename, true);
        });
            
        content = content.replace(/include_block\((.*)\)/g, function(command, filename) {
            return loadContents(filename) + "stop()\n";
        });
            
        content = content.replace(/multirun_file\((.*)\)/g, function(command, filename) {
            debug_count += 1;
            
            return "multirun(gen_" + filename + ")\n" +
                "goto(gen_" + filename + "_done_" + debug_count + ")\n" +
                loadContents(filename) + "\n" +
                "stop()\n" +
                "--gen_" + filename + "_done_" + debug_count + "--";
        });

        function chooseFromDir(dir) {
            var ret = "";
            function append(text) {
                ret += text + '\n';
            }
            
            append('--gen_' + dir + '--')
            
            var files = [];
                
            try {
                var files = fs.readdirSync(config.srcPath + name + '/' + dir);
            } catch (e) {
                console.log('Missing directory ' + config.srcPath + name + '/' + dir);
            }

            if (files.length) {
                for(var i = 0; i < files.length; i += 1) {
                    if(files[i][0] == '_') {
                        append("goto(gen_" + dir + "_" + files[i].replace('.pyai','').replace(/ /g,'_').replace(/^_/, '') + ")");
                    } else {
                        append("random_jump(1, " + "gen_" + dir + "_" + files[i].replace('.pyai','').replace(/ /g,'_').replace(/^_/, '') + ")");
                    }
                }

                append('goto(gen_' + dir + ')');
                
                for(var i = 0; i < files.length; i += 1) {
                    append(loadContents(name + '/' + dir + '/' + files[i]));
                    append('goto(' + 'gen_end_' + dir + ')');
                }
            }
            
            append('--gen_end_' + dir + '--');
            
            return ret;
        }

        content = content.replace(/choose_from_dir\((.*)\)/g, function(command, dir) {
            return chooseFromDir(dir);
        });
            
        function race_skip(races, skip_block) {
            races = races.replace(/ /g, '');
            races = races.split(',');
            
            valid_enemies = {};
            
            for(var i = 0; i < races.length; i +=1) {
                valid_enemies[races[i].toLowerCase()[0]] = true;
            }
            
            var complete = getFileBlock(filename) + '_race_checked';
            
            return('race_jump(' +
                (valid_enemies.t ? complete : skip_block) + ',' +
                (valid_enemies.z ? complete : skip_block) + ',' +
                (valid_enemies.p ? complete : skip_block) +
                ')\n' +
                '--' + complete + '--\n');
        }
        
        content = content.replace(/build_weight\((.*)\)/g, function(original, weight) {
            var skip_chance = parseInt((1 - weight) * 255);
            
            return 'random_jump(' + skip_chance + ', gen_builds)';
        });
        
        content = content.replace(/style_weight\((.*)\)/g, function(original, weight) {
            var skip_chance = parseInt((1 - weight) * 255);
            
            return 'random_jump(' + skip_chance + ', gen_lategame)';
        });
        
        content = content.replace(/use_build_vs\((.*)\)/g, function(original, races) {
            var message = '';
            
            if (config.verbosity >= 5) {
                var buildName = block.replace(/[\-\n ]/g, '').replace('gen_builds_', '').replace(/_/g, ' ');
                message = debug('Using ' + buildName + ' build');
            }

            return race_skip(races, 'gen_builds') + message;
        });
        
        content = content.replace(/use_lategame_vs\((.*)\)/g, function(original, races) {
            var message = '';
            
            if (config.verbosity >= 5) {
                var styleName = block.replace(/[\-\n ]/g, '').replace('gen_lategame_', '').replace(/_/g, ' ');
                message = debug('Using ' + styleName + ' style');
            }

            return race_skip(races, 'gen_lategame') + message;
        });

        content = buildConverter.parse(content);
        content = macros.parse(content);
        content = abbrevs.parse(content);
    
        if (name === 'terran') {
            content = content.replace(/Town Hall/g, "Terran Command Center");
            content = content.replace(/Peon/g, "Terran SCV");
            content = content.replace(/Gas/g, "Terran Refinery");
        }
        
        if (name === 'zerg') {
            content = content.replace(/Town Hall/g, "Zerg Hatchery");
            content = content.replace(/Peon/g, "Zerg Drone");
            content = content.replace(/Gas/g, "Zerg Extractor");
        }
        
        if (name === 'protoss') {
            content = content.replace(/Town Hall/g, "Protoss Nexus");
            content = content.replace(/Peon/g, "Protoss Probe");
            content = content.replace(/Gas/g, "Protoss Assimilator");
        }
        
        function debug(message) {
            debug_count += 1;
            var block_name = 'd_' + debug_count;
            
            return ('\ndebug(' + block_name + ', ' + message + ')\n' +
                    '--' + block_name + '--\n');
        }
        
        if (config.verbosity >= 10) {
            content = content.replace(/^(?!(TMCx|ZMCx|PMCx|\-\-)).+$/mg, function(original) {
                debug_count += 1;
                var block_name = 'd_' + debug_count;
                return '\ndebug(' + block_name + ', ' + debug_count + ')\n' +
                    '--' + block_name + '--\n' +
                    original + '\n';
            });
        }
        
        return comment + block + content;
    }
    function getFileBlock(filename) {
        var block = 'gen_' + filename.replace(config.srcPath, '');
        block = block.replace(/[-_ \/]/g, '_');
        block = block.replace('.pyai', '')
        block = block.replace(name, '');
        block = block.replace(/__/g, '_');
        return block;
    }

    return this;
}

module.exports = Race;