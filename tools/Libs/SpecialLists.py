from Tkinter import *
import re

class RichList(Frame):
	selregex = re.compile('\\bsel\\b')
	idregex = re.compile('(\\d+)\.(\\d+).(\\d+)(.+)?')

	def __init__(self, parent, **kwargs):
		self.entry = 0
		self.entries = []

		Frame.__init__(self, parent, bd=2, relief=SUNKEN)
		font = ('courier', -12, 'normal')
		self.hscroll = Scrollbar(self, orient=HORIZONTAL)
		self.vscroll = Scrollbar(self)
		self.text = Text(self, cursor='arrow', height=1, font=font, bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set, exportselection=0, **kwargs)
		self.text.grid(sticky=NSEW)
		self.hscroll.config(command=self.text.xview)
		self.hscroll.grid(sticky=EW)
		self.vscroll.config(command=self.text.yview)
		self.vscroll.grid(sticky=NS, row=0, column=1)
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)

		self.text.orig = self.text._w + '_orig'
		self.tk.call('rename', self.text._w, self.text.orig)
		self.tk.createcommand(self.text._w, self.dispatch)
		self.text.tag_config('Selection', background='lightblue')

		self.tag_bind = self.text.tag_bind
		self.tag_cget = self.text.tag_cget
		self.tag_config = self.text.tag_config
		self.tag_delete = self.text.tag_delete
		self.tag_lower = self.text.tag_lower
		self.tag_names = self.text.tag_names
		self.tag_raise = self.text.tag_raise
		self.tag_ranges = self.text.tag_ranges
		self.tag_unbind = self.text.tag_unbind

	def index(self, index):
		m = self.idregex.match(index)
		if m:
			index = 'entry%s.first +%sl +%sc' % (self.entries[int(m.group(1))-1],int(m.group(2))-1,int(m.group(3)))
			if m.group(4):
				index += m.group(4)
		return self.execute('index',(index,))

	def tag_add(self, tag, index, *args):
		return self.text.tag_add(tag, self.index(index), tuple(map(self.index, args)))

	def tag_nextrange(self, tag, start, end):
		return self.text.tag_nextrange(tag, self.index(start), self.index(end))

	def tag_prevrange(self, tag, start, end):
		return self.text.tag_prevrange(tag, self.index(start), self.index(end))

	def image_create(self, index, cnf={}, **kw):
		return self.text.image_create(self.index(index), cnf, **kw)

	def image_configure(self, index, **options):
		return self.text.image_config(self.index(index), **options)

	def image_cget(self, index, option):
		return self.text.image_config(self.index(index), option)

	def select(self, e):
		if e == END:
			e = -1
		if isinstance(e, int):
			n = 'entry%s' % self.entries[e]
		elif isinstance(e, str):
			n = e
		else:
			for n in self.text.tag_names(self.text.index('@%s,%s' % (e.x,e.y))):
				if n.startswith('entry'):
					break
			else:
				return
		self.text.tag_remove('Selection', '1.0', END)
		self.text.tag_add('Selection', n + '.first', n + '.last')

	def insert(self, index, text, tags=None):
		if index == END:
			index = -1
		e = 'entry%s' % self.entry
		self.text.tag_bind(e, '<Button-1>', self.select)
		if tags == None:
			tags = e
		elif isinstance(tags, str):
			tags = '%s %s' % (e,tags)
		else:
			tags = '%s %s' % (e,' '.join(tags))
		if self.entries:
			i = 'entry%s.last +1l' % self.entries[index]
		else:
			i = END
		if index == -1 or index == len(self.entries)-1:
			self.entries.append(self.entry)
		else:
			self.entries.insert(index+1, self.entry)
		self.entry += 1
		return self.execute('insert',(i, '%s\n' % text, tags))

	def delete(self, index):
		if index == ALL:
			self.entry = 0
			self.entries = []
			return self.execute('delete', ('1.0',END))
		if index == END:
			index == -1
		r = self.execute('delete',('entry%s.first' % self.entries[index],'entry%s.last' % self.entries[index]))
		if r:
			del self.entries[index]
		return r

	def execute(self, cmd, args):
		try:
			return self.tk.call((self.text.orig, cmd) + args)
		except TclError:
			return ""

	def dispatch(self, cmd, *args):
		if not cmd in ['insert','delete'] and not 'sel' in args:
			return self.execute(cmd, args)

	def get(self, index):
		return self.text.get('entry%s.first' % self.entries[index],'entry%s.last -1c' % self.entries[index])

