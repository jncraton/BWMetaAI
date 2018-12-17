info inferior

# This should be the locations of the string "LastReplay" in memory
print *(char*)0x004FF900

# This should be the location of the current game speed
print *(int*)0x006CDFD4

# This should be the number of milliseconds between frames at slowest game speed
print *(int*)0x005124D8

# Let's set slowest game speed to the fastest speed possible
set {int}0x005124D8=1
