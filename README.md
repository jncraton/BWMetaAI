BWMetaAI
========

A Brood War AI designed to follow a metagame closer to modern 1v1 than the original Brood War AI.

Purpose
--------

There are a lot of good BW AI mods already available (http://broodwarai.com/wiki/index.php?title=AI_script_mods). This project seeks to create a non-cheating AI that provides a unique experience with each game. It tends to avoid all-in strategies in favor of an economic focus, but it also includes a number of rushes to make scouting important.

It includes a number of build order that have been relatively popular in high level play.

Build Orders
------------
 
### Terran

* Siege Expand
* 1 Rax FE
* 2 Rax FE
* 2 Rax Pressure
* BBS
* 14 CC
* 2 Factory Push
* +1 5 Rax
* 2 port wraith

### Zerg
 
* 5 Pool
* 9 Pool
* Overpool
* 1 Base Muta
* 1 Base Lurker
* 12 Hatch 12 Pool
* 4 Hatch Lair
* 3 Hatch muta

### Protoss

* Forge Fast Expand
* 12 Nexus
* 2 Gate Range Expand
* 10/15 Gate Dragoon Pressure
* 2 Gate Corsair
* 2 Gate Zealots
* Fast DT

Late game 
---------

### Terran

* SK
* Mech
* Battlecruisers

### Zerg

* Muta-ling
* Lurker-ling-defiler
* Ultra-ling-defiler
* Hydra

### Protoss

* Zealot Dragoon Arbiter
* Zealot Archon
* Carriers

Running from source
--------------------

Prerequisites: node.js, Python 2.7 32 bit on Windows 

Windows is required for mpq manipulation. If you just want to generate the source of the scripts or aiscript.bin to inject manually, then any OS should be fine.

Build and patch SC
===============

1. Edit the makefile to use your SC path
2. Edit the makefile to use the absolute path to your prefered SC launcher. This can simply be starcraft.exe if no launcher is used
3. Run `make run` to compile the AIs, build an MPQ, and replace the default in your SC directory.

New AI commands/macros:
-----------------------

This includes an AI preprocessor which implements some new commands that you can use if you want to add your own syles or build orders.

### If blocks

Many _jump commands can be accessed using a Pythonic if structure. Here's how you would normally create a block that executes 50% of the time:

    random_jump(128, maybe)
    goto(always)
    --maybe--
    # sometimes do this
    --always--
    # always do this
    
If blocks allow you to write the same code like this:

    if random(128):
        # sometime do this
    # always do this
    
Else is not yet supported.

### message(string)

Displays the string as a message from the AI. This does not require a block to jump to like debug() does.

### wait_resources(min, gas)

Waits until the ai has the corresponding amount of minerals and gas in the bank.

### wait_until(minutes)

Waits until {minutes} normal games minutes have elapsed.

### attack_async()

Spawns a new thread to attack and continues execution of calling thread immediately.

### attack_simple()

Prepares, attacks with, and clears the current attacking parting.

### build_start(amount, building, [priority])

Builds {amount} of {building} at {priority} and waits for construction to start. Priority defaults to 80.

### build_finish(amount, building, [priority])

Builds {amount} of {building} at {priority} and waits for construction to complete. Priority defaults to 80.

### build_separately(amount, building, [priority])

Builds {amount} of {building} at {priority} one at a time and waits for construction to complete. Priority defaults to 80.

### enemyownsairtech_jump(block)

Jumps to block if enemy has Starport, Stargate, or Spire

### enemyownscloaked_jump(block)

Jumps to block if enemy has units that can cloak

### repeat()

Jumps to the beginning of the current file

### valid_build_against(Race, Race, Race)

Skips this build if nearest race is not in the list of races

### valid_style_against(Race, Race, Race)

Skips this style if nearest race is not in the list of races

### include(file)

Includes the text of the selected file in place of this command. This is similar to the #include C preprocessor macro.