class EditableReportSubList(RichList):
	def __init__(self, parent, selectmode, report, **kwargs):
		self.report = report
		self.lastsel = None
		self.selectmode = selectmode
		self.checkedit = None
		self.edittext = StringVar()
		self.entry = 0
		self.entries = []
		self.dctimer = None
		self.editing = False
		self.lineselect = False

		Frame.__init__(self, parent)
		font = ('courier', -11, 'normal')
		self.text = Text(self, cursor='arrow', height=1, width=1, font=font, bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, exportselection=0, **kwargs)
		self.text.pack(fill=BOTH, expand=1)

		self.text.orig = self.text._w + '_orig'
		self.tk.call('rename', self.text._w, self.text.orig)
		self.tk.createcommand(self.text._w, self.dispatch)
		self.text.tag_config('Selection', background='lightblue')
		self.text.tag_bind('Selection', '<Button-1>', self.edit)
		bind = [
			('<Button-1>', self.deselect),
			('<Up>', lambda e: self.movesel(-1)),
			('<Down>', lambda e: self.movesel(1)),
			('<Shift-Up>', lambda e: self.movesel(-1,True)),
			('<Shift-Down>', lambda e: self.movesel(1,True)),
		]
		for b in bind:
			self.text.bind(*b)

		self.tag_bind = self.text.tag_bind
		self.tag_cget = self.text.tag_cget
		self.tag_config = self.text.tag_config
		self.tag_delete = self.text.tag_delete
		self.tag_lower = self.text.tag_lower
		self.tag_names = self.text.tag_names
		self.tag_raise = self.text.tag_raise
		self.tag_ranges = self.text.tag_ranges
		self.tag_unbind = self.text.tag_unbind
		self.yview = self.text.yview

	def insert(self, index, text, tags=None):
		if index == END:
			index = -1
		e = 'entry%s' % self.entry
		self.text.tag_bind(e, '<Button-1>', lambda e,i=e: self.doselect(i,0))
		self.text.tag_bind(e, '<DoubleButton-1>', self.doubleclick)
		self.text.tag_bind(e, '<Button-3>', lambda e,i=e: self.popup(e,i))
		self.text.tag_bind(e, '<Shift-Button-1>', lambda e,i=e: self.doselect(i,1))
		self.text.tag_bind(e, '<Control-Button-1>', lambda e,i=e: self.doselect(i,2))
		if tags == None:
			tags = e
		elif isinstance(tags, str):
			tags = '%s %s' % (e,tags)
		else:
			tags = '%s %s' % (e,' '.join(tags))
		if self.entries:
			i = 'entry%s.last +1l' % self.entries[index]
		else:
			i = END
		if index == -1 or index == len(self.entries)-1:
			self.entries.append(self.entry)
		else:
			self.entries.insert(index+1, self.entry)
		self.entry += 1
		self.execute('insert',(i, text, tags))
		self.execute('insert',(i + ' lineend', '\n'))

	def doubleclick(self, e):
		if self.report.dcmd:
			self.report.dcmd(e)

	def popup(self, e, i):
		if self.report.pcmd:
			self.report.pcmd(e,i)

	def selected(self, e):
		if isinstance(e,int):
			e = 'entry%s' % e
		return not not [n for n in self.text.tag_names('%s.first' % e) if n == 'Selection']

	def deselect(self, e):
		if self.lineselect:
			self.lineselect = False
		else:
			self.lastsel = None
			self.text.tag_remove('Selection', '1.0', END)

	def movesel(self, d, s=False):
		if self.lastsel:
			l = self.lastsel
		elif self.entries:
			l = self.entries[0]
		if l:
			if not s:
				self.text.tag_remove('Selection', '1.0', END)
			r = self.text.tag_names('%s.last %+dl lineend -1c' % (l,d))
			for e in r:
				if e.startswith('entry'):
					self.text.tag_add('Selection', '%s.first' % e, '%s.last' % e)
					self.lastsel = e
					break
			else:
				self.text.tag_add('Selection', '%s.first' % self.lastsel, '%s.last' % self.lastsel)

	def doselect(self, i, t):
		self.lineselect = True
		if self.editing:
			self.text.tag_remove('Selection', '1.0', END)
			return
		if t == 0 or (t == 1 and self.selectmode == EXTENDED and self.lastsel == None) or (t == 2 and self.selectmode != SINGLE):
			if self.selectmode != MULTIPLE and t != 2:
				self.text.tag_remove('Selection', '1.0', END)
			if self.selectmode == EXTENDED:
				self.lastsel = i
			if not self.selected(i):
				self.text.tag_add('Selection',  '%s.first' % i, '%s.last' % i)
		elif t == 1 and self.selectmode == EXTENDED:
			if tuple(int(n) for n in self.text.index('%s.first' % self.lastsel).split('.')) > tuple(int(n) for n in self.text.index('%s.first' % i).split('.')):
				d = '-1l'
			else:
				d = '+1l'
			c,f = self.text.index('%s.last %s lineend -1c' % (self.lastsel,d)),self.text.index('%s.last %s lineend -1c' % (i,d))
			while d == '-1l' or c != f:
				r = self.text.tag_names(c)
				if not 'Selection' in r:
					for e in r:
						if e.startswith('entry'):
							self.text.tag_add('Selection', '%s.first' % e, '%s.last' % e)
							break
				if d == '-1l' and c == f:
					break
				c = self.text.index('%s %s lineend -1c' % (c,d))
			self.lastsel = i
		self.dctimer = self.after(300, self.nodc)
		if self.report.scmd:
			self.report.scmd()

	def nodc(self):
		self.dctimer = None

	def edit(self, e=None):
		if self.dctimer:
			self.after_cancel(self.dctimer)
			self.dctimer = None
			return
		self.editing = True
		if isinstance(e,int):
			n = 'entry%s' % self.entries[e]
		elif e == None:
			n = [n for n in self.text.tag_names('Selection.first') if n.startswith('entry')][0]
		else:
			c = '@%s,%s' % (e.x,e.y)
			n = [n for n in self.text.tag_names(c) if n.startswith('entry')][0]
		i = self.text.index(n + '.first')
		self.checkedit = self.text.get(n + '.first', n + '.last')
		self.edittext.set(self.checkedit)
		e = Entry(self.text, width=len(self.checkedit) + 5, textvariable=self.edittext, bd=1, relief=SOLID)
		e.select_range(0,END)
		e.bind('<Return>', lambda _,i=i,n=n: self.endedit(i,n))
		e.bind('<FocusOut>', lambda _,i=i,n=n: self.endedit(i,n))
		self.text.window_create('%s.first' % n, window=e)
		e.focus_set()
		self.execute('delete',(n + '.first', n + '.last'))
		self.text.tag_remove('Selection', '1.0', END)

	def endedit(self, i, n):
		t = self.edittext.get()
		if self.checkedit != t and self.report.rcmd and not self.report.rcmd(self.entries.index(int(n[5:])),self.checkedit):
			t = self.checkedit
		self.execute('delete',(i + ' linestart', i + ' lineend'))
		self.execute('insert',(i, t, n + ' Selection'))
		self.editing = False
		self.checkedit = None

	def cur_selection(self):
		s = []
		for i in self.text.tag_ranges('Selection')[::2]:
			s.extend([self.entries.index(int(n[5:])) for n in self.text.tag_names(i) if n.startswith('entry')])
		return s

	def get(self, index):
		return self.text.get('entry%s.first' % self.entries[index],'entry%s.last' % self.entries[index])

