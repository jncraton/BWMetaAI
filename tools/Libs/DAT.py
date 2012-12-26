from utils import *
import TBL

import struct, os, re

DATA_REFERENCE = {
	'SelCircleSize.txt':'Selection Circle Sizes',
	'Rightclick.txt':'Right Click Actions',
	'Flingy.txt':'Flingy Entries',
	'Behaviours.txt':'Behaviours',
	'DamTypes.txt':'Damage Types',
	'Mapdata.txt':'Campaign Names',
	'Units.txt':'Default Units',
	'Remapping.txt':'Remapping',
	'DrawList.txt':'Draw Types', 
	'FlingyControl.txt':'Flingy Controlers',
	'Sprites.txt':'Default Sprites',
	'Animations.txt':'IScript Animations',
	'Orders.txt':'Default Orders',
	'IscriptIDList.txt':"IScript ID's",
	'Portdata.txt':'Default Campaign',
	'Weapons.txt':'Default Weapons',
	'UnitSize.txt':'Unit Sizes',
	'Techdata.txt':'Default Technologies',
	'ElevationLevels.txt':'Elevation Levels',
	'Images.txt':'Default Images',
	'Upgrades.txt':'Default Upgrades',
	'Explosions.txt':'Explosion Types',
	'Races.txt':'Races',
	'Icons.txt':'Icons',
	'Sfxdata.txt':'Sound Effects',
	'ShieldSize.txt':'Shield Sizes'
}

DATA_CACHE = {}
for d in DATA_REFERENCE.keys():
	f = open(os.path.join(BASE_DIR, 'Libs', 'Data', d),'r')
	DATA_CACHE[d] = [l.rstrip() for l in f.readlines()]
	f.close()

