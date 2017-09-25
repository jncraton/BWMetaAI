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

# Stagnant AI

## Supply capped

## Define_max statement conflict

## Wrong race

## Mixed up build/train command