class ReportSubList(RichList):
	def __init__(self, parent, **kwargs):
		self.entry = 0
		self.entries = []
		Frame.__init__(self, parent)
		font = ('courier', -11, 'normal')
		self.text = Text(self, cursor='arrow', height=1, width=1, font=font, bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, exportselection=0, **kwargs)
		self.text.pack(fill=BOTH, expand=1)

		self.text.orig = self.text._w + '_orig'
		self.tk.call('rename', self.text._w, self.text.orig)
		self.tk.createcommand(self.text._w, self.dispatch)
		self.text.tag_configure('RightAlign', justify=RIGHT)

		self.tag_bind = self.text.tag_bind
		self.tag_cget = self.text.tag_cget
		self.tag_config = self.text.tag_config
		self.tag_delete = self.text.tag_delete
		self.tag_lower = self.text.tag_lower
		self.tag_names = self.text.tag_names
		self.tag_raise = self.text.tag_raise
		self.tag_ranges = self.text.tag_ranges
		self.tag_unbind = self.text.tag_unbind
		self.yview = self.text.yview

	def select(self, e):
		pass

	def insert(self, index, text, tags='RightAlign'):
		if index == END:
			index = -1
		e = 'entry%s' % self.entry
		self.text.tag_bind(e, '<Button-1>', self.select)
		if tags == None:
			tags = e
		elif isinstance(tags, str):
			tags = '%s %s' % (e,tags)
		else:
			tags = '%s %s' % (e,' '.join(tags))
		if self.entries:
			i = 'entry%s.last +1l' % self.entries[index]
		else:
			i = END
		if index == -1 or index == len(self.entries)-1:
			self.entries.append(self.entry)
		else:
			self.entries.insert(index+1, self.entry)
		self.entry += 1
		return self.execute('insert',(i, '%s\n' % text, tags))

