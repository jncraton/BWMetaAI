A Brood War AI designed to follow a metagame closer to modern 1v1 than the original Brood War AI.

# Installation

1. Open your Brood War folder (C:\Program Files\StarCraft by default)
2. Create a backup copy of your patch_rt.mpq file
3. Copy build/patch_rt.mpq from this project over the patch_rt.mpq in your Brood War folder
4. Create a game and this AI should be used
5. Replace your original patch_rt.mpq to restore the original AI

# Building from source

Prerequisits: node.js, Python 2.7 32 bit on Windows 

Windows is required for mpq manipulation. If you just want to generate the source of the scripts or aiscript.bin to inject manually, then any OS should be fine.

1. Run `make`

# Build Orders
 
## Terran

* Siege Expand
* 1 Rax FE
* 2 Rax FE
* 2 Rax Pressure
* 14 CC
* 2 Factory Push

## Zerg
 
* 5 Pool
* 9 Pool
* Overpool
* 1 Base Muta
* 1 Base Lurker
* 12 Hatch 12 Pool

## Protoss

* Forge Fast Expand
* 12 Nexus
* 2 Gate Range Expand
* 2 Gate Corsair
* 2 Gate Zealots
* Fast DT

# Play styles

## Terran

* SK
* Mech

## Zerg

* Muta-ling
* Lurker-ling
* Ultra-ling
* Hydra

## Protoss

* Zealot Dragoon
* Zealot Archon

# New AI commands/macros:

This includes an AI preprocessor which implements some new commands that you can use if you want to add your own syles or build orders.

## build_start(amount, building, [priority])

Builds {amount} of {building} at {priority} and waits for construction to start. Priority defaults to 80.

## build_finish(amount, building, [priority])

Builds {amount} of {building} at {priority} and waits for construction to complete. Priority defaults to 80.

## enemyownsairtech_jump(block)

Jumps to block if enemy has Starport, Stargate, or Spire

## enemyownscloaked_jump(block)

Jumps to block if enemy has units that can cloak

## repeat()

Jumps to the beginning of the current file

## valid_build_against(Race, Race, Race)

Skips this build if nearest race is not in the list of races

## valid_style_against(Race, Race, Race)

Skips this style if nearest race is not in the list of races

## include(file)

Includes the text of the selected file in place of this command. This is similar to the #include C preprocessor macro.