class UnitsDAT:
	format = [
		[[],1],
		[[],2],
		[[],2],
		#[Inclusive,Exclusive]
		[[106,202],2],
		[[],4],
		[[],1],
		[[],1],
		[[],2],
		[[],4],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],4],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[0,106],2],
		[[],2],
		[[],2],
		[[0,106],2],
		[[0,106],2],
		[[0,106],2],
		[[0,106],2],
		[[],2, 2],
		[[],2],
		[[106,202],2, 2],
		[[106,202],2],
		[[],2, 4],
		[[],2],
		[[],2],
		[[],2],
		[[],2],
		[[],2],
		[[],2],
		[[],2],
		[[],2],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],2],
		[[],2],
		[[],2],
		[[],1],
		[[],2]
	]
	labels = [
		'Graphics',
		'Subunit1',
		'Subunit2',
		'Infestation',
		'ConstructionAnimation',
		'UnitDirection',
		'ShieldEnable',
		'ShieldAmount',
		'HitPoints',
		'ElevationLevel',
		'Unknown',
		'Sublabel',
		'CompAIIdle',
		'HumanAIIdle',
		'ReturntoIdle',
		'AttackUnit',
		'AttackMove',
		'GroundWeapon',
		'MaxGroundHits',
		'AirWeapon',
		'MaxAirHits',
		'AIInternal',
		'SpecialAbilityFlags',
		'TargetAcquisitionRange',
		'SightRange',
		'ArmorUpgrade',
		'UnitSize',
		'Armor',
		'RightClickAction',
		'ReadySound',
		'WhatSoundStart',
		'WhatSoundEnd',
		'PissSoundStart',
		'PissSoundEnd',
		'YesSoundStart',
		'YesSoundEnd',
		'StarEditPlacementBoxWidth',
		'StarEditPlacementBoxHeight',
		'AddonHorizontal',
		'AddonVertical',
		'UnitSizeLeft',
		'UnitSizeUp',
		'UnitSizeRight',
		'UnitSizeDown',
		'Portrait',
		'MineralCost',
		'VespeneCost',
		'BuildTime',
		'Unknown1',
		'StarEditGroupFlags',
		'SupplyProvided',
		'SupplyRequired',
		'SpaceRequired',
		'SpaceProvided',
		'BuildScore',
		'DestroyScore',
		'UnitMapString',
		'BroodwarUnitFlag',
		'StarEditAvailabilityFlags'
	]
	flaglens = {
		'SpecialAbilityFlags':32,
		'StarEditGroupFlags':8,
		'StarEditAvailabilityFlags':16
	}
	longlabel = 26
	datname = 'units.dat'
	header = 'Unit'
	idfile = 'Units.txt'
	filesize = 19876
	count = 228
	def __init__(self, stat_txt=None):
		if stat_txt == None:
			stat_txt = os.path.join(BASE_DIR, 'Libs', 'MPQ', 'rez', 'stat_txt.tbl')
		if isstr(stat_txt):
			self.tbl = TBL.TBL()
			print stat_txt
			self.tbl.load_file(stat_txt)
		else:
			self.tbl = stat_txt
		self.entries = [[0] * len(self.labels) for _ in range(self.count)]
		if self.datname == 'units.dat':
			self.data = [
				[[self.dat_value,'Flingy'],''],
				[[self.dat_value,'Units'],''],
				[[self.dat_value,'Units'],''],
				[[self.dat_value,'Units'],''],
				[[self.dat_value,'Images'],''],
				[[None,''],''],
				[[None,''],''],
				[[None,''],''],
				[[None,''],''],
				[[self.info_value,'ElevationLevels'],''],
				[[None,''],'Old Movement?: 0x1,0x2,0x4,0x8,0x10,0x20,0x40,0x80 (Mine-safe)'],
				[[self.stattxt_value,'Sublabel'],''],
				[[self.dat_value,'Orders'],''],
				[[self.dat_value,'Orders'],''],
				[[self.dat_value,'Orders'],''],
				[[self.dat_value,'Orders'],''],
				[[self.dat_value,'Orders'],''],
				[[self.dat_value,'Weapons'],''],
				[[None,''],''],
				[[self.dat_value,'Weapons'],''],
				[[None,''],''],
				[[None,''],''],
				[[None,''],'Building,Addon,Flyer,Worker,Subunit,"Flying Building",Hero,"Regenerates HP","Animated Idle(?)",Cloakable,"Two Units in 1 Egg","Single Entity","Resource Depot","Resource Container","Robotic Unit",Detector,"Organic Unit","Requires Creep",Unused(?),"Requires Psi",Burrowable,Spellcaster,"Permanent Cloak","Pickup Item(?)","Ignore Supply Check","Use Medium Overlays","Use Large Overlays","Battle Reactions","Full Auto-Attack",Invincible,"Mechanical Unit","Produces Units(?)"'],
				[[None,''],''],
				[[None,''],'StarCraft crashes with values above 11'],
				[[self.dat_value,'Upgrades'],''],
				[[self.info_value,'UnitSize'],''],
				[[None,''],''],
				[[self.info_value,'Rightclick'],''],
				[[self.dat_value,'Sfxdata'],''],
				[[self.dat_value,'Sfxdata'],''],
				[[self.dat_value,'Sfxdata'],''],
				[[self.dat_value,'Sfxdata'],''],
				[[self.dat_value,'Sfxdata'],''],
				[[self.dat_value,'Sfxdata'],''],
				[[self.dat_value,'Sfxdata'],''],
				[[None,''],''],
				[[None,''],''],
				[[None,''],'X Position'],
				[[None,''],'Y Position'],
				[[None,''],''],
				[[None,''],''],
				[[None,''],''],
				[[None,''],''],
				[[self.dat_value,'Portdata'],''],
				[[None,''],''],
				[[None,''],''],
				[[self.time_value,''],''],
				[[None,''],''],
				[[None,''],'Zerg,Terran,Protoss,Men,Building,Factory,Independent,Neutral'],
				[[None,''],''],
				[[None,''],''],
				[[None,''],''],
				[[None,''],''],
				[[None,''],''],
				[[None,''],''],
				[[None,''],''],
				[[None,''],''],
				[[None,''],'Non-Neutral,"Unit Listing&&Palette","Mission Briefing","Player Settings","All Races","Set Doodad State","Non-Location Triggers","Unit&&Hero Settings","Location Triggers","BroodWar Only","Unused (0x400)","Unused (0x800)","Unused (0x1000)","Unused (0x2000)","Unused (0x4000)","Unused (0x8000)"']
			]
			self.special = {
				'HitPoints':self.hitpoints
			}

	def get_value(self, entry, label):
		try:
			return self.entries[entry][self.labels.index(label)]
		except:
			return None

	def set_value(self, entry, label, value):
		try:
			self.entries[entry][self.labels.index(label)] = value
		except:
			return False
		return True

	def hitpoints(self, value, save=False):
		if save:
			hp = struct.pack('<Q', value<<8)[:4]
			if hp == '\x00\x00\x00\x00':
				return '\x01\x00\x00\x00'
			return hp
		return value>>8

	def load_file(self, file):
		if isstr(file):
			try:
				f = open(file,'rb')
				data = f.read()
				f.close()
			except:
				raise PyMSError('Load',"Could not load %s file '%s'" % (self.datname, file))
		else:
			data = file.read()
		if len(data) != self.filesize:
			raise PyMSError('Load',"'%s' is an invalid %s file (the file size must be %s, but got a file with size %s)" % (file,self.datname,self.filesize,len(data)))
		try:
			entries = []
			offset = 0
			array = 0
			arraylen = 0
			for x,format in enumerate(self.format):
				bytes = format[1]
				if len(format) == 3:
					arraylen = array = format[2]
				vals = self.count
				values = []
				if format[0]:
					vals = format[0][1] - format[0][0]
					values.extend([0]*format[0][0])
				for y in range(vals):
					o = offset+y*arraylen*bytes+(arraylen-array)*bytes
					values.append(struct.unpack('<%s' % ['', 'B','H','','L'][bytes], data[o:o+bytes])[0])
					if not array:
						offset += bytes
				if format[0]:
					values.extend([0]*(self.count - format[0][1]))
				if array:
					array -= 1
					if not array:
						offset += arraylen * bytes * vals
						arraylen = 0
				# elif format[0]:
					# vals = format[0][1] - format[0][0]
					# values = [0]*format[0][0] + list(struct.unpack('<%s%s' % (vals, ['', 'B','H','','L'][bytes]), data[offset:offset+bytes*vals])) + [0]*(self.count - format[0][1])
					# offset += bytes * vals
				# else:
					# values = struct.unpack('<%s%s' % (self.count, ['','B','H','','L'][bytes]), data[offset:offset+bytes*self.count])
					# offset += bytes * self.count
				for id,value in enumerate(values):
					if x == 0:
						entries.append([value])
					elif self.labels[x] in self.special:
						entries[id].append(self.special[self.labels[x]](value))
					# elif self.datname == 'units.dat' and x == 8: #HitPoints
						# entries[id].append(value>>8)
					# elif self.datname == 'weapons.dat' and x in [4,5]:
						# entries[id].append(value>>4)
					else:
						entries[id].append(value)
			self.entries = entries
		except:
			raise PyMSError('Load','Unsupported %s file, could possibly be corrupt' % self.datname)

	def dat_value(self, file, value):
		if value == 65535:
			return '%s.dat entry: None'
		return '%s.dat entry: %s' % (file, DATA_CACHE[file + '.txt'][value])

	def info_value(self, file, value):
		if file == 'ElevationLevels':
			s = 'Unit elevation level: '
		elif file == 'UnitSize':
			s = 'Unit size: '
		elif file == 'Rightclick':
			s = 'Right-click order action: '
		return s + DATA_CACHE[file + '.txt'][value]

	def time_value(self, _, value):
		return 'Length in seconds: %s' % (value / 24)

	def stattxt_value(self, type, value):
		if type == 'Sublabel':
			value += 1301
		return '%s in stat_txt.tbl, item %s: %s' % (type, value, TBL.decompile_string(self.tbl.strings[value]))

	def interpret(self, file):
		if len(self.entries) != self.count:
			raise PyMSError('Interpreting',"No default %s file was loaded as a base" % self.datname)
		try:
			f = open(file,'r')
			data = f.readlines()
			f.close()
		except:
			raise PyMSError('Interpreting',"Could not load file '%s'" % file)
		entries = {}
		entrydata = False
		curentry = -1
		for n,l in enumerate(data):
			if len(l) > 1:
				ln = l.strip().split('#',1)[0]
				line = re.split('\s+', ln)
				if entrydata:
					if line[0] == self.header + 'ID':
						raise PyMSError('Interpreting',"Unexpected line, expected a value",n,ln)
					if line[0] not in self.labels:
						raise PyMSError('Interpreting',"'%s' is an invalid value label" % line[0],n,ln)
					label = self.labels.index(line[0])
					value = None
					if line[0] in self.flaglens:
						if len(line[1]) != self.flaglens[line[0]]:
							raise PyMSError('Interpreting',"Incorrect amount of flags (expected %s, got %s)" % (self.flaglens[line[0]],len(line[1])),n,ln)
						if re.match('[^01]',line[1]):
							raise PyMSError('Interpreting',"'%s' is an invalid set of flags" % line[1],n,ln)
						value = sum(int(x)*(2**n) for n,x in enumerate(reversed(line[1])))
					if value == None:
						try:
							value = int(line[1])
							if value < 0 or value > 256 ** self.format[label][1]:
								raise
						except:
							raise PyMSError('Interpreting',"'%s' is an invalid value (must be in range 0 to %s)" % (line[1],256**self.format[label][1]),n,ln)
					if self.datname == 'units.dat' and line[0] == 'SightRange' and value > 11:
						raise PyMSError('Interpreting',"SightRange can not be more then 11",n,ln)
					entries[curentry][label] = value
					if not None in entries[curentry]:
						entrydata = False
				else:
					if line[0] != self.header + 'ID' or not line[1].endswith(':'):
						raise PyMSError('Interpreting',"Unexpected line, expected a new %sID header" % self.header,n,ln)
					try:
						id = int(line[1][:-1])
						if id < 0 or id >= self.count:
							raise
					except:
						raise PyMSError('Interpreting',"Invalid %sID value (must be in the range 0 to %s)" % (self.header,self.count),n,ln)
					entries[id] = [None]*len(self.format)
					for n,format in enumerate(self.format):
						if format[0] and not id in range(*format[0]):
							entries[id][n] = 0
					curentry = id
					entrydata = True
		if None in entries[curentry]:
			raise PyMSError('Interpreting',"Entry '%s' is missing a value for %s" % (curentry,self.labels[entries.curentry.index(None)]),n,ln)
		for id,entry in entries.iteritems():
			self.entries[id] = entry
		return entries.keys()

	def decompile(self, file, ref=False, ids=None):
		try:
			f = open(file, 'w')
		except:
			raise PyMSError('Interpreting',"Could not load file '%s'" % file)
		if ref:
			f.write('#----------------------------------------------------')
			for file,name in DATA_REFERENCE.iteritems():
				f.write('\n# %s:' % name)
				for n,value in enumerate(DATA_CACHE[file]):
					pad = ' ' * (3 - len(str(n)))
					f.write('\n#     %s%s = %s' % (pad,n,value))
				f.write('\n#')
			f.write('----------------------------------------------------\n\n')
		if ids == None:
			ids = range(self.count)
		for id in ids:
			f.write('%sID %s:%s# %s name: %s\n' % (self.header, id, ' ' * (12 + self.longlabel - len(self.header) - len(str(id))), self.header, DATA_CACHE[self.idfile][id]))
			for format,data,label,value in zip(self.format,self.data,self.labels,self.entries[id]):
				if not format[0] or id in range(*format[0]):
					if label in self.flaglens:
						v = ''.join(reversed([str(value/(2**n)%2) for n in range(self.flaglens[label])]))
					else:
						v = value
					f.write('    %s%s%s' % (label, ' ' * (self.longlabel + 1 - len(label)), v))
					if data[0][0]:
						f.write('%s# %s' % (' ' * (11 - len(str(v))), data[0][0](data[0][1], v)))
					f.write('\n')
			f.write('\n')
		f.close()

	def compile(self, file):
		if len(self.entries) != self.count:
			raise
		if isstr(file):
			try:
				f = open(file, 'wb')
			except:
				raise PyMSError('Compile',"Could not load file '%s'" % file)
		else:
			f = file
		data = []
		for id,entry in enumerate(self.entries):
			if len(entry) < len(self.format):
				raise
			array = 0
			d,fd = 0,0
			for x,value in enumerate(entry):
				if array:
					d += 1
					fd += 1
				format = self.format[x-fd]
				if x-d == len(data):
					data.append([])
				if not array:
					if len(format) == 3:
						array = format[2] - 1
				else:
					array -= 1
					if array == 0:
						fd = 0
				if format[0] and not id in range(*format[0]):
					continue
				data[x-d].append(value)
		l = list(self.labels)
		d = 0
		for n,values in enumerate(data):
			format,label = self.format[n+d],self.labels[n+d]
			l.remove(label)
			if len(format) == 3:
				d += format[2]-1
			if label in self.special:
				for value in values:
					f.write(self.special[label](value,True))
			else:
				f.write(struct.pack('<%s%s' % (len(values), ['', 'B','H','','L'][format[1]]), *values))
		f.close()