class ReportList(Frame):
	def __init__(self, parent, columns=[''], selectmode=SINGLE, scmd=None, rcmd=None, pcmd=None, dcmd=None, **conf):
		self.scmd = scmd
		self.rcmd = rcmd
		self.pcmd = pcmd
		self.dcmd = dcmd
		self.entry = 0
		Frame.__init__(self, parent, bd=2, relief=SUNKEN)
		self.selectmode = selectmode
		self.panes = []
		self.columns = []
		self.vscroll = Scrollbar(self)
		self.vscroll.config(command=self.yview)
		self.vscroll.pack(side=RIGHT, fill=Y)
		p = self
		for n,title in enumerate(columns):
			end = n+1 == len(columns)
			if not end:
				c = PanedWindow(p, orient=HORIZONTAL, borderwidth=0, sashpad=0, sashwidth=4, sashrelief=FLAT)
				self.panes.append(c)
				l = Frame(c)
			else:
				l = Frame(p)
			if title == None:
				b = Button(l, text=' ', state=DISABLED)
			else:
				b = Button(l, text=title)
			b.pack(side=TOP, fill=X)
			if n == 0:
				lb = EditableReportSubList(l, selectmode, self, yscrollcommand=self.yscroll, **conf)
			else:
				lb = ReportSubList(l, yscrollcommand=self.yscroll, **conf)
			lb.pack(side=TOP, fill=BOTH, expand=1)
			l.pack(side=LEFT, fill=BOTH, expand=1)
			if not end:
				if n == 0:
					p['background'] = lb.text['background']
				c['background'] = lb.text['background']
				c.add(l)
			else:
				c = l
			if isinstance(p,PanedWindow):
				p.add(c)
			elif n == 0:
				c.pack(fill=BOTH, expand=1, padx=2, pady=2)
			else:
				c.pack()
			self.columns.append((b,lb))
			if not end:
				p = c
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', lambda a,i=0: self.move(a,i)),
			('<End>', lambda a,i=END: self.move(a,i)),
			('<Up>', lambda a,i=-1: self.move(a,i)),
			('<Left>', lambda a,i=-1: self.move(a,i)),
			('<Down>', lambda a,i=1: self.move(a,i)),
			('<Right>', lambda a,i=-1: self.move(a,i)),
			('<Prior>', lambda a,i=-10: self.move(a,i)),
			('<Next>', lambda a,i=10: self.move(a,i)),
		]
		# for d in bind:
			# parent.bind(*d)

	def select_set(self, i):
		self.columns[0][1].select(i)

	def scroll(self, e):
		if e.delta > 0:
			for c in self.columns:
				c[1].yview('scroll', -1, 'units')
		else:
			for c in self.columns:
				c[1].yview('scroll', 1, 'units')

	def move(self, e, a):
		s = self.curselection()
		if s:
			if a == END:
				a = self.size()-2
			elif a not in [0,END]:
				if a > 0:
					a = min(self.size()-1, int(s[-1]) + a)
				else:
					a = max(int(s[0]) + a,0)
			for c in self.columns:
				c[1].select_clear(0,END)
				c[1].select_set(a)
				c[1].see(a)

	def bind(self, event, cb, col=None, btn=False):
		if col != None:
			self.columns[col][not btn].bind(event,cb,True)
		else:
			for c in self.columns:
				c[not btn].bind(event,cb,True)

	def yview(self, *a):
		for c in self.columns:
			c[1].yview(*a)

	def yscroll(self, *a):
		self.vscroll.set(*a)
		for c in self.columns:
			c[1].yview(MOVETO, a[0])

	def select(self, e, l):
		sel = l.curselection()
		for c in self.columns:
			c[1].select_clear(0,END)
			for s in sel:
				c[1].select_set(s)

	def insert(self, index, text):
		if isinstance(text, str):
			text = [text]
		if len(text) < len(self.columns):
			for _ in range(len(self.columns) - len(text)):
				text.append('')
		for c,t in zip(self.columns,text):
			c[1].insert(index, t)

	def delete(self, index):
		for c in self.columns:
			c[1].delete(index)

	def cur_selection(self):
		return self.columns[0][1].cur_selection()

	def get(self, index):
		return [c[1].get(index) for c in self.columns]

	def size(self):
		return self.columns[0][1].size()

