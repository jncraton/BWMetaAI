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
Waits for all upgrades and research to finish. Takes no parameter.

http://www.broodwarai.com/forums/index.php?showtopic=11&st=0


From BWAI wiki:

==Header commands==
===farms_notiming===
:Build necessary farms only when it hits the maximum supply available.

===farms_timing===
:Build necessary farms with a correct timing, so nothing is paused by a maximum supply limit hit.

===start_areatown===
:Starts the AI Script for area town management. Should only be used in campaign scripts, as it uses the trigger location as its bounds (or area).

===start_campaign===
:Starts the AI Script for Campaign. 
:Note: This command may have many subtle (but significant in number) changes to AI behaviour which may be desirable in some cases, but not in others.

===start_town===
:Starts the AI Script for town management.

===transports_off===
:Computer will not manage/build transports on its own.

===check_transports===
:Informs computer to build transports on its own. If start_campaign was called, then 2 transports will be built, otherwise 5 will be built. The first transport is built at priority 80 and subsequent transports are built at priority 50. Protoss also trains up to 2 observers at priority 80. Used with header transports_off.


== General build order commands ==
The commands in this category manage the construction of buildings, training of workers, and researching tech and upgrades. Oddly enough, StarCraft uses the same AI manager for buildings and workers, while normal melee units (AKA military) are controlled by the military manager.

=== build ===
 build <count> <building> <priority>

Adds "Construct <tt><count></tt> number of <tt><building></tt> at <tt><priority></tt>" to the AI's town queue. This makes the AI build the <tt><building></tt> until it commands <tt><count></tt> of them.

This command does not wait for the actual construction to begin.

Morphed buildings (Lair, Hive, Greater Spire, etc) also count as their base building types (Hatchery, Spire, etc.).

