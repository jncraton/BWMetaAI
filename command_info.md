# Header commands

## farms_notiming
Build necessary farms only when it hits the maximum supply available.

## farms_timing
Build necessary farms with a correct timing, so nothing is paused by a maximum supply limit hit.

## start_areatown
Starts the AI Script for area town management. Should only be used in campaign scripts, as it uses the trigger location as its bounds (or area).

## start_campaign
Starts the AI Script for Campaign. Note: This command may have many subtle (but significant in number) changes to AI behaviour which may be desirable in some cases, but not in others.

## start_town
Starts the AI Script for town management.

## transports_off
Computer will not manage/build transports on its own.

## check_transports
Informs computer to build transports on its own. If start_campaign was called, then 2 transports will be built, otherwise 5 will be built. The first transport is built at priority 80 and subsequent transports are built at priority 50. Protoss also trains up to 2 observers at priority 80. Used with header transports_off. 

# Build/Attack/Defense order commands

## attack_add (byte) (military)
Add %1(byte) %2(military) to the current attacking party. %1 (byte) can be at most 62, otherwise the command is ignored.

## attack_clear
Clear the attack data.

## attack_do
Attack the enemy with the current attacking party.

## attack_prepare
Prepare the attack.

## build (byte) (building) (byte)
Build %2(building) until it commands %1(byte) of them, at priority %3(byte). The maximum value of %1(byte) is 30.

## defensebuild_aa (byte) (military)
Build %1(byte) %2(military) to defend against enemy attacking air units.

## defensebuild_ag (byte) (military)
Build %1(byte) %2(military) to defend against enemy attacking air units.

## defensebuild_ga (byte) (military)
Build %1(byte) %2(military) to defend against enemy attacking ground units.

## defensebuild_gg (byte) (military)
Build %1(byte) %2(military) to defend against enemy attacking ground units.

## defenseclear_aa
Clear defense against enemy attacking air units.

## defenseclear_ag
Clear defense against enemy attacking air units.

## defenseclear_ga
Clear defense against enemy attacking ground units.

## defenseclear_gg
Clear defense against enemy attacking ground units.

## defenseuse_aa (byte) (military)
Use %1(byte) %2(military) to defend against enemy attacking air units.

## defenseuse_ag (byte) (military)
Use %1(byte) %2(military) to defend against enemy attacking air units.

## defenseuse_ga (byte) (military)
Use %1(byte) %2(military) to defend against enemy attacking ground units.

## defenseuse_gg (byte) (military)
Use %1(byte) %2(military) to defend against enemy attacking ground units.

## do_morph (byte) (military)
Morph %2(military) until it commands %1(byte) of them.

## get_oldpeons (byte)
This command takes X number of workers from the main to move to the expansion. Should be used after the expansion is completed.

## guard_all
Uses all available units to guard the town.

## guard_resources (military)
Send units of type %1(military) to guard as many unacquired base locations as possible(1 per spot).

## place_guard (unit) (byte)
Place one %1(unit) to guard town at strategic location %2.
Location:
0 = town center
1 = mineral line
2 = geyser/refinery

## player_need (byte) (building)
If the player does not own %1(byte) number of %2(building), then build it at priority 80, otherwise ignore this opcode.
This command is different from build because it is global and not local to the town.

## prep_down (byte) (byte) (military)
Add all %3(military) to the current attacking party except for %1(byte) of them, however it must send a minimum of %2(byte) of them.

## tech (tech) (byte)
Research technology %1(technology), at priority %2(byte).

## train (byte) (military)
Train %2(military) until it commands %1(byte) of them.

## upgrade (byte) (upgrade) (byte)
Research upgrade %2(upgrade) up to level %1(byte), at priority %3(byte). The maximum supported upgrade level is 31.

## wait (word)
Wait for %1(word) logical game frames. A game frame is 42 milliseconds on fastest game speed.

## wait_finishattack
Wait until attacking party has finished to attack.

## wait_force (byte) (unit)
Wait until computer commands %1(byte) %2(unit).

## wait_build (byte) (building)
Wait until computer commands %1(byte) %2(building).

## wait_buildstart (byte) (building)
Wait until construction of %1(byte) %2(building) has started.

## wait_train (byte) (military)
Wait until computer commands %1(byte) %2(military).

# Flow control commands

## call (block)
Call %1(block) as a sub-routine. Only one call can be made in the game at all times from any computer player running a script.
If an AI owned by player 1 makes a call, then player 2 makes a call, will override player 1's call and controls the flow of the return statement.
Be sure that there is no wait command or blocking command inside the call to have it function correctly.

## enemyowns_jump (unit) (block)
If enemy has a %1(unit), jump to %2(block).

## enemyresources_jump (word) (word) (block)
If enemy has at least %1(word) minerals and %2(word) gas then jump in %3(block).

## goto (block)
Jump to %1(block).

## groundmap_jump (block)
If it is a ground map(in other words, if the enemy is reachable without transports), jump to %1(block). This will jump if any enemy structure is reachable at any given point.

## if_owned (unit) (block)
If the player owns a %1(unit) (includes incomplete) then jump to %2(block).