# class ReportView(Frame):
	# def __init__(self, parent, columns=[''], **conf):
		# Frame.__init__(self, parent, bd=2, relief=SUNKEN)
		# self.entry = 0
		# self.panes = []
		# self.columns = []
		# self.vscroll = Scrollbar(self, command=self.yview)
		# self.vscroll.pack(side=RIGHT, fill=Y)
		# p = self
		# while columns:
			# if len(columns) > 1:
				# c = PanedWindow(p, orient=HORIZONTAL, borderwidth=0, sashpad=2, sashwidth=0, sashrelief=RAISED)
				# self.panes.append(c)
				# l = Frame(c)
				# b = Button(l, text=columns[0])
				# b.pack(side=TOP, fill=X)
				# text = Text(l, cursor='arrow', height=1, font=font, bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set, exportselection=0)
				# text.pack(side=TOP, fill=BOTH, expand=1)
				# l.pack(side=LEFT, fill=BOTH, expand=1)
				# c['background'] = text['background']
				# if isinstance(p, PanedWindow):
					# text.orig = text._w + '_orig'
					# self.tk.call('rename', text._w, text.orig)
					# self.tk.createcommand(text._w, self.disabled)
					# self.text.tag_config('Right')
					# p.add(c)
				# else:
					# text.orig = text._w + '_orig'
					# self.tk.call('rename', text._w, text.orig)
					# self.tk.createcommand(text._w, self.dispatch)
					# text.tag_config('Selection', background='lightblue')
					# p['background'] = text['background']
					# c.pack(fill=BOTH, expand=1, padx=2, pady=2)
				# c.add(l)
				# p = c
			# else:
				# l = Frame(p)
				# b = Button(l, text=columns[0])
				# b.pack(side=TOP, fill=X)
				# text = Text(l, cursor='arrow', height=1, font=font, bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set, exportselection=0)
				# text.pack(side=TOP, fill=BOTH, expand=1)
				# l.pack(side=LEFT, fill=BOTH, expand=1)
				# if isinstance(p,PanedWindow):
					# text.orig = text._w + '_orig'
					# self.tk.call('rename', text._w, text.orig)
					# self.tk.createcommand(text._w, self.disabled)
					# self.text.tag_config('Right')
					# p.add(l)
				# else:
					# text.orig = text._w + '_orig'
					# self.tk.call('rename', text._w, text.orig)
					# self.tk.createcommand(text._w, self.dispatch)
					# text.tag_config('Selection', background='lightblue')
					# l.pack()
			# self.columns.append((b,text))
			# del columns[0]
		# bind = [
			# ('<MouseWheel>', self.scroll),
			# ('<Home>', lambda a,i=0: self.move(a,i)),
			# ('<End>', lambda a,i=END: self.move(a,i)),
			# ('<Up>', lambda a,i=-1: self.move(a,i)),
			# ('<Left>', lambda a,i=-1: self.move(a,i)),
			# ('<Down>', lambda a,i=1: self.move(a,i)),
			# ('<Right>', lambda a,i=-1: self.move(a,i)),
			# ('<Prior>', lambda a,i=-10: self.move(a,i)),
			# ('<Next>', lambda a,i=10: self.move(a,i)),
		# ]
		# for d in bind:
			# parent.bind(*d)

	# def scroll(self, e):
		# if e.delta > 0:
			# for c in self.columns:
				# c[1].yview('scroll', -2, 'units')
		# else:
			# for c in self.columns:
				# c[1].yview('scroll', 2, 'units')

	# def move(self, e, a):
		# s = self.curselection()
		# if s:
			# if a == END:
				# a = self.size()-2
			# elif a not in [0,END]:
				# if a > 0:
					# a = min(self.size()-1, int(s[-1]) + a)
				# else:
					# a = max(int(s[0]) + a,0)
			# self.columns[0][1].select_clear(0,END)
			# self.columns[0][1].select_set(a)
			# self.columns[0][1].see(a)

	# def yview(self, *a):
		# for c in self.columns:
			# c[1].yview(*a)

	# def execute(self, t, cmd, args):
		# try:
			# return self.tk.call((t.orig, cmd) + args)
		# except TclError:
			# return ""

	# def insert(self, index, text):
		# if isinstance(text, str):
			# text = [text]
		# if len(text) < len(self.columns):
			# for _ in range(len(self.columns) - len(text)):
				# text.append('')
		# l = False
		# for c,t in zip(self.columns,text):
			# if l:
				# self.execute(c[1],'insert',(i, text + '\n', 'entry%s' % self.entry, 'right'))
			# else:
				# self.execute(c[1],'insert',(i, text + '\n', 'entry%s' % self.entry))