class WeaponsDAT(UnitsDAT):
	format = [
		[[],2],
		[[],4],
		[[],1],
		[[],2],
		[[],4],
		[[],4],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],2],
		[[],2],
		[[],2],
		[[],2],
		[[],2],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],2],
		[[],2]
	]
	labels = [
		'Label',
		'Graphics',
		'Unused',
		'TargetFlags',
		'MinimumRange',
		'MaximumRange',
		'DamageUpgrade',
		'WeaponType',
		'WeaponBehavior',
		'RemoveAfter',
		'ExplosionType',
		'InnerSplashRange',
		'MediumSplashRange',
		'OuterSplashRange',
		'DamageAmount',
		'DamageBonus',
		'WeaponCooldown',
		'DamageFactor',
		'AttackAngle',
		'LaunchSpin',
		'ForwardOffset',
		'UpwardOffset',
		'TargetErrorMessage',
		'Icon'
	]
	flaglens = {'TargetFlags':9}
	longlabel = 18
	datname = 'weapons.dat'
	header = 'Weapon'
	idfile = 'Weapons.txt'
	filesize = 5460
	count = 130
	
	def __init__(self, stat_txt=None):
		UnitsDAT.__init__(self, stat_txt)
		self.data = [
			[[self.stattxt_value,'Weapon Label'],''],
			[[self.dat_value,'Flingy'],''],
			[[self.info_value,'Techdata'],''],
			[[None,''],'Air,Ground,Mechanical,Organic,non-Building,non-Robotic,Terrain,Organic or Mechanical,Own'],
			[[None,''],''],
			[[None,''],''],
			[[self.dat_value,'Upgrades'],''],
			[[self.info_value,'DamTypes'],''],
			[[self.info_value,'Behaviours'],''],
			[[None,''],''],
			[[self.info_value,'Explosions'],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[self.stattxt_value,'Targetting Error Message'],''],
			[[self.info_value,'Icons'],'']
		]
		self.special = {
			'MinimumRange':self.range,
			'MaximumRange':self.range,
		}

	def info_value(self, file, value):
		if file == 'DamTypes':
			s = 'Damage Type: '
		elif file == 'Behaviours':
			s = 'Projectile Behaviour: '
		elif file == 'Explosions':
			s = 'Explosion Type: '
		elif file == 'Icons':
			s = 'Weapon Icon: '
		elif file == 'Techdata':
			s = 'Has no effect. Assumed value: '
		return s + DATA_CACHE[file + '.txt'][value]

	def range(self, value, save=False):
		if save:
			return struct.pack('<L', value<<4)
		return value>>4

