info inferior
print *(char*)0x004FF900
print *(int*)0x006CDFD4
print *(int*)0x005124D8

set {int}0x005124D8=1

print *(int*)0x005124F4