class TreeList(Frame):
	selregex = re.compile('\\bsel\\b')

	def __init__(self, parent, selectmode=SINGLE, groupsel=True):
		self.selectmode = selectmode
		self.lastsel = None
		self.groupsel = groupsel
		self.entry = 0
		self.groups = []
		self.entries = {}
		self.icons = [PhotoImage(file='Images\\treeclose.gif'),PhotoImage(file='Images\\treeopen.gif')]

		Frame.__init__(self, parent, bd=2, relief=SUNKEN)
		font = ('courier', -12, 'normal')
		self.hscroll = Scrollbar(self, orient=HORIZONTAL)
		self.vscroll = Scrollbar(self)
		self.text = Text(self, cursor='arrow', height=1, font=font, bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set, exportselection=0)
		self.text.configure(tabs=self.tk.call("font", "measure", self.text["font"], "-displayof", self, '  ')+9)
		self.text.grid(sticky=NSEW)
		self.hscroll.config(command=self.text.xview)
		self.hscroll.grid(sticky=EW)
		self.vscroll.config(command=self.text.yview)
		self.vscroll.grid(sticky=NS, row=0, column=1)
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)

		self.bind = self.text.bind

		self.text.orig = self.text._w + '_orig'
		self.tk.call('rename', self.text._w, self.text.orig)
		self.tk.createcommand(self.text._w, self.dispatch)
		self.text.tag_config('Selection', background='lightblue')

	def execute(self, cmd, args):
		try:
			return self.tk.call((self.text.orig, cmd) + args)
		except TclError:
			return ""

	def dispatch(self, cmd, *args):
		if not cmd in ['insert','delete'] and not 'sel' in args:
			return self.execute(cmd, args)

	def index(self, e, g=None, i=''):
		if g == None:
			g = self.groups
		n = filter(lambda t: ((isinstance(t,list) and t[0] == e) or (isinstance(t,int) and t == e)),g)
		if n:
			return '%s%s' % (i,g.index(n[0]))
		for n,f in enumerate(g):
			if isinstance(f,list):
				d = self.index(e, f[1], '%s%s.' % (i,n))
				if d:
					return d

	def cur_selection(self):
		s = []
		for i in self.text.tag_ranges('Selection')[::2]:
			s.extend([int(n[5:]) for n in self.text.tag_names(i) if n.startswith('entry')])
		return s

	def selected(self, e):
		if isinstance(e,int):
			e = 'entry%s' % e
		return not not [n for n in self.text.tag_names('%s.first' % e) if n == 'Selection']

	def select(self, i, t):
		if t == 0 or (t == 1 and self.selectmode == EXTENDED and self.lastsel == None) or (t == 2 and self.selectmode != SINGLE):
			if self.selectmode != MULTIPLE and t != 2:
				self.text.tag_remove('Selection', '1.0', END)
			if self.selectmode == EXTENDED:
				self.lastsel = i
			if not self.selected(i):
				self.text.tag_add('Selection',  'entry%s.first' % i, 'entry%s.last' % i)
		elif t == 1 and self.selectmode == EXTENDED:
			if tuple(int(n) for n in self.text.index('entry%s.first' % self.lastsel).split('.')) > tuple(int(n) for n in self.text.index('entry%s.first' % i).split('.')):
				d = '-1l'
			else:
				d = '+1l'
			c,f = self.text.index('entry%s.last %s lineend -1c' % (self.lastsel,d)),self.text.index('entry%s.last %s lineend -1c' % (i,d))
			while c != f:
				r = self.text.tag_names(c)
				for e in r:
					if e.startswith('entry') and (self.groupsel or self.entries[int(e[5:])][2] == None) and not 'Selection' in r:
						self.text.tag_add('Selection', '%s.first' % e, '%s.last' % e)
				c = self.text.index('%s %s lineend -1c' % (c,d))
			self.lastsel = i

	def write_item(self, e, i, text, d):
		self.execute('insert',(e, text, 'entry%s' % i))
		self.execute('insert',(e, '\t' * (d+1)))
		self.execute('insert',('entry%s.last' % i, '\n'))
		self.text.tag_bind('entry%s' % i, '<Button-1>', lambda e,i=i: self.select(i,0))
		self.text.tag_bind('entry%s' % i, '<Shift-Button-1>', lambda e,i=i: self.select(i,1))
		self.text.tag_bind('entry%s' % i, '<Control-Button-1>', lambda e,i=i,t=0: self.select(i,2))

	def write_group(self, e, i, text, d, open):
		self.execute('insert',(e, text, 'entry%s' % i))
		self.execute('insert',(e, '\t' * d + '  '))
		self.execute('insert',('entry%s.last' % i, '\n'))
		if self.groupsel:
			self.text.tag_bind('entry%s' % i, '<Button-1>', lambda e,i=i: self.select(i,0))
			self.text.tag_bind('entry%s' % i, '<Shift-Button-1>', lambda e,i=i: self.select(i,1))
			self.text.tag_bind('entry%s' % i, '<Control-Button-1>', lambda e,i=i,t=0: self.select(i,2))
		self.text.image_create('entry%s.first -1c' % i, image=self.icons[open])
		self.text.tag_add('node%s' % d, 'entry%s.first -2c' % i, 'entry%s.first -1c' % i)
		self.text.tag_bind('node%s' % d, '<Button-1>', lambda e,d=d: self.toggle(e,d))

	def toggle(self, e, d):
		c = '@%s,%s' % (e.x,e.y)
		n = [n for n in self.text.tag_names('%s +2c' % c) if n.startswith('entry')]
		i = int(n[0][5:])
		if self.entries[i][2][2]:
			self.entries[i][2][2] = False
			self.text.image_configure(c, image=self.icons[0])
			n = self.text.tag_nextrange('node%s' % d, '%s +1c' % c)
			while not n and d:
				d -= 1
				n = self.text.tag_nextrange('node%s' % d, '%s +1c' % c)
			if not n:
				ids = ('entry%s.last +1c' % i, '%s -1c' % END)
			else:
				ids = ('entry%s.last +1c' % i, n[0] + ' linestart')
			if self.groupsel and self.text.tag_nextrange('Selection', *ids):
				self.select(i)
			return self.execute('delete', ids)
		else:
			self.entries[i][2][2] = True
			self.text.image_configure(c, image=self.icons[1])
			def do_insert(t,d,o=1):
				for e in t:
					if isinstance(e, list):
						self.write_group('%s +%sl linestart' % (c,o), e[0], self.entries[e[0]][3], d+1, e[2])
						if e[2]:
							o = do_insert(e[1],d+1,o+1)
						else:
							o += 1
					else:
						self.write_item('%s +%sl linestart' % (c,o), e, self.entries[e][3], d+1)
						o += 1
				return o
			do_insert(self.entries[i][2][1],d)

	def delete(self, index):
		if index == ALL:
			self.entry = 0
			self.groups = []
			self.entries = {}
			self.execute('delete', ('1.0', END))
		else:
			if isinstance(index, int):
				index = self.index(index)
			ids = list(int(i) for i in index.split('.'))
			p,t = None,self.groups
			if len(ids) > 1:
				for i in ids[:-1]:
					p = t
					t = t[i][1]
			i = ids[-1]
			r = self.text.tag_ranges('entry%s' % t[i][0])
			if isinstance(t[i], list):
				if r:
					d = self.entries[t[i][0]][0]
					n = self.text.tag_nextrange('node%s' % d, r[1])
					while not n and d:
						d -= 1
						n = self.text.tag_nextrange('node%s' % d, r[1])
					if not n:
						ids = ('%s linestart' % r[0], '%s -1c' % END)
					else:
						ids = ('%s linestart' % r[0], '%s linestart' % n[0])
					if self.text.tag_nextrange('Selection', *ids) and p:
						self.select(p[ids[-2]][0])
					self.execute('delete', ids)
				def remove(g):
					if isinstance(g, list):
						map(remove, g[1])
						del self.entries[g[0]]
					else:
						del self.entries[g]
				map(remove, t[i][1])
				del self.entries[t[i][0]]
			else:
				if r:
					self.execute('delete',('%s linestart' % r[0],'%s lineend' % r[1]))
				del self.entries[t[i]]
			del t[i]

	# Group: None = not group, True = open by default, False = closed by default
	def insert(self, index, text, group=None):
		ids = list(int(i) for i in index.split('.'))
		p,t = None,self.groups
		vis = True
		if len(ids) > 1:
			for i in ids[:-1]:
				if vis and (not self.text.tag_ranges('entry%s' % t[i][0]) or not t[i][2]):
					vis = False
				p = t
				t = t[i][1]
		i = ids[-1]
		if vis:
			if t:
				p = t
			if p:
				e = p[i]
				if i == -1:
					while isinstance(e,list) and i == -1:
						if e[2] and e[1]:
							e = e[1][-1]
						else:
							e = e[0]
					e = 'entry%s.last lineend +1c' % e
				elif isinstance(e, list):
					e = 'entry%s.first linestart' % e[0]
				else:
					e = 'entry%s.first linestart' % e
			else:
				e = '1.0'
			if group != None:
				self.write_group(e, self.entry, text, index.count('.'), group)
			else:
				self.write_item(e, self.entry, text, index.count('.'))
		if group != None:
			self.entries[self.entry] = [index.count('.'),t,[self.entry,[],group],text]
		else:
			self.entries[self.entry] = [index.count('.'),t,None,text]
		if ids[-1] == -1:
			ids[-1] = len(t)
			if group != None:
				t.append(self.entries[self.entry][2])
			else:
				t.append(self.entry)
		else:
			if group != None:
				t.insert(ids[-1], self.entries[self.entry][2])
			else:
				t.insert(ids[-1], self.entry)
		self.entry += 1
		return '.'.join(str(i) for i in ids)

	# def insert_item(self, index, text):
		# ids = list(int(i) for i in index.split('.'))
		# p,t = None,self.groups
		# vis = True
		# if len(ids) > 1:
			# for i in ids[:-1]:
				# if vis and (not self.text.tag_ranges('entry%s' % t[i][0]) or not t[i][2]):
					# vis = False
				# p = t
				# t = t[i][1]
		# i = ids[-1]
		# if vis:
			# if t:
				# p = t
			# if p:
				# e = p[i]
				# if i == -1:
					# while isinstance(e,list) and i == -1:
						# if e[2] and e[1]:
							# e = e[1][-1]
						# else:
							# e = e[0]
					# e = 'entry%s.last lineend +1c' % e
				# elif isinstance(e, list):
					# e = 'entry%s.first linestart' % e[0]
				# else:
					# e = 'entry%s.first linestart' % e
			# else:
				# e = '1.0'
			# self.write_item(e, self.entry, text, index.count('.'))
		# self.entries[self.entry] = [index.count('.'),t,None,text]
		# if ids[-1] == -1:
			# ids[-1] = len(t)
			# t.append(self.entry)
		# else:
			# t.insert(ids[-1], self.entry)
		# self.entry += 1
		# return '.'.join(str(i) for i in ids)

	# def insert_group(self, index, text, open=False):
		# ids = list(int(i) for i in index.split('.'))
		# p,t = None,self.groups
		# vis = True
		# if len(ids) > 1:
			# for i in ids[:-1]:
				# if vis and (not self.text.tag_ranges('entry%s' % t[i][0]) or not t[i][2]):
					# vis = False
				# p = t
				# t = t[i][1]
		# i = ids[-1]
		# if vis:
			# if t:
				# p = t
			# if p:
				# e = p[i]
				# if i == -1:
					# while isinstance(e,list) and i == -1:
						# if e[2] and e[1]:
							# e = e[1][-1]
						# else:
							# e = e[0]
					# e = 'entry%s.last lineend +1c' % e
				# elif isinstance(e, list):
					# e = 'entry%s.first linestart' % e[0]
				# else:
					# e = 'entry%s.first linestart' % e
			# else:
				# e = '1.0'
			# self.write_group(e, self.entry, text, index.count('.'), open)
		# self.entries[self.entry] = [index.count('.'),t,[self.entry,[],open],text]
		# if ids[-1] == -1:
			# ids[-1] = len(t)
			# t.append(self.entries[self.entry][2])
		# else:
			# t.insert(ids[-1], self.entries[self.entry][2])
		# self.entry += 1
		# return '.'.join(str(i) for i in ids)

	def get(self, entry, info=False):
		if isinstance(entry,str) or isinstance(entry,unicode):
			ids = list(int(i) for i in index.split('.'))
			t = self.groups
			if len(ids) > 1:
				for i in ids[:-1]:
					t = t[i][1]
			entry = t[t[-1]]
			if isinstnce(entry,list):
				entry = t[0]
		if info:
			if self.entries[entry][2]:
				return (self.entries[entry][3],self.entries[entry][2][2],not not self.text.tag_ranges('entry%s' % entry))
			return (self.entries[entry][3],not not self.text.tag_ranges('entry%s' % entry))
		return self.entries[entry][3]


		# else:
			# print '\t',cmd,args

