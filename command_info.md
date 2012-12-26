# Header commands

## farms_notiming
Build necessary farms only when it hits the maximum supply available.

## farms_timing
Build necessary farms with a correct timing, so nothing is paused by a maximum supply limit hit.

## start_areatown
Starts the AI Script for area town management.

## start_campaign
Starts the AI Script for Campaign.

## start_town
Starts the AI Script for town management.

## transports_off
Computer will not manage/build transports on its own.

## check_transports
Informs computer to use transports up to the defined Max#. Used with header transports_off.
* was noted in old forum that 5 was max transport. Needs to be confirmed.

# Build/Attack/Defense order commands

## attack_add (byte) (military)
Add %1(byte) %2(military) to the current attacking party.

## attack_clear
Clear the attack data.

## attack_do
Attack the enemy with the current attacking party.

## attack_prepare
Prepare the attack.

## build (byte) (building) (byte)
Build %2(building) until it commands %1(byte) of them, at priority %3(byte).

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
Send units of type %1(military) to guard as many resources spots as possible(1 per spot).

## place_guard (unit) (byte)
Place %2(byte) guards using %1(unit) to guard town. 
* index starts at 0 for first guard
for example place_guard medic 0 = place 1 medic to guard town.

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
Research upgrade %2(upgrade) up to level %1(byte), at priority %3(byte).

## wait (word)
Wait for %1(word) tenths of second in normal game speed.
* NOTE normal game speed. Fastest game speed is still undetermined.
see this post for further details.

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
Call %1(block) as a sub-routine. Only one call can be made in the game at a time.
If an AI owned by player 1 makes a call, then player 2 makes a call, will override player 1's call and controls the flow of the return statement.
Be sure that there is no wait command inside the call to have it function correctly.

## enemyowns_jump (unit) (block)
If enemy has a %1(unit), jump to %2(block).

## enemyresources_jump (word) (word) (block)
If enemy has at least %1(word) minerals and %2(word) gas then jump in %3(block).

## goto (block)
Jump to %1(block).

## groundmap_jump (block)
If it is a ground map(in other words, if the enemy is reachable without transports), jump to %1(block).

## if_owned (unit) (block)
If the player owns a %1(unit) (includes incomplete) then jump to %2(block).

## killable
Allows the current thread to be killed by another one.

## kill_thread
Kills all threads that have the killable attribute (including threads owned by other players).

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
see post #76 for updated conditions

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

## 
Miscellaneous commands

## create_nuke
Create a nuke. Should only be used in campaign scripts.

## create_unit (unit) (word) (word)
Create %1(unit) at map position (x,y) where x = %2(word) and y = %3(word). Should only be used in campaign scripts.

## creep (flag)
Builds structures(towers?) far if the flag is set to 4, or near if the flag is anything else.
The creep command is used for expanding the zerg creep.

## debug (block) (string)
Show debug string %2(string) and continue in %1(block). (unsupported by scAIEditIII

## define_max (byte) (unit)
Define maximum number of %2(unit) to %1(byte).

## fatal_error
Crashes starcraft with a fatal error and the message "Illegal AI script executed.".

## give_money
Gives 2000 ore if ore is currently below 500 and gives 2000 gas if gas is currently below 500. This is executed immediately, the AI does not wait until it falls below 500 resources. This will be skipped entirely of no resource is below 500.

## nuke_pos (word) (word)
Launch a nuke at map position (x,y) where x = %1(word) and y = %2(word). Should only be used in campaign scripts.

## nuke_rate (byte)
Builds nukes every %1(byte) minutes.
*see post#27 for further details

## send_suicide (byte)
Send all units to suicide mission. %1(byte) determines which type: 0 = Strategic suicide; 1 = Random suicide.
* 1 = includes workers too.

## set_randomseed (dword)
Set random seed to %1(dword).

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

## 
List of unknown or unclear commands 
Unknown purpose commands
Note: These are the most interesting commands to make research on. With the accurate opcode name list, they're now easier to decipher, but many still don't act as expected, or are still too obscure. 

## allies_watch (byte) (block)
The use of this command is unknown. Takes %1(byte) and %2(block) as parameters.
Byte might represent expansion number.

## capt_expand
Causes the AI to expand using a default expansion block. Takes no parameter.
The actual expansion block is unknown and needs research.

## default_min (byte)
The use of this command is unclear. Takes %1(byte) as parameter.
Racine used this command in our BWARAi War I.
see his scripts in this post for more details:
BWAi War I
Update/Suggestion: perhaps it specifies minimum number of expansions to acquire

## defaultbuild_off
The use of this command is unknown. Takes no parameter.
"default build" is on by default."

## fake_nuke
The use of this command is unknown. Takes no parameters.
Resets the AI nuke timer. Behaviour is unknown.

## max_force (word)
Takes %1(word) as parameter. Unknown.

## panic (block)
Appears to trigger (block) if attacked. Still unclear.

## region_size (byte) (block)
Jump to block %2 if the computer's region tile count is below %1. Untested.

## set_attacks (byte)
The use of this command is unknown. Takes %1(byte) as parameter.

## target_expansion
The use of this command is unknown. Takes no parameter.
appeared in vanilla SC scripts. Looks like was a general "attack" command not necessarily expansions.
Update: This only sets a flag. The actual effects from that flag are unknown.

## build_bunkers
Supposedly builds bunkers. Takes no parameters.

## build_turrets
Supposedly builds turrets. Takes no parameters.

## default_build
The use of this command is unknown. Takes no parameter.
"default build" is on by default."

## easy_attack (byte) (unit)
The definition of this command is unknown. Supposedly attacks the enemy with %1 units of type %2 without having to do attack_add, attack_prepare, and attack_do.

## eval_harass (block)
Jumps to a block when an unknown condition related to the town and attack manager are met. Also uses enemy unit ground/air strength values to compare with something.

## harass_factor (word)
Something related to unit strengths in a region.

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
Supposedly waits for all upgrades to finish. Takes no parameter.

http://www.broodwarai.com/forums/index.php?showtopic=11&st=0
