from utils import *

import struct, math

class BMP:
	def __init__(self, palette=[]):
		self.width = 0
		self.height = 0
		self.palette = palette
		self.image = []

	def load_file(self, file, issize=None):
		try:
			if isstr(file):
				f = open(file,'rb')
				data = f.read()
				f.close()
			else:
				data = file.read()
		except:
			raise PyMSError('Load',"Could not load the BMP '%s'" % file)
		if data[:2] != 'BM':
			raise PyMSError('Load',"'%s' is not a BMP file (no BMP header)" % file)
		try:
			width, height, bitcount, compression, colors_used = \
				struct.unpack('<LLxxHL12xL',data[18:50])
			if issize and width != issize[0] and height != issize[1]:
				raise PyMSError('Load', "Invalid dimensions in the BMP '%s' (Expected %sx%s, got %sx%s)" % (file,issize[0],issize[1],width,height))
			if bitcount != 8 or not compression in [0,1]:
				raise PyMSError('Load',"The BMP '%s' is not in the correct form. It must be 256 color (8 bit), with RLE compression or no compression at all." % file)
			if not colors_used:
				colors_used = 256
			palette = []
			for x in range(0,4 * colors_used,4):
				c = list(struct.unpack('3B',data[54+x:57+x]))
				c.reverse()
				palette.append(c)
			palette.extend([[0,0,0] for _ in range(256-colors_used)])
			image = []
			if not compression:
				pad = int(math.ceil(width/4.0))*4-width
				for y in range(height):
					x = 4*colors_used+54+(width+pad)*y
					image.append(list(struct.unpack('%sB%s' % (width, 'x' * pad),data[x:x+width+pad])))
			else:
				x = 4*colors_used+54
				image.append([])
				while True:
					if data[x] == '\x00':
						if ord(data[x+1]) < 3:
							if data[x+1] == '\x02':
								xoffset, yoffset = ord(data[x+2]), ord(data[x+3])
								if not image[-1]:
									image.pop()
								elif len(image[-1]) < width and yoffset > 0:
									image[-1].extend([0] * (width - len(image[-1])))
								image.extend([[0] * width] * yoffset + [[0] * xoffset])
								x += 2
							else:
								if image[-1] and len(image[-1]) < width:
									image[-1].extend([0] * (width - len(image[-1])))
								if data[x+1] == '\x01':
									if len(image) < height:
										image.extend([[0] * width] * (height - len(image)))
									break
								image.append([])
						else:
							n = ord(data[x+1])
							image[-1].extend([ord(i) for i in data[x+2:x+2+n]])
							x += int(math.ceil(n / 2.0)) * 2
					else:
						image[-1].extend([ord(data[x+1])] * ord(data[x]))
					x += 2
			image.reverse()
			for y in range(len(image)):
				if len(image[y]) > width:
					del image[y][width:]
		except PyMSError:
			raise
		except:
			raise PyMSError('Load',"Unsupported BMP file '%s', could possibly be corrupt" % file)
		self.width = width
		self.height = height
		self.palette = palette
		self.image = image

	def load_data(self, image, palette=None):
		self.height = len(image)
		self.width = len(image[0])
		if palette:
			self.palette = list(palette)
		self.image = [list(y) for y in image]

	def save_file(self, file):
		try:
			f = open(file,'wb')
		except:
			raise PyMSError('Save',"Could not save BMP to file '%s'" % file)
		data = ''
		pad = int(math.ceil(self.width/4.0))*4-self.width
		for y in self.image:
			data = struct.pack('%sB%s' % (self.width, 'x' * pad), *y) + data
		palette = list(self.palette)
		if len(palette) < 256:
			palette.extend([[0,0,0] for _ in range(256-len(palette))])
		palette.reverse()
		for c in list(palette):
			t = list(c)
			t.reverse()
			data = struct.pack('3Bx', *t) + data
		data = struct.pack('<HH4LHH6L', 0, 0, 1078, 40, self.width, self.height, 1, 8, 0, len(data) - 1024, 0, 0, 0, 0) + data
		f.write('BM' + struct.pack('<L',len(data) + 6) + data)
		f.close()