class FlingyDAT(UnitsDAT):
	format = [
		[[],2],
		[[],4],
		[[],2],
		[[],4],
		[[],1],
		[[],1],
		[[],1]
	]
	labels = [
		'Sprite',
		'Speed',
		'Acceleration',
		'HaltDistance',
		'TurnRadius',
		'Unused',
		'MovementControl'
	]
	longlabel = 15
	datname = 'flingy.dat'
	header = 'Flingy'
	idfile = 'Flingy.txt'
	filesize = 3135
	count = 209

	def __init__(self, stat_txt=None):
		UnitsDAT.__init__(self, stat_txt)
		self.data = [
			[[self.dat_value, 'Sprites'],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[self.info_value, 'FlingyControl'],'']
		]
		self.special = {}

	def info_value(self, file, value):
		return 'Flingy Control: ' + DATA_CACHE[file + '.txt'][value]

class SpritesDAT(UnitsDAT):
	format = [
		[[],2],
		[[130,517],1],
		[[],1],
		[[],1],
		[[130,517],1],
		[[130,517],1]
	]
	labels = [
		'ImageFile',
		'HealthBar',
		'Unknown',
		'IsVisible',
		'SelectionCircleImage',
		'SelectionCircleOffset'
	]
	longlabel = 21
	datname = 'sprites.dat'
	header = 'Sprite'
	idfile = 'Sprites.txt'
	filesize = 3229
	count = 517
	
	def __init__(self, stat_txt=None):
		UnitsDAT.__init__(self, stat_txt)
		self.data = [
			[[self.dat_value,'Images'],''],
			[[self.hpbar_value,''],''],
			[[None,''],''],
			[[None,''],''],
			[[self.info_value, 'SelCircleSize'],''],
			[[None,''],'']
		]
		self.special = {}

	def hpbar_value(self, _, value):
		return 'Health Bar Boxes: %s' % (int((value -1) / 3))

	def info_value(self, file, value):
		return 'Selection Circle Size: ' + DATA_CACHE[file + '.txt'][value]

