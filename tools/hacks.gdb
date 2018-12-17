info inferior

# This should be the locations of the string "LastReplay" in memory
print *(char*)0x004FF900

# This should be the location of the current game speed
print *(int*)0x006CDFD4

# This should be the number of milliseconds between frames at each game speed
# {167, 111, 83, 67, 56, 48, 42}
print *(int*)0x005124D8@7

# We'll leave normal, fast, faster, and fastest alone
# We'll make slow 2x, slower 4x, and and slowest 16x

# Let's set slowest game speed to the fastest speed possible
set {int}0x005124D8=3
set {int}0x005124DC=10
set {int}0x005124E0=21

# Print our new speed values
print *(int*)0x005124D8@7