## killable
Allows the current thread to be killed by another one.

## kill_thread
Kills all threads that have the killable attribute (including threads owned by other players). This should not be used in a script.

## notowns_jump (unit) (block)
If computer doesn't have a %1(unit), jump to %2(block).

## race_jump (block) (block) (block)
According to the enemy race, jump in %1(block) if enemy is Terran, %2(block) if Zerg or %3(block) if Protoss.

## random_jump (byte) (block)
There is %1(byte) chances out of 256 to jump to %2(block).

## resources_jump (word) (word) (block)
If computer has at least %1(word) minerals and %2(word) gas then jump in %3(block).

## return
Return to the flow point of the call command.

## rush (byte) (block)
will jump to %2(block) if %1(byte) conditions exist.

### Rush scoring system:

- Protoss Air Score = Protoss Dragoons + Protoss Scouts
- Zerg Ground Score = Zerg Hydralisks + Zerg Sunken Colonies * 2
- Zerg Air Score = Zerg Hydralisks + Zerg Mutalisks + Zerg Spore Colonies * 2
- Terran Infantry Score = bunkers * 4 <= marines ? marines + bunkers * 4 : 2 * marines

### Rush conditions:

#### Terran

- 0: Commands a Barracks
- 1: Terran Infantry Score > 16
- 2: Terran Infantry Score > 24
- 3: Terran Infantry Score > 5
- 4: Terran Infantry Score > 16
- 5: Terran Infantry Score > 6
- 6: Terran Infantry Score > 12
- 7: Commands a Siege Tank
- 8: Terran Infantry Score > 5
- 9: Terran Infantry Score > 9
- 10: Terran Infantry Score > 4
- 11: Terran Infantry Score > 10
- 12: Terran Infantry Score > 16
- 13: Terran Infantry Score > 24

#### Zerg

- 0: Commands a Spawning Pool
- 1: Zerg Ground Score > 10
- 2: Zerg Air Score > 10
- 3: Zerg Ground Score > 2, or commands a Hydralisk Den
- 4: Zerg Ground Score > 10
- 5: Zerg Ground Score > 6
- 6: Zerg Sunken Colonies > 1
- 7: Commands a Queen
- 8: Zerg Ground Score > 2
- 9: Zerg Ground Score > 4
- 10: Zerg Ground Score > 4
- 11: Zerg Ground Score > 10
- 12: Zerg Air Score > 5
- 13: Zerg Air Score > 10

#### Protoss

- 0: Commands a Gateway
- 1: Protoss Zealots > 6
- 2: Not used
- 3: Protoss Zealots > 1
- 4: Protoss Zealots > 8
- 5: Protoss Zealots > 3
- 6: Protoss Dragoons > 1
- 7: Protoss Zealots > 6
- 8: Protoss Zealots > 1
- 9: Protoss Zealots > 5
- 10: Protoss Zealots > 2
- 11: Protoss Zealots > 5
- 12: Protoss Air Score > 2
- 13: Protoss Air Score > 7

## stop
Stop script code execution. Often used to close script blocks called simultaneously.

## time_jump (byte) (block)
Jumps to %2(block) if %1(byte) normal game minutes have passed in the game.

## try_townpoint (byte) (block)
Jump to %2(block) when the AI owns %1 number of expansions.

# Multiple threads commands

## expand (byte) (block)
Run code at %2(block) for expansion number %1(byte)

## multirun (block)
Run simultaneously code at %1(block).

# Miscellaneous commands

## create_nuke
Create a nuke. Should only be used in campaign scripts.

## create_unit (unit) (word) (word)
Create %1(unit) at map position (x,y) where x = %2(word) and y = %3(word). Should only be used in campaign scripts.

## creep (flag)
Builds structures(towers?) far if the flag is set to 4, or near if the flag is anything else.
The creep command is used for expanding the zerg creep.

## debug (block) (string)
Show debug string %2(string) and continue in %1(block). (unsupported by scAIEditIII)

## define_max (byte) (unit)
Define maximum number of %2(unit) to %1(byte).

## fatal_error
Crashes starcraft with a fatal error and the message "Illegal AI script executed.".

## give_money
Gives 2000 ore if ore is currently below 500 and gives 2000 gas if gas is currently below 500. This is executed immediately, the AI does not wait until it falls below 500 resources. This will be skipped entirely of no resource is below 500.

## nuke_pos (word) (word)
Launch a nuke at map position (x,y) where x = %1(word) and y = %2(word). Should only be used in campaign scripts.

## nuke_rate (byte)
Builds and uses nukes every %1(byte) minutes.

## send_suicide (byte)
Send all units to suicide mission. %1(byte) determines which type: 0 = Strategic suicide; 1 = Random suicide.
* 1 = includes workers too.

## set_randomseed (dword)
Set random seed to %1(dword). Note: This affects other scripts and should not be used.

# StarEdit commands

## clear_combatdata
Clears all AI attack data for all units in the location.

## disruption_web
Orders a Protoss Corsair to cast Disruption Web in the location.

## enter_bunker
Orders units in the location to enter the closest bunker.

## enter_transport
Orders units in the location to enter the closest transport.