class ImagesDAT(UnitsDAT):
	format = [
		[[],4],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],4],
		[[],4],
		[[],4],
		[[],4],
		[[],4],
		[[],4],
		[[],4]
	]
	labels = [
		'GRPFile',
		'GfxTurns',
		'Clickable',
		'UseFullIscript',
		'DrawIfCloaked',
		'DrawFunction',
		'Remapping',
		'IscriptID',
		'ShieldOverlay',
		'AttackOverlay',
		'DamageOverlay',
		'SpecialOverlay',
		'LandingDustOverlay',
		'LiftOffDustOverlay'
	]
	longlabel = 18
	datname = 'images.dat'
	header = 'Image'
	idfile = 'Images.txt'
	filesize = 37962
	count = 999
	
	def __init__(self, grps=None):
		if grps == None:
			grps = os.path.join(BASE_DIR, 'Libs', 'MPQ', 'rez', 'images.tbl')
		UnitsDAT.__init__(self, grps)
		self.data = [
			[[self.stattxt_value,'GRP File Path: '],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[self.info_value,'DrawList'],''],
			[[self.info_value,'Remapping'],''],
			[[self.info_value,'IscriptIDList'],''],
			[[self.stattxt_value,'Shield Overlay File Path'],''],
			[[self.stattxt_value,'Attack Overlay File Path'],''],
			[[self.stattxt_value,'Damage Overlay File Path'],''],
			[[self.stattxt_value,'Special Overlay File Path'],''],
			[[self.stattxt_value,'Landing Dust Overlay File Path'],''],
			[[self.stattxt_value,'Lift-Off Dust Overlay File Path'],'']
		]
		self.special = {}

	def stattxt_value(self, type, value):
		if value == 0:
			return '%s: None' % type
		return '%s in images.tbl, item %s: %s' % (type, value - 1, TBL.decompile_string(self.tbl.strings[value - 1]))

	def info_value(self, file, value):
		if file == 'DrawList':
			s = 'Drawing Function: '
		elif file == 'Remapping':
			s = 'Additional Remapping Palette: '
		elif file == 'IscriptIDList':
			s = 'IScript Name: '
		return s + DATA_CACHE[file + '.txt'][value]

