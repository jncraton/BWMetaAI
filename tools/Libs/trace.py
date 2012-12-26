from utils import *

import sys,os

DEBUG = True

class ErrorHandler:
	def __init__(self, toplevel, prog):
		self.toplevel = toplevel
		self.prog = prog
		self.window = None
		self.buffer = ''
		if DEBUG:
			self.file = open(os.path.join(BASE_DIR,'Libs','stdeo.txt'),'w')

	def write(self, text, stdout=False):
		if DEBUG:
			self.file.write(text)
		if not self.window:
			if stdout:
				self.buffer += text
				return
			else:
				self.window = InternalErrorDialog(self.toplevel, self.prog, self)
				if self.buffer:
					text = self.buffer+'\n'+text
		self.window.text['state'] = NORMAL
		self.window.text.insert(END, text)
		self.window.text['state'] = DISABLED

class OutputHandler:
	def __init__(self, file):
		self.file = file

	def write(self, text):
		self.file.write(text, True)

def setup_trace(toplevel, prog):
	sys.stderr = ErrorHandler(toplevel, prog)
	if DEBUG:
		sys.stdout = OutputHandler(sys.stderr)