# import TBL,DAT
# class Test(Tk):
	# def __init__(self):
		# Tk.__init__(self)
		# self.title('My Lists Test')

# #ReportList:
		# self.rl = ReportList(self, ['One','Two','Three'])
		# self.rl.pack(fill=BOTH, expand=1)
		# for n in range(50):
			# self.rl.insert(END, [str(n+x) for x in range(3)])
		# self.rl.bind('<ButtonRelease-1>', self.sel)

	# def sel(self, e):
		# s = self.rl.curselection()
		# for i in s:
			# print '\t',self.rl.get(i)

# #TreeList:
		# self.tl = TreeList(self)
		# self.tl.pack(fill=BOTH, expand=1)
		# self.tl.insert('-1', 'Zerg', False)
		# self.tl.insert('-1', 'Terran', False)
		# self.tl.insert('-1', 'Protoss', False)
		# self.tl.insert('-1', 'Other', False)

		# tbl = TBL.TBL()
		# tbl.load_file('Libs\\MPQ\\rez\\stat_txt.tbl')
		# dat = DAT.UnitsDAT()
		# dat.load_file('Libs\\MPQ\\arr\\units.dat')

		# groups = [{},{},{},{}]
		# for i,n in enumerate(TBL.decompile_string(s) for s in tbl.strings[:228]):
			# g = dat.get_value(i,'StarEditGroupFlags')
			# s = n.split('<0>')
			# found = False
			# if s[0] == 'Zerg Zergling':
				# g = 1|2|4
			# for f in [1,2,4,3]:
				# if (f != 3 and g & f) or (f == 3 and not found):
					# if not s[2] in groups[f-1]:
						# if f == 4:
							# e = '2'
						# elif f == 3:
							# e = '3'
						# else:
							# e = str(f-1)
						# groups[f-1][s[2]] = self.tl.insert(e + '.-1', s[2], False)
					# self.tl.insert(groups[f-1][s[2]] + '.-1', '[%s] %s%s' % (i,s[0],['',' (%s)' % s[1]][s[1] != '*']))
					# found = True
		# self.tl.insert('-1', 'Zerg', True)
		# self.tl.insert('0.-1', 'Ground Units', True)
		# self.tl.insert('0.0.-1', 'Zerg Zergling')
		# self.tl.insert('0.0.-1', 'Zerg Zergling', False)
		# self.tl.insert('-1', 'Terran', False)
		# self.tl.insert('0', 'Test', False)
		# self.tl.bind('<Button-1>', self.test)
		# self.tl.bind('<Alt-d>', self.delete)
		# print self.tl.groups

	# def test(self, e):
		# print self.tl.text.tag_ranges('Selection')
		# s = self.tl.cur_selection()
		# print s
		# if s:
			# print self.tl.get(s[0],True)

	# def delete(self, e):
		# self.tl.delete(self.tl.cur_selection())

# #RichList:
		# self.rl = RichList(self)
		# self.rl.pack(fill=BOTH, expand=1)
		# self.rl.insert(END, 'test 1')
		# self.rl.insert(END, '  testing')
		# self.rl.insert(END, 'test 3')
		# print self.rl.index('2.1.0 lineend')
		# self.rl.text.tag_config('r', background='#FF0000')
		# print self.rl.tag_add('r','3.1.1','3.1.0 lineend -1c')
		# self.img = PhotoImage(file='Images\\treeopen.gif')
		# self.rl.image_create('2.1.1', image=self.img)
		# self.rl.bind('<Enter>', self.enter)

	# def enter(self, e):
		# self.rl.delete(0)

# def main():
	# gui = Test()
	# gui.mainloop()

# if __name__ == '__main__':
	# main()