class UpgradesDAT(UnitsDAT):
	format = [
		[[],2],
		[[],2],
		[[],2],
		[[],2],
		[[],2],
		[[],2],
		[[],2],
		[[],2],
		[[],2],
		[[],1],
		[[],1],
		[[],1]
	]
	labels = [
		'MineralCostBase',
		'MineralCostFactor',
		'VespeneCostBase',
		'VespeneCostFactor',
		'ResearchTimeBase',
		'ResearchTimeFactor',
		'Unknown',
		'Icon',
		'Label',
		'Race',
		'MaxRepeats',
		'BroodwarOnly'
	]
	longlabel = 18
	datname = 'upgrades.dat'
	header = 'Upgrade'
	idfile = 'Upgrades.txt'
	filesize = 1281
	count = 61
	
	def __init__(self, stat_txt=None):
		UnitsDAT.__init__(self, stat_txt)
		self.data = [
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[self.time_value,''],''],
			[[self.time_value,''],''],
			[[None,''],''],
			[[self.info_value,'Icons'],''],
			[[self.stattxt_value,'Upgrade Label'],''],
			[[self.info_value,'Races'],''],
			[[None,''],''],
			[[None,''],'']
		]
		self.special = {}

	def stattxt_value(self, type, value):
		if value == 0:
			return '%s: None' % type
		return '%s in stat_txt.tbl, item %s: %s' % (type, value - 1, TBL.decompile_string(self.tbl.strings[value - 1]))

	def info_value(self, file, value):
		if file == 'Icons':
			s = 'Upgrade Icon: '
		elif file == 'Races':
			s = 'Used by Race: '
		return s + DATA_CACHE[file + '.txt'][value]

