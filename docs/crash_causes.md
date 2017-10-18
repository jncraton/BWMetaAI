# Crash Causes

## Loops without wait

A loop without a wait command will cause BW to crash due to an
infinite loop.

Example:

    --foo--
    build(1, Pylon, 80)
    goto(foo)
    
## Simultaneous attack_do

Calling attack_do a second time before attack_clear will cause the 
game to crash.

The following example may cause a crash:

    multirun(second_attack)
    attack_add(1, Dragoon)
    attach_do()
    attack_clear()
    stop()
    
    --second_attack--
    attack_add(1, Zealot)
    attach_do()
    attack_clear()
    stop()

## wait_train

Train followed by wait_train could cause a hang if a unit is killed between the commands.

## Multithreaded upgrades

# Buggy AI

## 100 Request Limit

No more than 100 build, tech, and upgrade requests can be issued for a single town. Overflowing this limit causes commands to be issued in other towns and creates very buggy behavior. Loops should not contain these commands or bugs will eventually occur.

# Stagnant AI

## Supply capped

## Define_max statement conflict

## Wrong race

## Mixed up build/train command
