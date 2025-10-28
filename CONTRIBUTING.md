Contributing
============

Before you can hack on this project, you'll need to be able to build it from source so that you can make modifications and see their impact in-game.

Running from source
--------------------

Linux is strongly recommended for development. Everything should work on other platforms, but I only regularly test this on Linux.

### Prerequisites: 

- [GNU Make](https://www.gnu.org/software/make/)
- [Python](http://www.python.org/download/) 2.7 32 bit for PyAI compiler (interacting with storm.dll) and Python 3.6+ for build scripts

### Build 

Run `make bins` to build aiscript.bin or `make mpq` to build patch_rt.mpq with aiscript.bin included.

### Patch SC

1. Make sure that your SCPATH environment variable is set appropriately e.g. `export SCPATH={path to SC}`.
2. Execute `make patch` to compile the AIs, build an MPQ, and replace the default in your SC directory. You can use `make run` or `make run-wine` instead to start the game using Wine.

You could also manually overwrite aiscript.bin in patch_rt.mpq using an MPQ editor or inject aiscript.bin to a running Starcraft instance.

### EUD Injection

There is also work-in-progress support for injecting scripts into UMS maps using EUD triggers. These triggers make use of a buffer overflow in the SetDeaths trigger to overwrite the entire contents of aiscript.bin once a UMS map has loaded. This process is implemented by `tools/eud_gen_trigs.py`.

Currently, the scripts load properly, but there appear to be several differences between the AI environment between UMS and Melee modes that make the AI itself buggy in UMS mode.

New AI commands/macros:
-----------------------

This section is most useful once you're familiar with PyAI scripting. It describes new AI preprocessor commands that you can use when contributing.

### Build Orders

When designing build orders, you can use simple supply count syntax just like you would when writing down builds for human usage. This makes it fairly easy to add or modify builds without a deep knowledge of the AI engine.

    9 Depot
    11 Rax
    14 Marine
    16 Expand
    16 Depot
    16 Marine
    18 Barracks
    18 Marine
    20 Marine
    21 Refinery

### If blocks

Many _jump commands can be accessed using a new Pythonic `if` structure. Here's how you would normally create a block that executes 50% of the time:

    random_jump(128, maybe)
    goto(always)
    --maybe--
    # sometimes do this
    --always--
    # always do this
    
If blocks allow you to write the same code like this:

    if random(128):
        # sometimes do this
    # always do this
    
Else is not yet supported.

### loop blocks

Blocks of code can be looped indefinitely as follows:

    loop:
        do_morph(36, Terran Marine)

### multirun blocks

Blocks of code can be run asyncronously as follows:

    multirun:
        upgrade(1, Protoss Ground Weapons)
        wait(5000)
        upgrade(2, Protoss Ground Weopons)
        
    train(5, Zealot)
    
A stop command is added at the end of the block automatically.

### multirun_loop blocks

Loops can be run asyncronously as follows:

    multirun_loop:
        if enemyowns(Dark Templar):
            build_finish(1, Forge)
            build_start(2, Photon Cannon)
            
The block will automatically repeat after a wait of 75.

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

### valid_midgame_against(Race, Race, Race)

Skips this midgame if nearest race is not in the list of races

### include(file)

Includes the text of the selected file in place of this command. This is similar to the #include C preprocessor macro.