class TechDAT(UnitsDAT):
	format = [
		[[],2],
		[[],2],
		[[],2],
		[[],2],
		[[],4],
		[[],2],
		[[],2],
		[[],1],
		[[],1],
		[[],1]
	]
	labels = [
		'MineralCost',
		'VespeneCost',
		'ResearchTime',
		'EnergyRequired',
		'Unknown',
		'Icon',
		'Label',
		'Race',
		'Unused',
		'BroodwarOnly'
	]
	longlabel = 14
	datname = 'techdata.dat'
	header = 'Tech'
	idfile = 'Techdata.txt'
	filesize = 836
	count = 44
	
	def __init__(self, stat_txt=None):
		UnitsDAT.__init__(self, stat_txt)
		self.data = [
			[[None,''],''],
			[[None,''],''],
			[[self.time_value,''],''],
			[[None,''],''],
			[[None,''],''],
			[[self.info_value,'Icons'],''],
			[[self.stattxt_value,'Technology Label'],''],
			[[self.info_value,'Races'],''],
			[[None,''],''],
			[[None,''],'']
		]
		self.special = {}

	def stattxt_value(self, type, value):
		if value == 0:
			return '%s: None' % type
		return '%s in stat_txt.tbl, item %s: %s' % (type, value - 1, TBL.decompile_string(self.tbl.strings[value - 1]))

	def info_value(self, file, value):
		if file == 'Icons':
			s = 'Upgrade Icon: '
		elif file == 'Races':
			s = 'Used by Race: '
		return s + DATA_CACHE[file + '.txt'][value]

class SoundsDAT(UnitsDAT):
	format = [
		[[],4],
		[[],1],
		[[],1],
		[[],2],
		[[],1]
	]
	labels = [
		'SoundFile',
		'Unknown1',
		'Unknown2',
		'Unknown3',
		'Unknown4'
	]
	longlabel = 9
	datname = 'sfxdata.dat'
	header = 'Sound'
	idfile = 'Sfxdata.txt'
	filesize = 10296
	count = 1144
	
	def __init__(self, sfx=None):
		if sfx == None:
			sfx = os.path.join(BASE_DIR, 'Libs', 'MPQ', 'rez', 'sfxdata.tbl')
		UnitsDAT.__init__(self, sfx)
		self.data = [
			[[self.stattxt_value,'Sound File Path'],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],'']
		]
		self.special = {}

	def stattxt_value(self, type, value):
		if value == 0:
			return '%s: None' % type
		return '%s in sfxdata.tbl, item %s: %s' % (type, value - 1, TBL.decompile_string(self.tbl.strings[value - 1]))

class PortraitDAT(UnitsDAT):
	format = [
		[[],4],
		[[],1],
		[[],1]
	]
	labels = [
		'PortraitFile',
		'SMKChange',
		'Unknown'
	]
	longlabel = 12
	datname = 'portdata.dat'
	header = 'Portrait'
	idfile = 'Portdata.txt'
	filesize = 1320
	count = 220
	
	def __init__(self, ports=None):
		if ports == None:
			ports = os.path.join(BASE_DIR, 'Libs', 'MPQ', 'rez', 'portdata.tbl')
		UnitsDAT.__init__(self, ports)
		self.data = [
			[[self.stattxt_value,'Portrait File Path'],''],
			[[None,''],''],
			[[None,''],'']
		]
		self.special = {}

	def stattxt_value(self, type, value):
		if value == 0:
			return '%s: None' % type
		return '%s in portdata.tbl, item %s: %s' % (type, value - 1, TBL.decompile_string(self.tbl.strings[value - 1]))