Unlike the [[#player_need|player_need]] command, this only checks for units in the current town to see if the player already has enough of <tt><building></tt>.

If <tt><count></tt> is bigger than 30, this command is ignored.

<span style="color:green">In BWScriptEmulator this limitation will be removed.</span>

=== player_need ===
 player_need <count> <building>

Adds "Construct <tt><count></tt> number of <tt><building></tt> at priority 80" to the AI's town queue. This makes the AI build the <tt><building></tt> until it commands <tt><count></tt> of them.

This command does not wait for the actual construction to begin. 

Unlike the [[#build|build]] command, this checks all owned units to see if the player already has enough of <tt><building></tt>. Also, morphed buildings (Lair, Hive, Greater Spire, etc) do ''not'' count as their base building types (Hatchery, Spire, etc.).

Note: The AI will often hastily build more than 1 building when <tt>player_need</tt> is used.

If <tt><count></tt> is bigger than 30, this command is ignored.

=== wait_build ===
 wait_build <byte> <building>

Pause script execution until the AI has <tt><byte></tt> of <tt><building></tt> in the current town. Units/buildings in production are not counted.

Morphed buildings (Lair, Hive, Greater Spire, etc) also count as their base building types (Hatchery, Spire, etc.).

If <tt><building></tt> is a worker, the AI checks the appropriate maximum worker amount of the current town. The maximum amount of workers per base is:

 (max number of workers per base) = (mineral line worker max) + 3 x (number of gas geysers in base)
 
 Where (mineral line worker max) is equal to:
 
 if (total mineral in base) / 500 < (number of mineral patches in all of the player's bases)
   (mineral line worker max) = (number of mineral patches in base)
 else
   (mineral line worker max) = 2 x (number of mineral patches in base)
     or
   (mineral line worker max) = (total mineral in base) / 500, whichever is smaller

=== wait_buildstart ===
 wait_buildstart <byte> <building>

Pause script execution until the AI has <tt><byte></tt> of <tt><building></tt> in the current town, counting units/buildings in production.

Morphed buildings (Lair, Hive, Greater Spire, etc) also count as their base building types (Hatchery, Spire, etc.).

If <tt><building></tt> is a worker, the AI checks the appropriate maximum worker amount of the current town. See '''[[#wait_build|wait_build]]''' for the maximum worker count per base.

=== get_oldpeons ===
 get_oldpeons <count>

Retrieves <count> number of workers from other towns to the current town. The number of workers brought to the town cannot exceed the maximum worker-per-town limit.

The AI attempts to retrieve workers from the main town. If this command is used in the main town, or the main town does not have enough workers, the AI will bring workers from other expansions as well.

=== tech ===
 tech <technology> <priority>

Adds "Research <tt><technology></tt> at <tt><priority></tt>" to the AI's town queue.

This command does not wait for the actual research to begin.

=== upgrade ===
 upgrade <byte> <upgrade> <priority>

Adds "Research <tt><upgrade></tt> until <tt><byte></tt> level is reached, at <tt><priority></tt>" to the AI's town queue.

This command does not wait for the actual research to begin.

The maximum supported upgrade level is 31.

<span style="color:green">In BWScriptEmulator this limitation will be removed.</span>

==Military training commands==

All military training commands are global; they check units in all towns, not just the ones in the current town, and the actual training can take place in any town that has the appropriate production building.

=== train ===
 train <byte> <military>

Tells the AI to train <tt><military></tt> until it has at least <tt><byte></tt> of them, including those in production.

This command is similar to '''[[#wait_force|wait_force]]''', but it also counts units that are being trained or morphed.

=== wait_force ===
 wait_force <byte> <military>

Tells the AI to train <tt><military></tt> until it has at least <tt><byte></tt> of them. Units in production are not counted.

This command is similar to '''[[#train|train]]''', except that it only checks units that have been completed.

This command is similar to '''[[#do_morph|do_morph]]''', except that it waits for the unit(s) to be built.

=== do_morph ===
 do_morph <byte> <military>

Tells the AI to train one of <tt><military></tt> if it does not have at least <tt><byte></tt> of them. Units in production are not counted. If a '''[[#define_max|define_max]]''' has been specified for <military> that is lower than <byte>, the define_max's limit will be obeyed.

This command is similar to '''[[#wait_force|wait_force]]''', but it does not wait for the unit(s) to be built, and only builds one unit.

Note: The name of this command is a misnomer, as it works on any type of military (not just Zerg).

=== wait_train ===
<code>wait_train <byte> <unit></code>

Wait until computer commands <tt><byte></tt> of <tt><unit></tt>. Units in production are not counted towards the total..

== Military attack commands ==

=== attack_add ===
 attack_add <byte> <military>

Adds <tt><byte></tt> number of <tt><military></tt> to the current attack group. If <tt><byte></tt> is bigger than 62, this command is ignored.

Each AI player has one global attack group that can hold up to 64 units.

<span style="color:green">In BWScriptEmulator the 62-unit limitation will be removed.</span>

===attack_clear===
:Clear the attack data.

===attack_do===
:Attack the enemy with the current attacking party.

===attack_prepare===
:Prepare the attack.

=== prep_down ===
 prep_down <save_count> <min_count> <military>

Adds a number of <tt><military></tt> to the current attack group. The number of units added is guaranteed to be at least <tt><min_count></tt>; if possible, the AI will save up to <tt><save_count></tt> number of units and add all remaining units to the attack group.

See also: [[#attack_add|attack_add]]

===wait_finishattack===
:Wait until attacking party has finished to attack.

== Defense commands ==

These commands tell the AI how to react when its units are under attack. Each AI player maintains 8 sets of defense groups:

* DefenseBuild_GG: List of unit types to build when enemy ground units are attacking the AI's ground units.
* DefenseBuild_GA: List of unit types to build when enemy ground units are attacking the AI's air units.
* DefenseBuild_AG: List of unit types to build when enemy air units are attacking the AI's ground units.
* DefenseBuild_AA: List of unit types to build when enemy air units are attacking the AI's air units.
* DefenseUse_GG: List of unit types to use for defense when enemy ground units are attacking the AI's ground units.
* DefenseUse_GA: List of unit types to use for defense when enemy ground units are attacking the AI's air units.
* DefenseUse_AG: List of unit types to use for defense when enemy air units are attacking the AI's ground units.
* DefenseUse_AA: List of unit types to use for defense when enemy air units are attacking the AI's air units.

Each defense group can hold up to 20 unit types (including multiple units of the same type). Any unit types added after reaching this limit are ignored, unless the defense group is cleared with defenseclear_XX commands.

=== defensebuild_gg ===
 defensebuild_gg <count> <military>

Adds <tt><count></tt> number of <tt><military></tt> to the DefenseBuild_GG group. If <tt><count></tt> is bigger than 10, this command is ignored.

=== defensebuild_ga ===
 defensebuild_ga <count> <military>

Adds <tt><count></tt> number of <tt><military></tt> to the DefenseBuild_GA group. If <tt><count></tt> is bigger than 10, this command is ignored.

=== defensebuild_ag ===
 defensebuild_ag <count> <military>

Adds <tt><count></tt> number of <tt><military></tt> to the DefenseBuild_AG group. If <tt><count></tt> is bigger than 10, this command is ignored.

=== defensebuild_aa ===
 defensebuild_aa <count> <military>

Adds <tt><count></tt> number of <tt><military></tt> to the DefenseBuild_AA group. If <tt><count></tt> is bigger than 10, this command is ignored.

=== defenseuse_gg ===
 defenseuse_gg <count> <military>

Adds <tt><count></tt> number of <tt><military></tt> to the DefenseUse_GG group. If <tt><count></tt> is bigger than 10, this command is ignored.

=== defenseuse_ga ===
 defenseuse_ga <count> <military>

Adds <tt><count></tt> number of <tt><military></tt> to the DefenseUse_GA group. If <tt><count></tt> is bigger than 10, this command is ignored.

=== defenseuse_ag ===
 defenseuse_ag <count> <military>

Adds <tt><count></tt> number of <tt><military></tt> to the DefenseUse_AG group. If <tt><count></tt> is bigger than 10, this command is ignored.

=== defenseuse_aa ===
 defenseuse_aa <count> <military>

Adds <tt><count></tt> number of <tt><military></tt> to the DefenseUse_AA group. If <tt><count></tt> is bigger than 10, this command is ignored.

=== defenseclear_gg ===
 defenseclear_gg

Clears the DefenseBuild_GG and DefenseUse_GG defense groups.

=== defenseclear_ga ===
 defenseclear_ga

Clears the DefenseBuild_GA and DefenseUse_GA defense groups.

=== defenseclear_ag ===
 defenseclear_ag

Clears the DefenseBuild_AG and DefenseUse_AG defense groups.

=== defenseclear_aa ===
 defenseclear_aa

Clears the DefenseBuild_AA and DefenseUse_AA defense groups.

===guard_all===
:forces AI to defend all defensive structures and units around the map. In Campaign scripts, where pre-placed units and building are common, if said units (or buildings) are outside the perimeter of a base and are attacked, they will be ignored (the AI will not send units to defend them). By using guard_all all these units will be defended if attacked. The command identifies the locations which must be defended at the moment it is run in the script. Units or structures built after that do not count. Each location (unit or structure) that must be defended is considered as potential overlord/observer patrol point and/or spider mine placement spot.

===guard_resources (military)===
:Send units of type %1(military) to guard as many unacquired base locations as possible(1 per spot).

===place_guard (unit) (byte)===
:Place one %1(unit) to guard town at strategic location %2.
:0 = town center
:1 = mineral line
:2 = geyser/refinery


==Flow control commands==

===wait (word)===
:Wait for %1(word) logical game frames. A game frame is 67 milliseconds on normal game speed (about 15 FPS), and 42 milliseconds on fastest game speed (about 24 FPS).

===enemyowns_jump (unit) (block)===
:If enemy has a %1(unit), jump to %2(block).

===enemyresources_jump (word) (word) (block)===
:If enemy has at least %1(word) minerals and %2(word) gas then jump in %3(block).

===goto (block)===
:Jump to %1(block).

=== groundmap_jump ===
 groundmap_jump <block>

Jumps to <tt><block</tt> if there is a non-allied building on the map that can be reached by ground from the current town.

=== if_owned ===
 if_owned <unit> <block>

If the AI has a <tt><unit></tt>, jumps to <tt><block></tt>. This includes units in production (except for Zerg building-to-building morph and unit-to-unit morph).

Morphed buildings (Lair, Hive, Greater Spire, etc) do ''not'' count as their base building types (Hatchery, Spire, etc.). 

This command has the opposite effect of '''[[#notowns_jump|notowns_jump]]'''.

=== notowns_jump ===
 notowns_jump <unit> <block>

If the AI does not have a <tt><unit></tt>, jumps to <tt><block></tt>. This includes units in (except for Zerg building-to-building morph and unit-to-unit morph).

Morphed buildings (Lair, Hive, Greater Spire, etc) do ''not'' count as their base building types (Hatchery, Spire, etc.). 

This command has the opposite effect of '''[[#if_owned|if_owned]]'''.

=== race_jump ===
 race_jump <block_t> <block_z> <block_p>

Searches for an enemy unit that is nearest to the current town. If the enemy unit is Terran, jumps to <tt><block_t></tt>. If it is Zerg, jumps to <tt><block_z></tt>. If it is Protoss, jumps to <tt><block_p></tt>.

If there are no enemy units on the map, jumps to <tt><block_t></tt>.

=== random_jump ===
 random_jump <byte> <block>

Compares <tt><byte></tt> to a random number between 0 and 255. If the <tt><byte></tt> is same or bigger than the random number, jumps to <tt><block></tt>.

Effectively, this performs a jump with a chance of <tt>(<byte> + 1) / 256</tt>.

===resources_jump (word) (word) (block)===
:If computer has at least %1(word) minerals and %2(word) gas then jump in %3(block).

===[[Rush|rush (byte) (block)]]===
:will jump to %2(block) if %1(byte) conditions exist.

===time_jump (byte) (block)===
:Jumps to %2(block) if %1(byte) normal game minutes have passed in the game.

=== try_townpoint ===
 try_townpoint <byte> <block>

Jumps to <tt><block></tt> if the AI has exactly <tt><byte></tt> number of expansions (including the main base).

===stop===
:Stop script code execution. Often used to close script blocks called simultaneously.

===call (block)===
:Call %1(block) as a sub-routine. Only one call can be made in the game at all times from any computer player running a script.
:If an AI owned by player 1 makes a call, then player 2 makes a call, will override player 1's call and controls the flow of the return statement.
:Be sure that there is no wait command or blocking command inside the call to have it function correctly.
:<span style="color:green">In BWScript Emulator, this command will be fixed and function as it was intended.</span>

===return===
:Return to the flow point of the call command.

===killable===
:Allows the current thread to be killed by another one.

===kill_thread===
:Kills all threads that have the killable attribute (including threads owned by other players). This should not be used in a script.

==Multiple threads commands==

=== expand ===
 expand <byte> <block>

If the number of expansions owned by the AI (including the main base) is same or less than <tt><byte></tt>, attempts to create an expansion using the script at <tt><block></tt>.

In non-UMS games, the AI will ignore this opcode if it has at least 5000 minerals and 3000 gas.

===multirun (block)===
:Run simultaneously code at %1(block).


==Miscellaneous commands==

===create_nuke===
:Create a nuke. Should only be used in campaign scripts.
:<span style="color:green">The BWScript Emulator cannot emulate this opcode. It will be ignored.</span>

===create_unit (unit) (word) (word)===
:Create %1(unit) at map position (x,y) where x = %2(word) and y = %3(word). Should only be used in campaign scripts.
:<span style="color:green">The BWScript Emulator cannot emulate this opcode. It will be ignored.</span>

===creep (flag)===
:Builds structures(towers?) far if the flag is set to 4, or near if the flag is anything else.
:The creep command is used for expanding the zerg creep.

===debug (block) (string)===
:Show debug string %2(string) and continue in %1(block). (unsupported by scAIEditIII)
:<span style="color:green">The BWScript Emulator will send the string as a text message to all players.</span>

=== define_max ===
 define_max <byte> <military>

Sets a global limit of trainable unit <military> to <byte>.

Note: Setting <byte> to 255 will disallow that <military> unit's production

===fatal_error===
:Crashes starcraft with a fatal error and the message "Illegal AI script executed."
:<span style="color:green">In BWScript Emulator, this will simply send the text message "Illegal AI script executed".</span>

===give_money===
:Gives 2000 ore if ore is currently below 500 and gives 2000 gas if gas is currently below 500. This is executed immediately, the AI does not wait until it falls below 500 resources. This will be skipped entirely if no resource is below 500.
:<span style="color:green">In BWScript Emulator, this will use the cheat codes "whats mine is mine" and "breathe deep" four times in a row under the same conditions. This will not work in multiplayer.</span>

===nuke_pos (word) (word)===
:Launch a nuke at map position (x,y) where x = %1(word) and y = %2(word). Should only be used in campaign scripts.

===nuke_rate (byte)===
:Builds and uses nukes every %1(byte) minutes.
:determines the time in minutes between ordering a single ghost to use Nuclear Strike, provided there are a Ghost and a Nuke available.  The AI may have more than 10 Nukes, but will still order Nuclear Strikes one at a time. Since the timer resets when the Ghost is ordered, and not when the Nuke actually launches, it is possible, with low timer to have multiple Nuclear Strikes.  Default value is "0", and fake_nuke resets the timer whenever it is entered in the script. The Nuke is aborted if the ghost is disabled in any way during his way (not yet painting the target) - if killed, under stasis field/maelstrom... or if the ghost must board a transport to reach the destination (Note that if a target is available when landing it may still proceed with the Nuke).

===send_suicide (byte)===
:Send all units to suicide mission. %1(byte) determines which type: 0 = Strategic suicide; 1 = Random suicide.
:* 1 = includes workers too.

===set_randomseed (dword)===
:Set random seed to %1(dword). Note: This affects other scripts and should not be used.

==StarEdit commands==

===clear_combatdata===
:Clears all AI attack data for all units in the location.

===disruption_web===
:Orders a Protoss Corsair to cast Disruption Web in the location.

===enter_bunker===
:Orders units in the location to enter the closest bunker.

===enter_transport===
:Orders units in the location to enter the closest transport.

===exit_transport===
:Orders transports in the location to unload their units.

===junkyard_dog===
:Orders the unit to run on "Junk Yard Dog" (similar to critter).

===make_patrol===
:Orders the units to patroll to the Generic Command Target.

===move_dt===
:Orders all Dark Templar(Hero) to attack-move to the specified region.

===nuke_location===
:Orders a computer player to nuke the selected location.

===player_ally===
:Makes all players in a specified location an ally of the trigger owner.

===player_enemy===
:Makes all players in a specified location an enemy of the trigger owner.

===recall_location===
:Orders an Arbiter to use recall at this location.

===sharedvision_off (player)===
:Orders the specified player to unvision the trigger owner.
:<span style="color:green">The BWScript Emulator cannot emulate this opcode, however it can emulate the inverse, and the current player will unvision the specified player.</span>

===sharedvision_on (player)===
:Orders the specified player to give vision to the trigger owner.
:<span style="color:green">The BWScript Emulator cannot emulate this opcode, however it can emulate the inverse, and the current player will share vision with the specified player.</span>

===value_area===
:Causes the computer to value a specified area higher than any other area. It may guard the area with units.



==Unused commands==

===if_towns===
:Does not exist in memory.

=== scout_with ===
 scout_with <military>

This command does nothing; it has no action associated with it.

<span style="color:green">In the BWScript Emulator, this command will correctly send the given military to scout the enemy.</span>

=== harass_location ===
 harass_location

This command does nothing; it has no action associated with it.
<!-- Old description says: AI Harass at selected location. (Needs definition) -->

=== easy_attack ===
 easy_attack <byte> <military>

Adds <tt><byte></tt> of <tt><military></tt> to the current attack group. Because this command checks some sort of debug flag that has been disabled in the current version of StarCraft, it actually does nothing.

See also: [[#attack_add|attack_add]]


==List of unknown or unclear commands==
Note: These are the most interesting commands to make research on. With the accurate opcode name list, they're now easier to decipher, but many still don't act as expected, or are still too obscure. 

=== allies_watch ===
 allies_watch <byte> <block>

Expands at the base with ID = <tt><byte></tt>, using AI script code at <tt><block></tt>. If the expansion is already occupied, it does nothing.

Note: Base IDs are assigned to potential bases on game start. Player start locations receive ID values between 0 and 7, while expansions are automatically numbered. The maximum value for <tt><byte></tt> is 250.

===capt_expand===
:Causes the AI to expand using a default expansion block. Takes no parameter.
:The actual expansion block is unknown and needs research.

===default_min (byte)===
:Defines how much standing army (from defenseuse commands) will be placed at expansions. The greater the value, more units will be sent. If (byte) = 0, then it will send units only if the expansion is under attack

===defaultbuild_off===
:Turns off default_build. Note: "default build" is on by default.

===fake_nuke===
:Resets the AI nuke timer. Behaviour is unknown.

===max_force (word)===
:Takes %1(word) as parameter. Unknown.

===panic (block)===
:If AI has not expanded yet and total unmined minerals in the mineral line are less than 7500, then it will expand using (block). If the AI has expanded before, the command triggers every time there are less than 7500 unmined minerals total in all owned bases, or there are less than 2 owned Refineries that are not depleted.

===region_size (byte) (block)===
:Jump to block %2 if the computer's region tile count is below %1. Untested.

===set_attacks (byte)===
:The use of this command is unknown. Takes %1(byte) as parameter.

===target_expansion===
:The use of this command is unknown. Takes no parameter.
:appeared in vanilla SC scripts. Looks like was a general "attack" command not necessarily expansions.
:Update: This only sets a flag. The actual effects from that flag are unknown.
:Update2: Only used with set_attacks, does nothing if the start_campaign opcode was executed.

===build_bunkers===
:Builds up to 3 bunkers around the base (Terran only). Takes no parameters.

===build_turrets===
:Builds up to 6 missile turrets around the base (Terran only). Takes no parameters.

===default_build===
:If the AI has more than 600 minerals and 300 gas, it will continuously train race specific units until it reaches the define_max value.
:Terran: marine, ghost, siege tank, goliath, wraith, battlecruiser.
:Zerg: hydralisk, mutalisk.
:Protoss: zealot, dragoon, reaver, scout, carrier.

:Note: "default build" is on by default. To turn it off, use defaultbuild_off

===eval_harass (block)===
:Jumps to a block when an unknown condition related to the town and attack manager are met. Also uses enemy unit ground/air strength values to compare with something.

=== harass_factor ===
 harass_factor <word>

Duplicates/triplicates the current attack group of the attack manager, depending on the <tt><word></tt> value and the nearest enemy player.

This command does the following:

# Find the owner of the closest non-allied unit near the current script's region [NEEDS VERIFICATION].
# Calculate the sum of strengths of all enemy units that are owned by the player found in step 1.
# Compares the sum of enemy strength with the <tt><word></tt> value:
## If the total enemy strength is more than the double of the <tt><word></tt> value, duplicates the attack group of the current AI.
## If the total enemy strength is more than the triple of the <tt><word></tt> value, triplicates the attack group of the current AI.
## Otherwise, the command does nothing.

The number of units in the duplicated/triplicated attack group cannot exceed the attack group maximum size (64 units).

===if_dif (byte) (byte) (block)===
:Jumps to block %3 if value %2 is different than an unknown internal value (related to attacking?), using modifier %1(0 = greater than, 1 = less than).

===implode===
:The definition of this command is unknown. Takes no parameter.

===quick_attack===
:Supposedly perform an attack quickly without preparing it. (?) Takes no parameter.

===wait_bunkers===
:Supposedly waits for the command build_bunkers to finish. Takes no parameters.

===wait_secure===
:The definition of this command is unknown. Takes no parameters.

===wait_turrets===
:Supposedly waits for the command build_turrets to finish. Takes no parameters.

===wait_upgrades===
:Waits for all upgrades and research to finish. Takes no parameter.
