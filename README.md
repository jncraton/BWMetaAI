BWMetaAI
========

[![Build Status](https://travis-ci.org/jncraton/BWMetaAI.svg?branch=master)](https://travis-ci.org/jncraton/BWMetaAI)

A Brood War AI designed to follow the modern 1v1 metagame.

![Zeal Goon vs Mech](docs/zeal_goon_tank.png)

Purpose
--------

This project seeks to create an AI that provides a unique experience in each game while closely mirroring builds and unit compositions used by humans today.

![Muta Harass](docs/muta_harass.png)

This provides a much stronger learning experience for new players compared to the Blizzard AI. Players are encouraged to scout, learn what the AI is doing, and adapt instead of turtling up. The AI tends to avoid all-in strategies in favor of economic builds, but it also includes a number of rushes to make scouting and early defense important.

![Large bio attack](docs/marines_sunkens.png)

The included screenshots are from real AI vs AI games to demonstrate the unit compositions used in different matchups.

Installation
------------

You need to overwrite the default scripts that Brood War uses for melee games. This allows you to play in any game mode that supports computer opponents, including multiplayer if you are both properly patched to the same version of BWMetaAI. Here's how to patch Brood War:

### StarCraft Remastered Samase Method (version 1.18+)

1. Get [Samase](http://www.staredit.net/topic/17430/0/)
2. Get aiscript.bin from BWMetaAI's [releases](https://github.com/jncraton/BWMetaAI/releases/latest)
3. Make the directory layout like this:
    - StarCraft\x86\StarCraft.exe
    - StarCraft\x86\sesame.exe
    - StarCraft\x86\custom\scripts\aiscript.bin
4. Make a shortcut to sasame.exe and add `custom` as a command line parameter.
5. Run StarCraft using this shortcut

### Version 1.16.1 and lower

1. Browse to your StarCraft folder and make a backup copy of `patch_rt.mpq` so you can revert to the standard AI.
2. Download the latest [patch_rt.mpq](https://github.com/jncraton/BWMetaAI/releases/latest) from the releases and save it over your current patch_rt.mpq.
3. Run StarCraft Brood War and play a non-custom game with an AI opponent. If the AI is running correctly you will receive a message from the AI letting you know it is running.

Build Orders
------------

BWMetaAI includes a number of build orders that have been relatively popular in high level play. Once the initial build is completed, one of several common midgame transitions are used to take the AI into a variety of late game pushes.

### Terran

#### Terran vs Terran

* BBS
* 14 CC
* Siege Expand
* 2 Factory Tank/Vulture
* 2 Factory Vulture

#### Terran vs Zerg

* BBS
* 2 Rax Pressure
* 2 port wraith
* +1 5 Rax
* 1 Rax FE
* 2 Rax FE
* [Fake Mech](https://liquipedia.net/starcraft/Iloveoov_Fake_Mech)
* [Fantasy](https://liquipedia.net/starcraft/Fantasy_Build)

#### Terran vs Protoss

* BBS
* 14 CC
* Siege Expand
* 2 Factory Tank/Vulture
* 2 port wraith



### Zerg

#### Zerg vs Terran

* 5 Pool
* 1 Base Lurker
* 2 Hatch Muta
* 3 Hatch Muta

#### Zerg vs Protoss

* 5 Pool
* 1 Base Lurker
* 3 Hatch Muta
* 4 Hatch before Gas
* 4 Hatch Lair

#### Zerg vs Zerg

* 5 Pool
* 9 Pool Speed into Spire
* 9 Hatch
* Overgas

### Protoss

#### Protoss vs Terran

* 2 Base Carrier
* 2 Gate Range Expand
* 10/15 Gate Dragoon Pressure
* 1 Gate Zealot Dragoon Pressure
* 12 Nexus

#### Protoss vs Zerg

* Forge Fast Expand
* 10/12 Gate Zealots
* 1 Gate Zealot Expand
* 2 Gate Corsair
* 9/9 Gate Zealots
* 2 Gate Dark Templar

#### Protoss vs Protoss

* 12 Nexus
* ZcoreZ Expand
* ZcoreZ Reaver
* 10/12 Gate Zealots
* 9/9 Gate Zealots
* 2 Gate Dark Templar

Late game 
---------

Once the AI has many bases and all useful tech, it jumps into a loop of common late game unit compositions.

### Terran

* Mech
* Battlecruisers
* SK in TvZ only

### Zerg

* Muta-ling
* Lurker-ling-defiler
* Ultra-ling-defiler
* Hydra

### Protoss

* Zealot Dragoon Arbiter
* Zealot Archon
* Carriers

Difficulty
----------

This project doesn't seek to perform especially well against either humans or other AIs. Advanced techniques such as those used in [BWAPI](https://github.com/bwapi/bwapi) are not used. This project only rewrites the internal AI scripts that Brood War uses to decide what to build next and when to attack. This is done primarily to make it very simple to get up and running.

Micro and building placement are still extremely poor. The AI targets most spells poorly, sieges tanks at terrible times, unburrows lurkers to chase things that have gone out of range, wanders around instead of attacking wall-ins, and makes all sorts of other mistakes that good humans would not. Playing against one AI should provide a good learning environment for a newer player. Playing against two or three of these at once can still provide a challenging experience even for decent players.

With all of that in mind, if you find behavior that you think can reasonably be addressed (e.g. you DT rush a computer and it doesn't attempt to build detection), feel free to open an issue.
