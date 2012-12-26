A Brood War AI preprocessor. This uses pyAI to build the scripts in aiscript.bin and bwscript.bin.

# New AI commands/macros:

## build_start(amount, building, [priority])

Builds {amount} of {building} at {priority} and waits for construction to start. Priority defaults to 80.

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