from utils import *

import struct

class Palette:
	def __init__(self):
		self.palette = [[0,0,0] for _ in range(256)]
		self.type = None

	def load_riff_pal(self, data):
		if len(data) != 1047 or not data.startswith('RIFF\x00\x00PAL data'):
			raise
		return self.load_sc_pal(self, data[24:])

	def load_jasc_pal(self, data):
		data = data.split('\r\n')
		if not data[-1]:
			data.pop()
		if len(data) != 259 or data[0] != 'JASC-PAL' or data[1] != '0100' or data[2] != '256':
			raise
		return [[int(c) for c in line.split(' ')] for line in data[3:]]

	def load_zsoft_pcx(self, data):
		if data[0:2] != '\x0A\x05' or data[3] != '\x08' or data[-769] != '\x0C':
			raise
		return self.load_sc_pal(data[-768:])

	def load_sc_wpe(self, data):
		return self.load_sc_pal(data, 1024, 4)

	def load_sc_pal(self, data, max=768, mult=3):
		if len(data) != max:
			raise
		palette = []
		for x in range(0,max,mult):
			palette.append(list(struct.unpack('3B', data[x:x+3])))
		return palette

	def load_file(self, file):
		try:
			if isstr(file):
				f = open(file,'rb')
				data = f.read()
				f.close()
			else:
				data = file.read()
		except:
			raise PyMSError('Palette',"Could not load palette '%s'" % file)
		for t,pal in [(0,self.load_riff_pal),(1,self.load_jasc_pal),(None,self.load_zsoft_pcx),(3,self.load_sc_wpe),(2,self.load_sc_pal)]:
			try:
				palette = pal(data)
				if len(palette) == 256:
					self.type = t
					break
			except:
				pass
		else:
			raise PyMSError('Palette',"Unsupported palette file '%s', could possibly be corrupt" % file)
		self.palette = palette

	def load_data(self, palette):
		self.palette = palette

	def save_riff_pal(self, file):
		try:
			f = open(file,'wb')
		except:
			raise PyMSError('Palette',"Could not save palette to file '%s'" % file)
		f.write('RIFF\x00\x00PAL data')
		for c in self.palette:
			f.write(struct.pack('3B',*c))
		f.close()

	def save_jasc_pal(self, file):
		try:
			f = open(file,'wb')
		except:
			raise PyMSError('Palette',"Could not save palette to file '%s'" % file)
		f.write('JASC-PAL\r\n0100\r\n256\r\n')
		for c in self.palette:
			f.write(' '.join(c) + '\r\n')
		f.close()

	def save_sc_wpe(self, file):
		try:
			f = open(file,'wb')
		except:
			raise PyMSError('Palette',"Could not save palette to file '%s'" % file)
		for c in self.palette:
			f.write(struct.pack('3Bx',*c))
		f.close()

	def save_sc_pal(self, file):
		try:
			f = open(file,'wb')
		except:
			raise PyMSError('Palette',"Could not save palette to file '%s'" % file)
		for c in self.palette:
			f.write(struct.pack('3B',*c))
		f.close()