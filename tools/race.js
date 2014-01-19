var fs = require('fs');

var debug_count = 0;
var nonce = 0

var config = require('./config.json');

var abbrevs = require('./abbrevs.js');
var macros = require('./macros.js');
var buildConverter = require('./buildConverter.js');

function Race(name) {
    function getFullPath(filename) {
        filename = filename.replace('.pyai', '')
        filename += '.pyai'
        
        if(fs.existsSync(config.srcPath + name + '/' + filename)) {
            filename = config.srcPath + name + '/' + filename;
        } else if(fs.existsSync(config.srcPath + name + '/managers/' + filename)) {
            filename = config.srcPath + name + '/managers/' + filename;
        } else if(fs.existsSync(config.srcPath + 'managers/' + filename)) {
            filename = config.srcPath + 'managers/' + filename;
        } else if(fs.existsSync(config.srcPath + name + '/expansions/' + filename)) {
            filename = config.srcPath + name + '/expansions/' + filename;
        } else if(fs.existsSync(config.srcPath + 'expansions/' + filename)) {
            filename = config.srcPath + 'expansions/' + filename;
        } else {
            filename = config.srcPath + filename;
        }
        
        return filename;
    }
    
    function loadContents(filename, skip_block_header) {
        filename = getFullPath(filename)
        
        return parseTemplate(filename, skip_block_header) + "\n";
    }

    this.loadContents = loadContents;

    function parseTemplate(filename, skip_block_header) {
        var comment = "\n#" + filename + '\n';
        var block;
        var file_block;
        
        if(!skip_block_header) {
            file_block = getFileBlock(filename);
        } else {
            file_block = getFileBlock(filename) + (nonce++);
        }
        
        block = (filename.indexOf('header') > -1 ? '' : '--' + file_block + '--\n');
        
        var content = fs.readFileSync(filename, 'utf-8');
        
        content = content.replace(/repeat\(\)/g, 'wait(300)\ngoto(' + file_block + ')');
        
        content = content.replace(/include\((.*)\)/g, function(command, filename) {
            return loadContents(filename, true);
        });
            
        content = content.replace(/include_block\((.*)\)/g, function(command, filename) {
            return loadContents(filename) + "stop()\n";
        });
            
        content = content.replace(/expand\(([\d, ]+)(.*)\)/g, function(command, num, block) {
            return 'expand(' + num + 'gen_expansions_' + block + ')'
        });
            
        content = content.replace(/multirun_file\((.*)\)/g, function(command, relative_filename) {
            debug_count += 1;
            
            var block = getFileBlock(getFullPath(relative_filename))
            
            return "multirun("+ block + ")\n" +
                "goto(" + block + "_done_" + debug_count + ")\n" +
                loadContents(relative_filename) + "\n" +
                "stop()\n" +
                "--" + block + "_done_" + debug_count + "--";
        });

        function chooseFromDir(dir) {
            var ret = "";
            function append(text) {
                ret += text + '\n';
            }
            
            append('--gen_' + dir + '--')
            append('wait(50)')
            append('--gen_jump_loop' + dir + '--')
            
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
                        append("random_jump(5, " + "gen_" + dir + "_" + files[i].replace('.pyai','').replace(/ /g,'_').replace(/^_/, '') + ")");
                    }
                }

                append('goto(gen_jump_loop' + dir + ')');
                
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
            
            var complete = file_block + '_race_checked';
            
            return('enemyowns_jump(command center, ' + (valid_enemies.t ? complete : skip_block) + ')\n' + 
                    'enemyowns_jump(hatchery, ' + (valid_enemies.z ? complete : skip_block) + ')\n' + 
                    'enemyowns_jump(nexus, ' + (valid_enemies.p ? complete : skip_block) + ')\n' + 
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
        
        content = content.replace(/use_midgame_vs\((.*)\)/g, function(original, races) {
            var message = '';
            
            if (config.verbosity >= 5) {
                var styleName = block.replace(/[\-\n ]/g, '').replace('gen_midgame_', '').replace(/_/g, ' ');
                message = debug('Using ' + styleName + ' midgame');
            }

            return race_skip(races, 'gen_midgame') + message;
        });

        content = content.replace(/use_lategame_vs\((.*)\)/g, function(original, races) {
            var message = '';
            
            if (config.verbosity >= 5) {
                var styleName = block.replace(/[\-\n ]/g, '').replace('gen_lategame_', '').replace(/_/g, ' ');
                message = debug('Using ' + styleName + ' lategame');
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