class CampaignDAT(UnitsDAT):
	format = [
		[[],4]
	]
	labels = [
		'MapFile'
	]
	longlabel = 7
	datname = 'mapdata.dat'
	header = 'Map'
	idfile = 'Mapdata.txt'
	filesize = 260
	count = 65
	
	def __init__(self, maps=None):
		if maps == None:
			maps = os.path.join(BASE_DIR, 'Libs', 'MPQ', 'rez', 'mapdata.tbl')
		UnitsDAT.__init__(self, maps)
		self.data = [
			[[self.stattxt_value,'Map File Path'],'']
		]
		self.special = {}

	def stattxt_value(self, type, value):
		if value == 65:
			return '%s in mapdata.tbl, item %s: None' % (type, value)
		return '%s in mapdata.tbl, item %s: %s' % (type, value, TBL.decompile_string(self.tbl.strings[value]))

class OrdersDAT(UnitsDAT):
	format = [
		[[],2],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],1],
		[[],2],
		[[],2],
		[[],1]
	]
	labels = [
		'Label',
		'UseWeaponTargeting',
		'Unknown1',
		'MainOrSecondary',
		'Unknown3',
		'Unknown4',
		'Interruptable',
		'Unknown5',
		'Queueable',
		'Unknown6',
		'Unknown7',
		'Unknown8',
		'Unknown9',
		'Targeting',
		'Energy',
		'Animation',
		'Highlight',
		'Unknown10',
		'ObscuredOrder'
	]
	longlabel = 18
	datname = 'orders.dat'
	header = 'Order'
	idfile = 'Orders.txt'
	filesize = 4158
	count = 189
	
	def __init__(self, stat_txt=None):
		UnitsDAT.__init__(self, stat_txt)
		self.data = [
			[[self.stattxt_value,'Order Label'],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[None,''],''],
			[[self.dat_value,'Weapons'],''],
			[[self.info_value,'Techdata'],''],
			[[self.info_value,'Animations'],''],
			[[self.info_value,'Icons'],''],
			[[None,''],''],
			[[self.dat_value,'Orders'],'']
		]
		self.special = {}

	def info_value(self, file, value):
		if file == 'Techdata':
			s = 'Energy Cost Technology: '
		elif file == 'Animations':
			s = 'Unit IScript Animation: '
		elif file == 'Icons':
			s = 'Highlight Icon: '
			if value == 65535:
				return s + 'None'
		return s + DATA_CACHE[file + '.txt'][value]

# for DAT in [SpritesDAT]:#UnitsDAT,WeaponsDAT,FlingyDAT,SpritesDAT,ImagesDAT,UpgradesDAT,TechDAT,SoundsDAT,PortraitDAT,CampaignDAT,OrdersDAT]:
	# d = DAT()
	# print d.datname
	# d.load_file('Default\\' + d.datname)
	# d.compile('Test\\' + d.datname)
#d = ImagesDAT()
#d.load_file('Default\images.dat')
#d.decompile('blah.txt',[0,1])
#d.interpret('blah.txt')
#d.decompile('test.txt',[0,1])
#d.compile('test.dat')

# class DAT(UnitsDAT):
	# format = [

	# ]
	# labels = [

	# ]
	# longlabel = 0
	# datname = '.dat'
	# header = ''
	# idfile = '.txt'
	# filesize = 0
	# count = 0
	
	# def __init__(self, stat_txt='Default\stat_txt.tbl'):
		# UnitsDAT.__init__(self, stat_txt)
		# self.data = [

		# ]

	# def info_value(self, file, value):
		# if file == 'DamTypes':
			# s = 'Damage Type: '
		# elif file == 'Behaviours':
			# s = 'Projectile Behaviour: '
		# elif file == 'Explosions':
			# s = 'Explosion Type: '
		# elif file == 'Icons':
			# s = 'Weapon Icon: '
		# elif file == 'Techdata':
			# s = 'Has no effect. Assumed value: '
		# return s + DATA_CACHE[file + '.txt'][value]