## exit_transport
Orders transports in the location to unload their units.

## harass_location
AI Harass at selected location. (Needs definition)

## junkyard_dog
Orders the unit to run on "Junk Yard Dog" (similar to critter).

## make_patrol
Orders the units to patroll to the Generic Command Target.

## move_dt
Orders the computer to move all Dark Templars to the specified region.

## nuke_location
Orders a computer player to nuke the selected location.

## player_ally
Makes all players in a specified location an ally of the trigger owner.

## player_enemy
Makes all players in a specified location an enemy of the trigger owner.

## recall_location
Orders an Arbiter to use recall at this location.

## sharedvision_off (player)
Orders the specified player to unvision the trigger owner.

## sharedvision_on (player)
Orders the specified player to give vision to the trigger owner.

## value_area
Causes the computer to value a specified area higher than any other area. It may guard the area with units.

# Unused commands

## if_towns
Does not exist in memory.

## scout_with (military)
This command has no action associated with it and therefore cannot be used.

#  List of unknown or unclear commands 
Unknown purpose commands
Note: These are the most interesting commands to make research on. With the accurate opcode name list, they're now easier to decipher, but many still don't act as expected, or are still too obscure. 

## allies_watch (byte) (block)
Expands at hardcoded expansion number %1 (byte) using %2 (block). Note: If %1 is < 8 then it is a player's start location, otherwise it is a map's base location. Does nothing if the expansion is occupied. The maximum value for %1 (byte) is 250.

## capt_expand
Causes the AI to expand using a default expansion block. Takes no parameter.
The actual expansion block is unknown and needs research.

## default_min (byte)
Defines how much standing army (from defenseuse commands) will be placed at expansions. The greater the value, more units will be sent. If (byte) = 0, then it will send units only if the expansion is under attack

## defaultbuild_off
Turns off default_build. Note: "default build" is on by default.

## fake_nuke
Resets the AI nuke timer. Behaviour is unknown.

## max_force (word)
Takes %1(word) as parameter. Unknown.

## panic (block)
If AI has not expanded yet and total unmined minerals in the mineral line are less than 7500, then it will expand using (block). If the AI has expanded before, the command triggers every time there are less than 7500 unmined minerals total in all owned bases, or there are less than 2 owned Refineries that are not depleted.

## region_size (byte) (block)
Jump to block %2 if the computer's region tile count is below %1. Untested.

## set_attacks (byte)
The use of this command is unknown. Takes %1(byte) as parameter.

## target_expansion
The use of this command is unknown. Takes no parameter.
appeared in vanilla SC scripts. Looks like was a general "attack" command not necessarily expansions.
Update: This only sets a flag. The actual effects from that flag are unknown.
Update2: Only used with set_attacks, does nothing if the start_campaign opcode was executed.

## build_bunkers
Builds up to 3 bunkers around the base (Terran only). Takes no parameters.

## build_turrets
Builds up to 6 missile turrets around the base (Terran only). Takes no parameters.

## default_build
If the AI has more than 600 minerals and 300 gas, it will continuously train race specific units until it reaches the define_max value.
Terran: marine, ghost, siege tank, goliath, wraith, battlecruiser.
Zerg: hydralisk, mutalisk.
Protoss: zealot, dragoon, reaver, scout, carrier.

Note: "default build" is on by default. To turn it off, use defaultbuild_off

## easy_attack (byte) (unit)
The definition of this command is unknown. Supposedly attacks the enemy with %1 units of type %2 without having to do attack_add, attack_prepare, and attack_do.

## eval_harass (block)
Jumps to a block when an unknown condition related to the town and attack manager are met. Also uses enemy unit ground/air strength values to compare with something.

## harass_factor (word)
Duplicates/triplicates the current attack group of the attack manager, depending on the <word> value and the nearest enemy player.

This command does the following:

- Find the owner of the closest non-allied unit near the current script's region.
- Calculate the sum of strengths of all enemy units that are owned by the player found in step 1.
- Compares the sum of enemy strength with the <word>value:
    - If the total enemy strength is more than the double of the <word> value, duplicates the attack group of the current AI.
    - If the total enemy strength is more than the triple of the <word> value, triplicates the attack group of the current AI.
    - Otherwise, the command does nothing.

The number of units in the duplicated/triplicated attack group cannot exceed the attack group maximum size (64 units).

## if_dif (byte) (byte) (block)
Jumps to block %3 if value %2 is different than an unknown internal value (related to attacking?), using modifier %1(0 = greater than, 1 = less than).

## implode
The definition of this command is unknown. Takes no parameter.

## quick_attack
Supposedly perform an attack quickly without preparing it. (?) Takes no parameter.

## wait_bunkers
Supposedly waits for the command build_bunkers to finish. Takes no parameters.

## wait_secure
The definition of this command is unknown. Takes no parameters.

## wait_turrets
Supposedly waits for the command build_turrets to finish. Takes no parameters.

## wait_upgrades
Waits for all upgrades and research to finish. Takes no parameter.

More information may be available on the BroodwarAI wiki:

http://www.broodwarai.com/forums/index.php?showtopic=11&st=0