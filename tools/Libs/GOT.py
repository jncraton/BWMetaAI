from utils import *

import struct, re

class GOT:
	labels = [
		'SubtypeLabel',
		'GameTypeID',
		'SubtypeID',
		'SubtypeValue',
		'VictoryConditions',
		'ResourceType',
		'UnitStats',
		'FogOfWar',
		'StartingUnits',
		'StartingPositions',
		'PlayerTypes',
		'Allies',
		'TeamMode',
		'CheatCodes',
		'TournamentMode',
		'VictoryValue',
		'ResourceValue',
	]
	info = [
		None,
		1,
		1,
		4,
		['Map Default','Melee','High Score','Resources','Capture the Flag','Sudden Death','Slaughter','One on One'],
		['Map Default','Fixed Value','Low','Medium','High','Income'],
		['Map Default','Standard'],
		['Off','Warcraft 1 Style','On'],
		['Map Default','Worker Only','Worker and Center'],
		['Random','Fixed'],
		['No Single, No Computers','No Single, Computers Allowed','Single, No Computers','Single, Computers Allowed',],
		['Not Allowed','Allowed'],
		['Off','A value of 1 is Invalid for this setting. DO NOT USE IT!','2 Teams','3 Teams','4 Teams'],
		['Off','On'],
		['Off','On'],
		4,
		4
	]

	def __init__(self):
		self.template = [0]*18

	def load_file(self, file):
		try:
			if isstr(file):
				f = open(file,'rb')
				data = f.read()
				f.close()
			else:
				data = file.read()
		except:
			raise PyMSError('Load',"Could not load GOT '%s'" % file)
		try:
			if data[0] != '\x03':
				raise
			template = list(struct.unpack('<32s32sBxBxHxx11BLL', data[1:-5]))
			template[0] = template[0].rstrip('\x00')
			template[1] = template[1].rstrip('\x00')
			self.template = template
		except:
			raise PyMSError('Load',"Unsupported GOT file '%s', could possibly be corrupt" % file)

	def interpret(self, file):
		try:
			f = open(file,'r')
			data = f.readlines()
			f.close()
		except:
			raise PyMSError('Interpreting',"Could not load file '%s'" % file)
		template = [None]*18
		tdata = False
		for n,l in enumerate(data):
			if len(l) > 1:
				ln = l.strip().split('#',1)[0]
				line = re.split('\s+', ln)
				if line:
					if tdata:
						if line[0] not in self.labels:
							raise PyMSError('Interpreting',"'%s' is an unknown entry" % file,n,ln)
						label = self.labels.index(line[0])
						if label == 0:
							if len(line[1]) > 32:
								raise PyMSError('Interpreting',"Subtype label '%s' is too long (max length is 32, got length %s)" % (line[1],len(line[1])),n,ln)
							value = line[1]
						else:
							try:
								value = int(line[1])
								info = self.info[label]
								if value < 0 or (type(info) == list and value >= len(info)) or (type(info) == int and value >= 256 ** info):
									raise
							except:
								raise PyMSError('Interpreting',"Invalid value '%s' for entry '%s'" % (line[1],line[0]),n,ln)
						template[label+1] = value
						if not None in template:
							break
					else:
						if line[-1] != 'Template:':
							raise PyMSError('Interpreting',"Unknown line format, expected 'Template:' start line" % file,n,ln)
						template[0] = ' '.join(line[:-1])
						if len(template[0]) > 32:
							raise PyMSError('Interpreting',"Template name '%s' is too long (max length is 32, got length %s)" % (template[0],len(template[0])),n,ln)
						tdata = True
		if None in template:
			raise PyMSError('Interpreting',"The template is missing a '%s' entry" % (template[0],self.labels[template.index(None)-1]),n,ln)
		self.template = template

	def decompile(self, file, ref=False):
		try:
			f = open(file, 'w')
		except:
			raise PyMSError('Decompile',"Could not load file '%s'" % file)
		if ref:
			f.write('#----------------------------------------------------\n')
			for l,v in zip(self.labels,self.info):
				if type(v) == list:
					f.write('# %s Values:\n' % l)
					for n,i in enumerate(v):
						f.write('#    %s = %s\n' % (n,i))
					f.write('#\n')
			f.write('#----------------------------------------------------\n')
		f.write('%s Template:\n' % self.template[0])
		for label,info,value in zip(self.labels,self.info,self.template[1:]):
			f.write('    %s%s%s' % (label, ' ' * (18 - len(label)), value))
			if type(info) == list:
				if value < len(info):
					f.write('%s# %s' % (' ' * (11 - len(str(value))), info[value]))
			f.write('\n')
		f.close()

	def compile(self, file):
		try:
			f = open(file, 'wb')
		except:
			raise PyMSError('Compile',"Could not load file '%s'" % file)
		f.write(struct.pack('<B32s32sBxBxHxx11BLL5x', 3, self.template[0] + '\x00' * (32 - len(self.template[0])), self.template[1] + '\x00' * (32 - len(self.template[1])), *self.template[2:]))
		f.close()

#g = GOT()
#g.load_file('test.got')
#g.decompile('test.txt')
#g.interpret('test.txt')
#g.compile('asd.got')