import struct

triggers = ''
trigger_start = """
Trigger {
   players={P1},
   actions={
"""
trigger_end = """
       PreserveTrigger();
   }
}
"""

with open('build/aiscript.bin', 'rb') as aiscript:
  next = aiscript.read(4)
  ints = []

  while(next):
    # Null pad
    next = (next + b'\x00\x00\x00\x00')[0:4]

    value = struct.unpack('i', next)[0]

    ints.append(value)

    # Null pad next result
    next = aiscript.read(4)

  actions_per_trigger = 31
  triggers += trigger_start

  for (i, value) in enumerate(ints):
    triggers += '       SetDeaths(CurrentPlayer, SetTo, %d, %d);SetMemory(0x6509B0, Add, 1);\n' % (value, (0))

    if (i % actions_per_trigger == actions_per_trigger - 1):
      triggers += trigger_end.replace('{{ offset }}', str(actions_per_trigger))
      triggers += trigger_start
    
  triggers += trigger_end.replace('{{ offset }}', str(actions_per_trigger))

with open('docs/eud.trg') as template:
  content = template.read().replace('{{ write_actions }}', triggers)

  with open('build/trigs.trg','w') as out:
    out.write(content)