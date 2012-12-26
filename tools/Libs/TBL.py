from utils import *

import struct, re

TBL_REF = """#----------------------------------------------------
# Misc.
#    <0> = End Substring
#    <9> = Tab
#   <10> = Newline
#   <18> = Right Align
#   <19> = Center Align
#   <27> = Escape Key
#   <35> = #
#   <60> = <
#   <62> = >
#
# Menu Screen Colors
#    <1> = Cyan
#    <2> = Cyan
#    <3> = Green
#    <4> = Light Green
#    <5> = Grey*
#    <6> = White
#    <7> = Red
#    <8> = Black*
#   <11> = Invisible*
#   <12> = Truncate
#   <14> = Black
#   <15> = Black
#   <16> = Black
#   <17> = Black
#   <20> = Invisible*
#   <21> = Black
#   <22> = Black
#   <23> = Black
#   <24> = Black
#   <25> = Black
#   <26> = Black/Cyan?
#   <27> = Black
#   <28> = Black
#
# In-game Colors
#    <1> = Cyan
#    <2> = Cyan
#    <3> = Yellow
#    <4> = White
#    <5> = Grey*
#    <6> = Red
#    <7> = Green
#    <8> = Red (Player 1)
#   <11> = Invisible*
#   <12> = Truncate
#   <14> = Blue (Player 2)
#   <15> = Teal (Player 3)
#   <16> = Purple (Player 4)
#   <17> = Orange (Player 5)
#   <20> = Invisible*
#   <21> = Brown (Player 6)
#   <22> = White (Player 7)
#   <23> = Yellow (Player 8)
#   <24> = Green (Player 9)
#   <25> = Brighter Yellow (Player 10)
#   <26> = Cyan
#   <27> = Pinkish (Player 11)
#   <28> = Dark Cyan (Player 12)
#   <29> = Greygreen
#   <30> = Bluegrey
#   <31> = Turquiose
#
# Hotkey Types
#    <0> = Label Only, no Requirements
#    <1> = Minerals, Gas, Supply (Unit/Building)
#    <2> = Upgrade Research
#    <3> = Spell
#    <4> = Technology Research
#    <5> = Minerals, Gas (Guardian/Devourer Aspect)
#
# * Starcraft will ignore all color tags after this.
#----------------------------------------------------
"""

DEF_DECOMPILE = ''.join([chr(x) for x in range(32)]) + '#<>'

def compile_string(string):
	def special_chr(o):
		c = int(o.group(1)) 
		if -1 > c or 255 < c:
			return o.group(0)
		return chr(c)
	return re.sub('<(\d+)>', special_chr, string)

def decompile_string(string, exclude='', include=''):
	def special_chr(o):
		return '<%s>' % ord(o.group(0))
	decompile = DEF_DECOMPILE + include
	if exclude:
		decompile = re.sub('[%s]' % re.escape(exclude),'',decompile)
	return re.sub('([%s])' % decompile, special_chr, string)

class TBL:
	def __init__(self):
		self.strings = []

	def load_file(self, file):
		try:
			if isstr(file):
				f = open(file,'rb')
				data = f.read()
				f.close()
			else:
				data = file.read()
		except:
			raise PyMSError('Load',"Could not load TBL file '%s'" % file)
		try:
			n = struct.unpack('<H', data[:2])[0]
			offsets = struct.unpack('<%sH' % n, data[2:2+2*n])
			findlen = {}
			for x in offsets:
				findlen[x] = 1
			findlen = findlen.keys() + [len(data)]
			findlen.sort()
			strings = []
			for o in offsets:
				strings.append(data[o:findlen[findlen.index(o)+1]])
			self.strings = strings
		except:
			raise PyMSError('Load',"Unsupported TBL file '%s', could possibly be corrupt" % file)

	def interpret(self, file):
		try:
			f = open(file,'r')
			data = f.readlines()
			f.close()
		except:
			raise PyMSError('Interpreting',"Could not load file '%s'" % file)
		strings = []
		for n,l in enumerate(data):
			line = l.split('#',1)[0]
			if line:
				if len(strings) == 65536:
					raise PyMSError('Interpreting',"There are too many string entries (max entries is 65536)")
				s = compile_string(line.rstrip('\r\n'))
				strings.append(s)
		self.strings = strings

	def compile(self, file):
		try:
			f = open(file, 'wb')
		except:
			raise PyMSError('Compile',"Could not load file '%s'" % file)
		o = 2 + 2 * len(self.strings)
		header = struct.pack('<H', len(self.strings))
		data = ''
		for s in self.strings:
			if not s.endswith('\x00'):
				s += '\x00'
			header += struct.pack('<H', o)
			data += s
			o += len(s)
		f.write(header + data)
		f.close()

	def decompile(self, file, ref=False):
		try:
			f = open(file, 'w')
		except:
			raise PyMSError('Decompile',"Could not load file '%s'" % file)
		if ref:
			f.write(TBL_REF)
		for s in self.strings:
		   f.write(decompile_string(s) + '\n')
		f.close()

#t = TBL()
#t.load_file('Data\stat_txt.tbl')
#t.decompile('test.txt')
# t.interpret('test.txt')
# t.compile('test.tbl')
# t.compile('test.tbl')
# o = open('out.txt','w')
# def getord(o):
   # return '<%s>' % ord(o.group(0))
# for s in t.strings:
   # o.write(re.sub('([\x00\x01\x02\x03\x04\x05\x06\x07\x08<>])', getord, s) + '\n')