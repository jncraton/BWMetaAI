import shutil

trigger_gap = 2400
write_gap = 64
writes_per_trig = 31

maps = [
  ('(1)Destination BWMetaAI P.scx',  0x74be2),
  ('(1)Destination BWMetaAI T.scx',  0x74be4),
  ('(1)Destination BWMetaAI Z.scx',  0x74bb3),
]

def write_map(map_filename, offset):
  print('Writing aiscript.bin to EUD triggers in %s' % map_filename)
  shutil.copy('tools/' + map_filename, 'build/' + map_filename)
  with open('build/aiscript.bin', 'rb') as aiscript:
    with open ('build/' + map_filename, 'r+b') as map:
      i = 0
      while (1):
        map.seek(offset + trigger_gap * i)

        for _ in range(0,writes_per_trig):
          value = aiscript.read(4)
          if not value:
            return
          map.write(value)
          map.seek(write_gap - 4, 1)
        i += 1
        
for map, offset in maps:
  write_map(map, offset)