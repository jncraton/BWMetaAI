from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs import AIBIN, TBL, DAT

try:
    from Tkinter import *
    from tkMessageBox import *
    import tkFileDialog, tkColorChooser
    from thread import start_new_thread
except ImportError:
    # Python 3
    from tkinter import *
    from tkinter.messagebox import *
    import tkinter.filedialog as tkFileDialog
    import tkinter.colorchooser as tkColorChooser
    from _thread import start_new_thread

from shutil import copy
import optparse, os, re, webbrowser, sys

VERSION = (2,4)
LONG_VERSION = 'v%s.%s)' % VERSION

IMG_CACHE = {}
def get_img(n):
	if n in IMG_CACHE:
		return IMG_CACHE[n]
	IMG_CACHE[n] = PhotoImage(file=os.path.join(BASE_DIR, 'Images','%s.gif)' % n))
	return IMG_CACHE[n]

types = [
	('byte','A number in the range 0 to 255'),
	('word','A number in the range 0 to 65535'),
	('dword','A number in the range 0 to 4294967295'),
	('unit','A unit ID from 0 to 227, or a full unit name from stat_txt.tbl'),
	('building','Same as unit type, but only units that are Buildings, Resource Miners, and Overlords'),
	('military','Same as unit type, but only for a unit to train (not a Building, Resource Miners, or Overlords)'),
	('gg_military','Same as Military type, but only for defending against an enemy Ground unit attacking your Ground unit'),
	('ag_military','Same as Military type, but only for defending against an enemy Air unit attacking your Ground unit'),
	('ga_military','Same as Military type, but only for defending against an enemy Ground unit attacking your Air unit'),
	('aa_military','Same as Military type, but only for defending against an enemy Air unit attacking your Air unit'),
	('upgrade','An upgrade ID from 0 to 60, or a full upgrade name from stat_txt.tbl'),
	('technology','An technology ID from 0 to 43, or a full technology name from stat_txt.tbl'),
	('string',"A string of any characters (except for nulls: <0>) in TBL string formatting (use <40> for an open parenthesis '(', <41> for a close parenthesis ')', and <44> for a comma ',')"),
	('block','The label name of a block in the code'),
]
TYPE_HELP = odict()
for t,h in types:
	TYPE_HELP[t] = h
cmds = [
	('Header',[
		('farms_notiming','Build necessary farms only when it hits the maximum supply available.'),
		('farms_timing','Build necessary farms with a correct timing, so nothing is paused by a maximum supply limit hit.'),
		('start_areatown','Starts the AI Script for area town management.'),
		('start_campaign','Starts the AI Script for Campaign.'),
		('start_town','Starts the AI Script for town management.'),
		('transports_off','Tells the AI to not worry about managing transports until check_transports is called.'),
	]),
	('Build/Attack/Defense order',[
		('attack_add','Add Byte Military to the current attacking party.'),
		('attack_clear','Clear the attack data.'),
		('attack_do','Attack the enemy with the current attacking party.'),
		('attack_prepare','Prepare the attack.'),
		('build','Build Building until it commands Byte(1) of them, at priority Byte(2).'),
		('defensebuild_aa','Build Byte Military to defend against enemy attacking air units, when air units are attacked.'),
		('defensebuild_ag','Build Byte Military to defend against enemy attacking air units, when ground units are attacked.'),
		('defensebuild_ga','Build Byte Military to defend against enemy attacking ground units, when air units are attacked.'),
		('defensebuild_gg','Build Byte Military to defend against enemy attacking ground units, when ground units are attacked.'),
		('defenseclear_aa','Clear defense against enemy attacking air units, when air units are attacked.'),
		('defenseclear_ag','Clear defense against enemy attacking air units, when ground units are attacked.'),
		('defenseclear_ga','Clear defense against enemy attacking ground units, when air units are attacked.'),
		('defenseclear_gg','Clear defense against enemy attacking ground units, when ground units are attacked.'),
		('defenseuse_aa','Use Byte Military to defend against enemy attacking air units, when air units are attacked.'),
		('defenseuse_ag','Use Byte Military to defend against enemy attacking air units, when ground units are attacked.'),
		('defenseuse_ga','Use Byte Military to defend against enemy attacking ground units, when air units are attacked.'),
		('defenseuse_gg','Use Byte Military to defend against enemy attacking ground units, when ground units are attacked.'),
		('guard_resources','Send units of type Military to guard as many resources spots as possible(1 per spot).'),
		('tech','Research technology Technology, at priority Byte.'),
		('train','Train Military until it commands Byte of them.'),
		('upgrade','Research upgrade Upgrade up to level Byte(1), at priority Byte(2).'),
		('wait','Wait for Word tenths of second in normal game speed.'),
		('wait_finishattack','Wait until attacking party has finished to attack.'),
		('wait_build','Wait until computer commands Byte Building.'),
		('wait_buildstart','Wait until construction of Byte Unit has started.'),
		('wait_train','Wait until computer commands Byte Military.'),
		('clear_combatdata','Clear previous combat data.'),
		('nuke_rate','Tells the AI to launch nukes every Byte minutes.'),
	]),
	('Flow control',[
		('call','Call Block as a sub-routine.'),
		('enemyowns_jump','If enemy has a Unit, jump to Block.'),
		('enemyresources_jump','If enemy has at least Word(1) minerals and Word(2) gas then jump in Block.'),
		('goto','Jump to Block.'),
		('groundmap_jump','If it is a ground map(in other words, if the enemy is reachable without transports), jump to Block.'),
		('killable','Allows the current thread to be killed by another one.'),
		('kill_thread','Kill the current thread.'),
		('notowns_jump','If computer doesn\'t have a Unit, jump to Block.'),
		('race_jump','According to the enemy race, jump in Block(1) if enemy is Terran, Block(2) if Zerg or Block(3) if Protoss.'),
		('random_jump','There is Byte chances out of 256 to jump to Block.'),
		('resources_jump','If computer has at least Word(1) minerals and Word(2) gas then jump in Block.'),
		('return','Return to the flow point of the call command.'),
		('stop','Stop script code execution. Often used to close script blocks called simultaneously.'),
		('time_jump','Jumps to Block if Byte normal game minutes have passed in the game.'),
		('region_size','Something to do with an enemy being in an unknown radius of the computer.'),
		('panic','Appears to trigger Block if attacked. Still unclear.'),
		('rush','Depending on Byte, it detects combinations of units and buildings either built or building, and jumps to Block'),
		('debug','Show debug string String and continue in Block.'),
	]),
	('Multiple threads',[
		('expand','Run code at Block for expansion number Byte.'),
		('multirun','Run simultaneously code (so in another thread) at Block.'),
	]),
	('Miscellaneous',[
		('create_nuke','Create a nuke. Should only be used in campaign scripts.'),
		('create_unit','Create Unit at map position (x,y) where x = Word(1) and y = Word(2). Should only be used in campaign scripts.'),
		('define_max','Define maximum number of Unit to Byte.'),
		('give_money','Give 2000 ore and gas if owned resources are low. Should only be used in campaign scripts.'),
		('nuke_pos','Launch a nuke at map position (x,y) where x = Word(1) and y = Word(2). Should only be used in campaign scripts.'),
		('send_suicide','Send all units to suicide mission. Byte determines which type, 0 = Strategic suicide; 1 = Random suicide.'),
		('set_randomseed','Set random seed to DWord(1).'),
		('switch_rescue','Switch computer to rescuable passive mode.'),
		('help_iftrouble','Ask allies for help if ever in trouble.'),
		('check_transports','Used in combination with header command transports_off, the AI will build and keep as many transports as was set by the define_max (max 5?) and use them for drops and expanding.'),
		('creep','Effects the placement of towers (blizzard always uses 3 or 4 for Byte, see link below)'),
		('get_oldpeons','Pull Byte existing workers from the main base to the expansion, but the main base will train the workers to replace the ones you took. Useful if you need workers as quickly as possible at the expansion.'),
	]),
	('StarEdit',[
		('disruption_web','Disruption Web at selected location. (STAREDIT)'),
		('enter_bunker','Enter Bunker in selected location. (STAREDIT)'),
		('enter_transport','Enter in nearest Transport in selected location. (STAREDIT)'),
		('exit_transport','Exit Transport in selected location. (STAREDIT)'),
		('harass_location','AI Harass at selected location. (STAREDIT)'),
		('junkyard_dog','Junkyard Dog at selected location. (STAREDIT)'),
		('make_patrol','Make units patrol in selected location. (STAREDIT)'),
		('move_dt','Move Dark Templars to selected location. (STAREDIT)'),
		('nuke_location','Nuke at selected location. (STAREDIT)'),
		('player_ally','Make selected player ally. (STAREDIT)'),
		('player_enemy','Make selected player enemy. (STAREDIT)'),
		('recall_location','Recall at selected location. (STAREDIT)'),
		('sharedvision_off','Disable Shared Vision for selected player. (STAREDIT)'),
		('sharedvision_on','Enable Shared vision for selected player. (STAREDIT)'),
		('value_area','Value this area higher. (STAREDIT)'),
		('set_gencmd','Set generic command target. (STAREDIT)'),
	]),
	('Unknown',[
		('allies_watch','The use of this command is unknown. Takes Byte and Block as parameters.'),
		('capt_expand','The use of this command is unknown. Takes no parameter.'),
		('default_min','The use of this command is unknown. Takes Byte as parameter.'),
		('defaultbuild_off','The use of this command is unknown. Takes no parameter.'),
		('do_morph','The use of this command is unknown. Takes no parameters.'),
		('fake_nuke','The use of this command is unknown. Takes no parameters.'),
		('guard_all','The use of this command is unknown. Takes no parameters.'),
		('if_owned','The use of this command is unknown. Takes Unit and Block as parameters.'),
		('max_force','The use of this command is unknown. Takes Word as parameter.'),
		('place_guard','The use of this command is unknown. Takes Unit and Byte as parameters.'),
		('player_need','The use of this command is unknown. Takes Byte and Building as parameters.'),
		('scout_with','This command is unused.'),
		('set_attacks','The use of this command is unknown. Takes Byte as parameter.'),
		('target_expansion','The use of this command is unknown. Takes no parameter.'),
		('try_townpoint','The use of this command is unknown. Takes Byte and Block as parameters.'),
		('wait_force','The use of this command is unknown. Takes Byte and Unit as parameters.'),
	]),
	('Undefined',[
		('build_bunkers','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('build_turrets','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('default_build','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('easy_attack','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('eval_harass','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('fatal_error','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('harass_factor','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('if_dif','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('if_towns','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('implode','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('prep_down','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('quick_attack','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('wait_bunkers','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('wait_secure','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('wait_turrets','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('wait_upgrades','The definition of this command is unknown. It is never used in Blizzard scripts.'),
	]),
]
CMD_HELP = odict()
for s,cmdl in cmds:
	CMD_HELP[s] = odict()
	for c,h in cmdl:
		CMD_HELP[s][c] = h
#
class FindReplaceDialog(PyMSDialog):
	def __init__(self, parent):
		self.resettimer = None
		PyMSDialog.__init__(self, parent, 'Find/Replace', grabwait=False)

	def widgetize(self):
		self.resizable(True, False)

		self.find = StringVar()
		self.replacewith = StringVar()
		self.replace = IntVar()
		self.inselection = IntVar()
		self.casesens = IntVar()
		self.regex = IntVar()
		self.multiline = IntVar()
		self.updown = IntVar()
		self.updown.set(1)

		l = Frame(self)
		f = Frame(l)
		s = Frame(f)
		Label(s, text='Find:', anchor=E, width=12).pack(side=LEFT)
		self.findentry = TextDropDown(s, self.find, self.parent.parent.findhistory, 30)
		self.findentry.c = self.findentry['bg']
		self.findentry.pack(fill=X)
		self.findentry.entry.selection_range(0, END)
		self.findentry.focus_set()
		s.pack(fill=X)
		s = Frame(f)
		Label(s, text='Replace With:', anchor=E, width=12).pack(side=LEFT)
		self.replaceentry = TextDropDown(s, self.replacewith, self.parent.parent.replacehistory, 30)
		self.replaceentry.pack(fill=X)
		s.pack(fill=X)
		f.pack(side=TOP, fill=X, pady=2)
		f = Frame(l)
		self.selectcheck = Checkbutton(f, text='In Selection', variable=self.inselection, anchor=W)
		self.selectcheck.pack(fill=X)
		Checkbutton(f, text='Case Sensitive', variable=self.casesens, anchor=W).pack(fill=X)
		Checkbutton(f, text='Regular Expression', variable=self.regex, anchor=W, command=lambda i=1: self.check(i)).pack(fill=X)
		self.multicheck = Checkbutton(f, text='Multi-Line', variable=self.multiline, anchor=W, state=DISABLED, command=lambda i=2: self.check(i))
		self.multicheck.pack(fill=X)
		f.pack(side=LEFT, fill=BOTH)
		f = Frame(l)
		lf = LabelFrame(f, text='Direction')
		self.up = Radiobutton(lf, text='Up', variable=self.updown, value=0, anchor=W)
		self.up.pack(fill=X)
		self.down = Radiobutton(lf, text='Down', variable=self.updown, value=1, anchor=W)
		self.down.pack()
		lf.pack()
		f.pack(side=RIGHT, fill=Y)
		l.pack(side=LEFT, fill=BOTH, pady=2, expand=1)

		l = Frame(self)
		Button(l, text='Find Next', command=self.findnext).pack(fill=X, pady=1)
		Button(l, text='Count', command=self.count).pack(fill=X, pady=1)
		self.replacebtn = Button(l, text='Replace', command=lambda i=1: self.findnext(replace=i))
		self.replacebtn.pack(fill=X, pady=1)
		self.repallbtn = Button(l, text='Replace All', command=self.replaceall)
		self.repallbtn.pack(fill=X, pady=1)
		Button(l, text='Close', command=self.ok).pack(fill=X, pady=4)
		l.pack(side=LEFT, fill=Y, padx=2)

		self.bind('<Return>', self.findnext)
		self.bind('<FocusIn>', lambda e,i=3: self.check(i))

		if 'findreplacewindow' in self.parent.parent.settings:
			loadsize(self, self.parent.parent.settings, 'findreplacewindow')

		return self.findentry

	def check(self, i):
		if i == 1:
			if self.regex.get():
				self.multicheck['state'] = NORMAL
			else:
				self.multicheck['state'] = DISABLED
				self.multiline.set(0)
		if i in [1,2]:
			s = [NORMAL,DISABLED][self.multiline.get()]
			self.up['state'] = s
			self.down['state'] = s
			if s == DISABLED:
				self.updown.set(1)
		elif i == 3:
			if self.parent.text.tag_ranges('Selection'):
				self.selectcheck['state'] = NORMAL
			else:
				self.selectcheck['state'] = DISABLED
				self.inselection.set(0)

	def findnext(self, key=None, replace=0):
		f = self.find.get()
		if not f in self.parent.parent.findhistory:
			self.parent.parent.findhistory.append(f)
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except:
				self.resettimer = self.after(1000, self.updatecolor)
				self.findentry['bg'] = '#FFB4B4'
				return
			if replace:
				rep = self.replacewith.get()
				if not rep in self.parent.parent.replacehistory:
					self.parent.parent.replacehistory.append(rep)
				item = self.parent.text.tag_ranges('Selection')
				if item and r.match(self.parent.text.get(*item)):
					ins = r.sub(rep, self.parent.text.get(*item))
					self.parent.text.delete(*item)
					self.parent.text.insert(item[0], ins)
					self.parent.text.update_range(item[0])
			if self.multiline.get():
				m = r.search(self.parent.text.get(INSERT, END))
				if m:
					self.parent.text.tag_remove('Selection', '1.0', END)
					s,e = '%s +%sc)' % (INSERT, m.start(0)),'%s +%sc)' % (INSERT,m.end(0))
					self.parent.text.tag_add('Selection', s, e)
					self.parent.text.mark_set(INSERT, e)
					self.parent.text.see(s)
					self.check(3)
				else:
					p = self
					if key and key.keycode == 13:
						p = self.parent
					askquestion(parent=p, title='Find', message="Can't find text.", type=OK)
			else:
				u = self.updown.get()
				s,lse,rlse,e = ['-','+'][u],['lineend','linestart'][u],['linestart','lineend'][u],[self.parent.text.index('1.0 lineend'),self.parent.text.index(END)][u]
				i = self.parent.text.index(INSERT)
				if i == e:
					return
				if i == self.parent.text.index('%s %s)' % (INSERT, rlse)):
					i = self.parent.text.index('%s %s1lines %s)' % (INSERT, s, lse))
				n = -1
				while not u or i != e:
					if u:
						m = r.search(self.parent.text.get(i, '%s %s)' % (i, rlse)))
					else:
						m = None
						a = r.finditer(self.parent.text.get('%s %s)' % (i, rlse), i))
						c = 0
						for x,f in enumerate(a):
							if x == n or n == -1:
								m = f
								c = x
						n = c - 1
					if m:
						self.parent.text.tag_remove('Selection', '1.0', END)
						if u:
							s,e = '%s +%sc)' % (i,m.start(0)),'%s +%sc)' % (i,m.end(0))
							self.parent.text.mark_set(INSERT, e)
						else:
							s,e = '%s linestart +%sc)' % (i,m.start(0)),'%s linestart +%sc)' % (i,m.end(0))
							self.parent.text.mark_set(INSERT, s)
						self.parent.text.tag_add('Selection', s, e)
						self.parent.text.see(s)
						self.check(3)
						break
					if (not u and n == -1 and self.parent.text.index('%s lineend)' % i) == e) or i == e:
						p = self
						if key and key.keycode == 13:
							p = self.parent
						askquestion(parent=p, title='Find', message="Can't find text.", type=OK)
						break
					i = self.parent.text.index('%s %s1lines %s)' % (i, s, lse))
				else:
					p = self
					if key and key.keycode == 13:
						p = self.parent
					askquestion(parent=p, title='Find', message="Can't find text.", type=OK)

	def count(self):
		f = self.find.get()
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except:
				self.resettimer = self.after(1000, self.updatecolor)
				self.findentry['bg'] = '#FFB4B4'
				return
			askquestion(parent=self, title='Count', message='%s matches found.)' % len(r.findall(self.parent.text.get('1.0', END))), type=OK)

	def replaceall(self):
		f = self.find.get()
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except:
				self.resettimer = self.after(1000, self.updatecolor)
				self.findentry['bg'] = '#FFB4B4'
				return
			text = r.subn(self.replacewith.get(), self.parent.text.get('1.0', END))
			if text[1]:
				self.parent.text.delete('1.0', END)
				self.parent.text.insert('1.0', text[0].rstrip('\n'))
				self.parent.text.update_range('1.0')
			askquestion(parent=self, title='Replace Complete', message='%s matches replaced.)' % text[1], type=OK)

	def updatecolor(self):
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.findentry['bg'] = self.findentry.c

	def destroy(self):
		self.parent.parent.settings['findreplacewindow'] = self.winfo_geometry()
		PyMSDialog.withdraw(self)

class CodeColors(PyMSDialog):
	def __init__(self, parent):
		self.cont = False
		self.tags = dict(parent.text.tags)
		self.info = odict()
		self.info['Block'] = 'The color of a --block-- in the code.'
		self.info['Keywords'] = 'Keywords:\n    extdef  aiscript  bwscript'
		self.info['Types'] = 'Variable types:\n    ' + '  '.join(AIBIN.types)
		self.info['Commands'] = 'The color of all the commands.'
		self.info['Number'] = 'The color of all numbers.'
		self.info['TBL Format'] = 'The color of TBL formatted characters, like null: <0>'
		self.info['Info Comment'] = 'The color of a one line Extra Information Comment either for a script or block.'
		self.info['MultiInfo Comment'] = 'The color of a multi-line Extra Information Comment either for a script or block.'
		self.info['Comment'] = 'The color of a regular comment.'
		self.info['AI ID'] = 'The color of the AI ID in the AI header.'
		self.info['Header String'] = 'The color of the String index in the AI header.'
		self.info['Header Flags'] = 'The color of the Flags in the AI header'
		self.info['Operators'] = 'The color of the operators:\n    ( ) , = :'
		self.info['Error'] = 'The color of an error when compiling.'
		self.info['Warning'] = 'The color of a warning when compiling.'
		self.info['Selection'] = 'The color of selected text in the editor.'
		PyMSDialog.__init__(self, parent, 'Color Settings')

	def widgetize(self):
		self.resizable(False, False)
		self.listbox = Listbox(self, font=couriernew, width=20, height=16, exportselection=0, activestyle=DOTBOX)
		self.listbox.bind('<ButtonRelease-1>', self.select)
		for t in self.info.keys():
			self.listbox.insert(END, t)
		self.listbox.select_set(0)
		self.listbox.pack(side=LEFT, fill=Y, padx=2, pady=2)

		self.fg = IntVar()
		self.bg = IntVar()
		self.bold = IntVar()
		self.infotext = StringVar()

		r = Frame(self)
		opt = LabelFrame(r, text='Style:', padx=5, pady=5)
		f = Frame(opt)
		c = Checkbutton(f, text='Foreground', variable=self.fg, width=20, anchor=W)
		c.bind('<ButtonRelease-1>', lambda e,i=0: self.select(e,i))
		c.grid(sticky=W)
		c = Checkbutton(f, text='Background', variable=self.bg)
		c.bind('<ButtonRelease-1>', lambda e,i=1: self.select(e,i))
		c.grid(sticky=W)
		c = Checkbutton(f, text='Bold', variable=self.bold)
		c.bind('<ButtonRelease-1>', lambda e,i=2: self.select(e,i))
		c.grid(sticky=W)
		self.fgcanvas = Canvas(f, width=32, height=32, background='#000000')
		self.fgcanvas.bind('<Button-1>', lambda e,i=0: self.colorselect(e, i))
		self.fgcanvas.grid(column=1, row=0)
		self.bgcanvas = Canvas(f, width=32, height=32, background='#000000')
		self.bgcanvas.bind('<Button-1>', lambda e,i=1: self.colorselect(e, i))
		self.bgcanvas.grid(column=1, row=1)
		f.pack(side=TOP)
		Label(opt, textvariable=self.infotext, height=6, justify=LEFT).pack(side=BOTTOM, fill=X)
		opt.pack(side=TOP, fill=Y, expand=1, padx=2, pady=2)
		f = Frame(r)
		ok = Button(f, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3)
		Button(f, text='Cancel', width=10, command=self.cancel).pack(side=LEFT)
		f.pack(side=BOTTOM, pady=2)
		r.pack(side=LEFT, fill=Y)

		self.select()

		return ok

	def select(self, e=None, n=None):
		i = self.info.getkey(int(self.listbox.curselection()[0]))
		s = self.tags[i.replace(' ', '')]
		if n == None:
			t = self.info[i].split('\n')
			text = ''
			if len(t) == 2:
				d = '  '
				text = t[0] + '\n'
			else:
				d = ''
			text += fit(d, t[-1], 35, True)[:-1]
			self.infotext.set(text)
			if s['foreground'] == None:
				self.fg.set(0)
				self.fgcanvas['background'] = '#000000'
			else:
				self.fg.set(1)
				self.fgcanvas['background'] = s['foreground']
			if s['background'] == None:
				self.bg.set(0)
				self.bgcanvas['background'] = '#000000'
			else:
				self.bg.set(1)
				self.bgcanvas['background'] = s['background']
			self.bold.set(s['font'] != None)
		else:
			v = [self.fg,self.bg,self.bold][n].get()
			if n == 2:
				s['font'] = [self.parent.text.boldfont,couriernew][v]
			else:
				s[['foreground','background'][n]] = ['#000000',None][v]
				if v:
					[self.fgcanvas,self.bgcanvas][n]['background'] = '#000000'

	def colorselect(self, e, i):
		if [self.fg,self.bg][i].get():
			v = [self.fgcanvas,self.bgcanvas][i]
			g = ['foreground','background'][i]
			c = tkColorChooser.askcolor(parent=self, initialcolor=v['background'], title='Select %s color)' % g)
			if c[1]:
				v['background'] = c[1]
				self.tags[self.info.getkey(int(self.listbox.curselection()[0])).replace(' ','')][g] = c[1]
			self.focus_set()

	def ok(self):
		self.cont = self.tags
		PyMSDialog.ok(self)

	def cancel(self):
		self.cont = False
		PyMSDialog.ok(self)

class AICodeText(CodeText):
	def __init__(self, parent, ai, ecallback=None, icallback=None, scallback=None, highlights=None):
		self.ai = ai
		self.boldfont = ('Courier New', -11, 'bold')
		if highlights:
			self.highlights = highlights
		else:
			self.highlights = {
				'Block':{'foreground':'#FF00FF','background':None,'font':None},
				'Keywords':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'Types':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'Commands':{'foreground':'#0000AA','background':None,'font':None},
				'Number':{'foreground':'#FF0000','background':None,'font':None},
				'TBLFormat':{'foreground':None,'background':'#E6E6E6','font':None},
				'InfoComment':{'foreground':'#FF963C','background':None,'font':None},
				'MultiInfoComment':{'foreground':'#FF963C','background':None,'font':None},
				'Comment':{'foreground':'#008000','background':None,'font':None},
				'AIID':{'foreground':'#FF00FF','background':None,'font':self.boldfont},
				'HeaderString':{'foreground':'#FF0000','background':None,'font':self.boldfont},
				'HeaderFlags':{'foreground':'#8000FF','background':None,'font':self.boldfont},
				'Operators':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'Newline':{'foreground':None,'background':None,'font':None},
				'Error':{'foreground':None,'background':'#FF8C8C','font':None},
				'Warning':{'foreground':None,'background':'#FFC8C8','font':None},
			}
		CodeText.__init__(self, parent, ecallback, icallback, scallback)
		self.text.bind('<Control-q>', self.commentrange)

	def setedit(self):
		if self.ecallback != None:
			self.ecallback()
		self.edited = True

	def commentrange(self, e=None):
		item = self.tag_ranges('Selection')
		if item:
			head,tail = self.index('%s linestart)' % item[0]),self.index('%s linestart)' % item[1])
			while self.text.compare(head, '<=', tail):
				m = re.match(r'(\s*)(#?)(.*)', self.get(head, '%s lineend)' % head))
				if m.group(2):
					self.tk.call(self.text.orig, 'delete', '%s +%sc)' % (head, len(m.group(1))))
				elif m.group(3):
					self.tk.call(self.text.orig, 'insert', head, '#')
				head = self.index('%s +1line)' % head)
			self.update_range(self.index('%s linestart)' % item[0]), self.index('%s lineend)' % item[1]))

	def setupparser(self):
		infocomment = r'(?P<InfoComment>\{[^\n]+\})'
		multiinfocomment = r'^[ \t]*(?P<MultiInfoComment>\{[ \t]*(?:\n[^}]*)?\}?)$'
		comment = r'(?P<Comment>#[^\n]*$)'
		header = r'^(?P<AIID>[^\n\x00,():]{4})(?=\([^#]+,[^#]+,[^#]+\):.+$)'
		header_string = r'\b(?P<HeaderString>\d+)(?=,[^#]+,[^#]+\):.+$)'
		header_flags = r'\b(?P<HeaderFlags>[01]{3})(?=,[^#]+\):.+$)'
		block = r'^[ \t]*(?P<Block>--[^\x00:(),\n]+--)(?=.+$)'
		cmds = r'\b(?P<Commands>%s)\b)' % '|'.join(AIBIN.AIBIN.short_labels)
		num = r'\b(?P<Number>\d+)\b'
		tbl = r'(?P<TBLFormat><0*(?:25[0-5]|2[0-4]\d|1?\d?\d)?>)'
		operators = r'(?P<Operators>[():,=])'
		kw = r'\b(?P<Keywords>extdef|aiscript|bwscript)\b'
		types = r'\b(?P<Types>%s)\b)' % '|'.join(AIBIN.types)
		self.basic = re.compile('|'.join((infocomment, multiinfocomment, comment, header, header_string, header_flags, block, cmds, num, tbl, operators, kw, types, r'(?P<Newline>\n)')), re.S | re.M)
		self.tooptips = [CommandCodeTooltip(self.text,self.ai),TypeCodeTooltip(self.text,self.ai),StringCodeTooltip(self.text,self.ai),FlagCodeTooltip(self.text,self.ai)]
		self.tags = dict(self.highlights)

	def colorize(self):
		next = '1.0'
		while True:
			item = self.tag_nextrange("Update", next)
			if not item:
				break
			head, tail = item
			self.tag_remove('Newline', head, tail)
			item = self.tag_prevrange('Newline', head)
			if item:
				head = item[1] + ' linestart'
			else:
				head = "1.0"
			chars = ""
			next = head
			lines_to_get = 1
			ok = False
			while not ok:
				mark = next
				next = self.index(mark + '+%d lines linestart)' % lines_to_get)
				lines_to_get = min(lines_to_get * 2, 100)
				ok = 'Newline' in self.tag_names(next + '-1c')
				line = self.get(mark, next)
				if not line:
					return
				for tag in self.tags.keys():
					if tag != 'Selection':
						self.tag_remove(tag, mark, next)
				chars = chars + line
				m = self.basic.search(chars)
				while m:
					for key, value in m.groupdict().items():
						if value != None:
							a, b = m.span(key)
							self.tag_add(key, head + '+%dc)' % a, head + '+%dc)' % b)
					m = self.basic.search(chars, m.end())
				if 'Newline' in self.tag_names(next + '-1c'):
					head = next
					chars = ''
				else:
					ok = False
				if not ok:
					self.tag_add('Update', next)
				self.update()
				if not self.coloring:
					return

class CodeTooltip(Tooltip):
	tag = ''

	def __init__(self, widget, ai):
		self.ai = ai
		Tooltip.__init__(self, widget)

	def setupbinds(self, press):
		if self.tag:
			self.widget.tag_bind(self.tag, '<Enter>', self.enter, '+')
			self.widget.tag_bind(self.tag, '<Leave>', self.leave, '+')
			self.widget.tag_bind(self.tag, '<Motion>', self.motion, '+')
			self.widget.tag_bind(self.tag, '<Button-1>', self.leave, '+')
			self.widget.tag_bind(self.tag, '<ButtonPress>', self.leave)

	def showtip(self):
		if self.tip:
			return
		t = ''
		if self.tag:
			pos = list(self.widget.winfo_pointerxy())
			head,tail = self.widget.tag_prevrange(self.tag,self.widget.index('@%s,%s+1c)' % (pos[0] - self.widget.winfo_rootx(),pos[1] - self.widget.winfo_rooty())))
			t = self.widget.get(head,tail)
		try:
			t = self.gettext(t)
			self.tip = Toplevel(self.widget, relief=SOLID, borderwidth=1)
			self.tip.wm_overrideredirect(1)
			frame = Frame(self.tip, background='#FFFFC8', borderwidth=0)
			Label(frame, text=t, justify=LEFT, font=self.font, background='#FFFFC8', relief=FLAT).pack(padx=1, pady=1)
			frame.pack()
			pos = list(self.widget.winfo_pointerxy())
			self.tip.wm_geometry('+%d+%d)' % (pos[0],pos[1]+22))
			self.tip.update_idletasks()
			move = False
			if pos[0] + self.tip.winfo_reqwidth() > self.tip.winfo_screenwidth():
				move = True
				pos[0] = self.tip.winfo_screenwidth() - self.tip.winfo_reqwidth()
			if pos[1] + self.tip.winfo_reqheight() + 22 > self.tip.winfo_screenheight():
				move = True
				pos[1] -= self.tip.winfo_reqheight() + 44
			if move:
				self.tip.wm_geometry('+%d+%d)' % (pos[0],pos[1]+22))
		except:
			if self.tip:
				try:
					self.tip.destroy()
				except:
					pass
				self.tip = None
			return

	def gettext(self, t):
		# Overload to specify tooltip text
		return ''

class CommandCodeTooltip(CodeTooltip):
	tag = 'Commands'

	def gettext(self, cmd):
		for help,info in CMD_HELP.items():
			if cmd in info:
				text = '%s Command:\n  %s()' % (help, cmd)
				break
		params = self.ai.parameters[self.ai.short_labels.index(cmd)]
		pinfo = ''
		if params:
			pinfo = '\n\n'
			done = []
			for p in params:
				t = p.__doc__.split(' ',1)[0]
				text += t + ', '
				if not t in done:
					pinfo += fit('  %s: )' % t, TYPE_HELP[t], end=True, indent=4)
					done.append(t)
			text = text[:-2]
		text += ')'
		return text + '\n' + fit('    ', info[cmd], end=True)[:-1] + pinfo[:-1]

class TypeCodeTooltip(CodeTooltip):
	tag = 'Types'

	def gettext(self, type):
		return '%s:\n%s)' % (type, fit('    ', TYPE_HELP[type], end=True)[:-1])

class StringCodeTooltip(CodeTooltip):
	tag = 'HeaderString'

	def gettext(self, stringid):
		stringid = int(stringid)
		m = len(self.ai.tbl.strings)
		if stringid > m:
			text = 'Invalid String ID (Range is 0 to %s))' % (m-1)
		else:
			text = 'String %s:\n  %s)' % (stringid, TBL.decompile_string(self.ai.tbl.strings[stringid]))
		return text

class FlagCodeTooltip(CodeTooltip):
	tag = 'HeaderFlags'

	def gettext(self, flags):
		text = 'AI Script Flags:\n  %s:\n    )' % flags
		if flags == '000':
			text += 'None'
		else:
			text += '\n    '.join([d for d,f in zip(['BroodWar Only','Invisible in StarEdit','Requires a Location'], flags) if f == '1'])
		return text

class CodeEditDialog(PyMSDialog):
	def __init__(self, parent, ids):
		self.ids = ids
		self.decompile = ''
		self.file = None
		self.autocomptext = TYPE_HELP.keys()
		self.completing = False
		self.complete = [None, 0]
		t = ''
		if ids:
			t = ', '.join(ids[:5])
			if len(ids) > 5:
				t += '...'
			t += ' - '
		t += 'AI Script Editor'
		PyMSDialog.__init__(self, parent, t, grabwait=False)
		self.findwindow = None

	def widgetize(self):
		self.extrainfo = IntVar()
		self.extrainfo.set(self.parent.settings.get('codeeditextrainfo', 1))
		buttons = [
			('save', self.save, 'Save (Ctrl+S)', '<Control-s>'),
			('test', self.test, 'Test Code (Ctrl+T)', '<Control-t>'),
			4,
			('export', self.export, 'Export Code (Ctrl+E)', '<Control-e>'),
			('saveas', self.exportas, 'Export As... (Ctrl+Alt+A)', '<Control-Alt-a>'),
			('import', self.iimport, 'Import Code (Ctrl+I)', '<Control-i>'),
			4,
			('saveextra', self.extrainfo, 'Save Information Comments and Labels', True),
			10,
			('find', self.find, 'Find/Replace (Ctrl+F)', '<Control-f>'),
			10,
			('colors', self.colors, 'Color Settings (Ctrl+Alt+C)', '<Control-Alt-c>'),
			10,
			('asc3topyai', self.asc3topyai, 'Compile ASC3 to PyAI (Ctrl+Alt+P)', '<Control-Alt-p>'),
			('debug', self.debuggerize, 'Debuggerize your code (Ctrl+D)', '<Control-D>'),
		]
		self.bind('<Alt-Left>', lambda e,i=0: self.gotosection(e,i))
		self.bind('<Alt-Right>', lambda e,i=1: self.gotosection(e,i))
		self.bind('<Alt-Up>', lambda e,i=2: self.gotosection(e,i))
		self.bind('<Alt-Down>', lambda e,i=3: self.gotosection(e,i))
		bar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = get_img(btn[0])
				if btn[3] == True:
					button = Checkbutton(bar, image=image, width=20, height=20, indicatoron=0, variable=btn[1])
				else:
					button = Button(bar, image=image, width=20, height=20, command=btn[1])
					self.bind(btn[3], btn[1])
				button.image = image
				button.tooltip = Tooltip(button, btn[2], couriernew)
				button.pack(side=LEFT)
				if button.winfo_reqwidth() > 26:
					button['width'] = 18
				if button.winfo_reqheight() > 26:
					button['height'] = 18
			else:
				Frame(bar, width=btn).pack(side=LEFT)
		bar.pack(fill=X, padx=2, pady=2)

		self.text = AICodeText(self, self.parent.ai, self.edited, highlights=self.parent.highlights)
		self.text.pack(fill=BOTH, expand=1, padx=1, pady=1)
		self.text.icallback = self.statusupdate
		self.text.scallback = self.statusupdate
		self.text.acallback = self.autocomplete

		self.status = StringVar()
		if self.ids:
			self.status.set("Original ID's: " + ', '.join(self.ids))
		self.scriptstatus = StringVar()
		self.scriptstatus.set('Line: 1  Column: 0  Selected: 0')

		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		image = get_img('save')
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, textvariable=self.scriptstatus, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		statusbar.pack(side=BOTTOM, fill=X)

		if self.ids:
			self.after(1, self.load)

		if 'codeeditwindow' in self.parent.settings:
			loadsize(self, self.parent.settings, 'codeeditwindow', True)

		return self.text

	def gotosection(self, e, i):
		c = [self.text.tag_prevrange, self.text.tag_nextrange][i % 2]
		t = [('Error','Warning'),('AIID','Block')][i > 1]
		a = c(t[0], INSERT)
		b = c(t[1], INSERT)
		s = None
		if a:
			if not b or self.text.compare(a[0], ['>','<'][i % 2], b[0]):
				s = a
			else:
				s = b
		elif b:
			s = b
		if s:
			self.text.see(s[0])
			self.text.mark_set(INSERT, s[0])

	def autocomplete(self):
		i = self.text.tag_ranges('Selection')
		if i and '\n' in self.text.get(*i):
			return False
		self.completing = True
		self.text.taboverride = ' (,)'
		def docomplete(s, e, v, t):
			self.text.delete(s, e)
			self.text.insert(s, v)
			ss = '%s+%sc)' % (s,len(t))
			se = '%s+%sc)' % (s,len(v))
			self.text.tag_remove('Selection', '1.0', END)
			self.text.tag_add('Selection', ss, se)
			if self.complete[0] == None:
				self.complete = [t, 1, s, se]
			else:
				self.complete[1] += 1
				self.complete[3] = se
		if self.complete[0] != None:
			t,f,s,e = self.complete
		else:
			s,e = self.text.index('%s -1c wordstart)' % INSERT),self.text.index('%s -1c wordend)' % INSERT)
			t,f = self.text.get(s,e),0
		if t and t[0].lower() in 'abcdefghijklmnopqrstuvwxyz':
			ac = list(self.autocomptext)
			m = re.match('\\A\\s*[a-z\\{]+\\Z',t)
			if not m:
				for _,c in CMD_HELP.items():
					ac.extend(c.keys())
			for ns in self.parent.tbl.strings[:228]:
				cs = ns.split('\x00')
				if cs[1] != '*':
					cs = TBL.decompile_string('\x00'.join(cs[:2]), '\x0A\x28\x29\x2C')
				else:
					cs = TBL.decompile_string(cs[0], '\x0A\x28\x29\x2C')
				if not cs in ac:
					ac.append(cs)
			for i in range(61):
				cs = TBL.decompile_string(self.parent.tbl.strings[self.parent.upgrades.get_value(i,'Label') - 1].split('\x00',1)[0].strip(), '\x0A\x28\x29\x2C')
				if not cs in ac:
					ac.append(cs)
			for i in range(44):
				cs = TBL.decompile_string(self.parent.tbl.strings[self.parent.tech.get_value(i,'Label') - 1].split('\x00',1)[0].strip(), '\x0A\x28\x29\x2C')
				if not cs in ac:
					ac.append(cs)
			aiid = ''
			item = self.text.tag_prevrange('AIID', INSERT)
			if item:
				aiid = self.text.get(*item)
			head = '1.0'
			while True:
				item = self.text.tag_nextrange('Block', head)
				if not item:
					break
				head,tail = item
				block = ''
				if aiid:
					item = self.text.tag_prevrange('AIID', head)
					if item:
						id = self.text.get(*item)
						if id != aiid:
							block = id + ':'
				block += self.text.get('%s +2c)' % head,'%s -2c)' % tail)
				if not block in ac:
					ac.append(block)
				head = tail
			ac.sort()
			if not m:
				x = []
				for _,c in CMD_HELP.items():
					x.extend(c.keys())
				x.sort()
				ac = x + ac
			r = False
			matches = []
			for v in ac:
				if v and v.lower().startswith(t.lower()):
					matches.append(v)
			if matches:
				if f < len(matches):
					docomplete(s,e,matches[f],t)
					self.text.taboverride = ' (,)'
				elif self.complete[0] != None:
					docomplete(s,e,t,t)
					self.complete[1] = 0
				r = True
			self.after(1, self.completed)
			return r

	def completed(self):
		self.completing = False

	def statusupdate(self):
		if not self.completing:
			self.text.taboverride = False
			self.complete = [None, 0]
		i = self.text.index(INSERT).split('.') + [0]
		item = self.text.tag_ranges('Selection')
		if item:
			i[2] = len(self.text.get(*item))
		self.scriptstatus.set('Line: %s  Column: %s  Selected: %s)' % tuple(i))

	def edited(self):
		if not self.completing:
			self.text.taboverride = False
			self.complete = [None, 0]
		self.editstatus['state'] = NORMAL
		if self.file:
			self.title('AI Script Editor [*%s*])' % self.file)

	def cancel(self):
		if self.text.edited:
			save = askquestion(parent=self, title='Save Code?', message="Would you like to save the code?", default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return
				self.save()
		self.ok()

	def save(self, e=None):
		if self.parent.iimport(iimport=self, parent=self, extra=self.extrainfo.get()):
			self.text.edited = False
			self.editstatus['state'] = DISABLED

	def ok(self):
		savesize(self, self.parent.settings, 'codeeditwindow')
		self.parent.settings['codeeditextrainfo'] = self.extrainfo.get()
		PyMSDialog.ok(self)

	def test(self, e=None):
		i = AIBIN.AIBIN(False, self.parent.unitsdat, self.parent.upgradesdat, self.parent.techdat, self.parent.tbl)
		i.bwscript = AIBIN.BWBIN(self.parent.unitsdat, self.parent.upgradesdat, self.parent.techdat, self.parent.tbl)
		try:
			warnings = i.interpret(self, self.parent.extdefs)
			for id in i.ais.keys():
				if id in self.parent.ai.externaljumps[0]:
					for o,l in self.parent.ai.externaljumps[0].items():
						for cid in l:
							if not cid in i.ais:
								raise PyMSError('Interpreting',"You can't edit scripts (%s) that are referenced externally with out editing the scripts with the external references (%s) at the same time.)" % (id,cid))
		except PyMSError as e:
			if e.line != None:
				self.text.see('%s.0)' % e.line)
				self.text.tag_add('Error', '%s.0)' % e.line, '%s.end)' % e.line)
			if e.warnings:
				for w in e.warnings:
					if w.line != None:
						self.text.tag_add('Warning', '%s.0)' % w.line, '%s.end)' % w.line)
			ErrorDialog(self, e)
			return
		if warnings:
			c = False
			for w in warnings:
				if w.line != None:
					if not c:
						self.text.see('%s.0)' % w.line)
						c = True
					self.text.tag_add('Warning', '%s.0)' % w.line, '%s.end)' % w.line)
			WarningDialog(self, warnings, True)
		else:
			askquestion(parent=self, title='Test Completed', message='The code compiles with no errors or warnings.', type=OK)

	def export(self, e=None):
		if not self.file:
			self.exportas()
		else:
			f = open(self.file, 'w')
			f.write(self.text.get('1.0', END))
			f.close()
			self.title('AI Script Editor [%s])' % self.file)

	def exportas(self, e=None):
		file = self.parent.select_file('Export Code', False, '.txt', [('Text Files','*.txt'),('All Files','*')], self)
		if not file:
			return
		self.file = file
		self.export()

	def iimport(self, e=None):
		iimport = self.parent.select_file('Import From', True, '.txt', [('Text Files','*.txt'),('All Files','*')], self)
		if iimport:
			try:
				f = open(iimport, 'r')
				self.text.delete('1.0', END)
				self.text.insert('1.0', f.read())
				f.close()
			except:
				ErrorDialog(self, PyMSError('Import',"Could not import file '%s')" % iimport))

	def find(self, e=None):
		if not self.findwindow:
			self.findwindow = FindReplaceDialog(self)
			self.bind('<F3>', self.findwindow.findnext)
		elif self.findwindow.state() == 'withdrawn':
			self.findwindow.deiconify()
		self.findwindow.focus_set()

	def colors(self, e=None):
		c = CodeColors(self)
		if c.cont:
			self.text.setup(c.cont)
			self.parent.highlights = c.cont

	def asc3topyai(self, e=None):
		beforeheader = ''
		header = '### NOTE: There is no way to determine the scripts flags or if it is a BW script or not!\n###       please update the header below appropriately!\n%s(%s, 111, %s): # Script Name: %s'
		headerinfo = [None,None,None,None]
		data = ''
		for line in self.text.text.get('1.0',END).split('\n'):
			if line.lstrip().startswith(';'):
				if not None in headerinfo:
					data += line.replace(';','#',1) + '\n'
				else:
					beforeheader += line.replace(';','#',1) + '\n'
			elif line.lstrip().startswith(':'):
				data += '        --%s--\n)' % line.split('#',1)[0].strip()[1:]
			elif line.lstrip().startswith('script_name ') and headerinfo[3] == None:
				headerinfo[3] = line.lstrip()[12:]
				if re.match('bw|brood ?war',headerinfo[3],re.I):
					headerinfo[2] = 'bwscript'
				else:
					headerinfo[2] = 'aiscript'
				for n,string in enumerate(self.parent.tbl.strings):
					if headerinfo[3] + '\x00' == string:
						headerinfo[1] = n
						break
				else:
					headerinfo[1] = 0
			elif line.lstrip().startswith('script_id ') and headerinfo[0] == None:
				headerinfo[0] = line.lstrip()[10:]
			elif line.strip():
				d = line.lstrip().split(';',1)[0].strip().split(' ')
				if d[0] in AIBIN.AIBIN.short_labels:
					data += '    %s(%s))' % (d[0], ', '.join(d[1:]))
					if ';' in line:
						data += ' # ' + line.split('#',1)[1]
				else:
					if not None in headerinfo:
						data += '# ' + line
					else:
						beforeheader += '# ' + line + '\n'
				data += '\n'
			else:
				data += '\n'
		if None in headerinfo:
			askquestion(parent=self, title='Invalid Header', message='The script is either missing a script_name or a script_id.', type=OK)
			return
		self.text.delete('1.0', END)
		self.text.insert(END, beforeheader + '\n' + header % tuple(headerinfo) + data)
		self.text.edited = True
		self.editstatus['state'] = NORMAL

	def debuggerize(self):
		d = 0
		data = ''
		debug = {
			'goto':('debug(%(param1)s, Goto block "%(param1)s". %(s)s)%(c)s',0),
			'notowns_jump':('notowns_jump(%(param1)s,%(debug1)s)%(c)s\ndebug(%(debug2)s, I do not own the unit "%(param1)s"<44> continuing the current block... %(s)s)\n	--%(debug1)s--\ndebug(%(param2)s, I own the unit "%(param1)s"<44> going to block "%(param2)s". %(s)s)\n	--%(debug2)s--',2),
			'expand':('debug(%(debug1)s, Running block "%(param2)s" for expansion number "%(param1)s". %(s)s)\n	--%(debug1)s--\nexpand(%(param1)s, %(param2)s)%(c)s',1),
			'debug':('debug(%(param1)s, %(param2)s [%(param1)s]%(s)s)%(c)s',0),
			'random_jump':('random_jump(%(param1)s, %(debug1)s)%(c)s\ndebug(%(debug2)s, I randomly chose to continue this block instead of going to block "%(param2)s". %(s)s)\n	--%(debug1)s--\ndebug(%(param2)s, I randomly chose to go to block "%(param2)s". %(s)s)\n	--%(debug2)s--',2),
			'time_jump':('time_jump(%(param1)s, %(debug1)s)%(c)s\ndebug(%(debug2)s, "%(param1)s" minutes have not passed in game<44> continuing the current block. %(s)s)\n	--%(debug1)s--\ndebug(%(param2)s, "%(param1)s" minutes have passed in game<44> going to block "%(param2)s". %(s)s)\n	--%(debug2)s--',2),
			'race_jump':('race_jump(%(debug1)s, %(debug2)s, %(debug3)s)%(c)s\n	--%(debug1)s--\ndebug(%(param1)s, My current enemy is Terran<44> going to block "%(param1)s". %(s)s)\n	--%(debug2)s--\ndebug(%(param2)s, My current enemy is Zerg<44> going to block "%(param2)s". %(s)s)\n	--%(debug3)s--\ndebug(%(param3)s, My current enemy is Protoss<44> going to block "%(param3)s". %(s)s)',3),
			#'region_size':('',),
			'groundmap_jump':('groundmap_jump(%(debug1)s)%(c)s\ndebug(%(debug2)s, The map is not a ground map<44> continuing the current block. %(s)s)\n	--%(debug1)s--\ndebug(%(param1)s, The map is a ground map<44> going to "%(param1)s". %(s)s)\n	--%(debug2)s--',2),
			'call':('debug(%(debug1)s, Calling block "%(param1)s". %(s)s)\n	--%(debug1)s--\ncall(%(param1)s)%(c)s\ndebug(%(debug2)s, Returned from a call to block "%(param1)s". %(s)s)\n	--%(debug2)s--',2),
			#'panic':('',),
			'multirun':('debug(%(debug1)s, Running block "%(param1)s" in another thread. %(s)s)\n	--%(debug1)s--\nmultirun(%(param1)s)%(c)s',1),
			#'rush':('',),
			'resources_jump':('resources_jump(%(param1)s, %(param2)s, %(debug1)s)%(c)s\ndebug(%(debug2)s, I do not have at least "%(param1)s" minerals and "%(param2)s" vespene<44> continuing the current block. %(s)s)\n	--%(debug1)s--\ndebug(%(param3)s, I have at least "%(param1)s" minerals and "%(param2)s" vespene<44> going to "%(param3)s". %(s)s)\n	--%(debug2)s--',2),
			'enemyowns_jump':('enemyowns_jump(%(param1)s, %(debug1)s)%(c)s\ndebug(%(debug2)s, My current enemy doesn\'t own the unit "%(param1)s"<44> continuing the current block. %(s)s)\n	--%(debug1)s--\ndebug(%(param2)s, My current enemy owns the unit "%(param1)s"<44> going to "%(param2)s". %(s)s)\n	--%(debug2)s--',2),
			'enemyresources_jump':('enemyresources_jump(%(param1)s, %(param2)s, %(debug1)s)%(c)s\ndebug(%(debug2)s, My current enemy doesn\'t have at least "%(param1)s" minerals and "%(param2)s" vespene<44> continuing the current block. %(s)s)\n	--%(debug1)s--\ndebug(%(param3)s, My current enemy has at least "%(param1)s" minerals and "%(param2)s" vespene<44> going to "%(param3)s". %(s)s)\n	--%(debug2)s--',2),
			'stop':('debug(%(debug1)s, Stopping the current block. %(s)s)\n	--%(debug1)s--\nstop()%(c)s',1),
			#'if_owned':('',),
			#'allies_watch':('',),
			#'try_townpoint':('',),
		}
		header = re.compile(r'\A([^(]{4})\([^)]+\):\s*(?:\{.+\})?(?:\s*#.*)?\Z')
		label = re.compile(r'\A\s*--\s*(.+)\s*--(?:\s*\{(.+)\})?(?:\s*#.*)?\Z')
		jump = re.compile(r'\A(\s*)(%s)\((.+)\)(\s*#.*)?\Z)' % '|'.join(debug.keys()))
		script,block = '',''
		for n,line in enumerate(self.text.text.get('1.0',END).split('\n')):
			m = header.match(line)
			if m:
				script = m.group(1)
				block = ''
				data += line + '\n'
				continue
			m = label.match(line)
			if m:
				block = m.group(1)
				data += line + '\n'
				continue
			m = jump.match(line)
			if m and m.group(2) in debug:
				inblock = ''
				if block:
					inblock = ' block "%s")' % block
				rep = {
					'debug1':'== Debug %s ==)' % d,
					'debug2':'== Debug %s ==)' % (d+1),
					'debug3':'== Debug %s ==)' % (d+2),
					's':'[Line: %s | Inside script "%s"%s])' % (n, script, inblock),
					'c':m.group(4) or '',
				}
				params = self.parent.ai.parameters[self.parent.ai.short_labels.index(m.group(2))]
				if params:
					p = re.match('\\A%s\\Z)' % ','.join(['\\s*(.+)\\s*'] * len(params)), m.group(3))
					if not p:
						data += line + '\n'
						continue
					for g,param in enumerate(p.groups()):
						rep['param%s)' % (g+1)] = param
				data += m.group(1) + (debug[m.group(2)][0] % rep).replace('\n','\n' + m.group(1)) + '\n'
				d += debug[m.group(2)][1]
				continue
			data += line + '\n'
		self.text.delete('1.0', END)
		self.text.insert(END, data)
		self.text.edited = True
		self.editstatus['state'] = NORMAL

	def load(self):
		try:
			warnings = self.parent.ai.decompile(self, self.parent.extdefs, self.parent.reference.get(), 1, self.ids)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		if warnings:
			WarningDialog(self, warnings)

	def write(self, text):
		self.decompile += text

	def readlines(self):
		return self.text.get('1.0', END).split('\n')

	def close(self):
		if self.decompile:
			self.text.insert('1.0', self.decompile.strip())
			self.decompile = ''
			self.text.text.mark_set(INSERT, '1.0')
			self.text.text.see(INSERT)
			self.text.edited = False
			self.editstatus['state'] = DISABLED

	def destroy(self):
		if self.findwindow:
			Toplevel.destroy(self.findwindow)
		Toplevel.destroy(self)
#
class FindDialog(PyMSDialog):
	def __init__(self, parent, findstr=False):
		self.findstr = findstr
		self.results = False
		self.id = StringVar()
		self.bw = IntVar()
		self.flags = StringVar()
		self.stringid = StringVar()
		self.string = StringVar()
		self.extra = StringVar()
		self.casesens = IntVar()
		self.regex = IntVar()

		self.reset = None

		self.ai = parent.ai
		self.tbl = parent.tbl
		self.settings = parent.settings
		self.edittbl = parent.edittbl
		self.stattxt = parent.stattxt
		self.strings = parent.strings
		self.resort = parent.resort
		self.select_file = parent.select_file
		PyMSDialog.__init__(self, parent, ['Find a Script','Find a String'][findstr])

	def widgetize(self):
		self.bind('<Control-a>', self.selectall)

		if self.findstr:
			self.minsize(300,150)
			data = [
				('String ID', self.stringid, 'stringidentry', True),
				('String', self.string, 'stringentry'),
			]
		else:
			self.minsize(300,325)
			data = [
				('AI ID', self.id, 'identry'),
				[
					('aiscript.bin', 1),
					('bwscript.bin', 2),
					('Either', 0),
				],
				('Flags', self.flags, 'flagsentry'),
				('String ID', self.stringid, 'stringidentry', True),
				('String', self.string, 'stringentry'),
				('Extra Info', self.extra, None, False),
			]
		focuson = None
		for d in data:
			if isinstance(d, list):
				frame = Frame(self)
				for rb in d:
					Radiobutton(frame, text=rb[0], variable=self.bw, value=rb[1]).pack(side=LEFT)
				frame.pack(fill=X)
			else:
				Label(self, text=d[0], anchor=W).pack(fill=X)
				if len(d) == 4:
					if d[3]:
						frame = Frame(self)
						entry = Entry(frame, textvariable=d[1])
						setattr(self, d[2], entry)
						entry.pack(side=LEFT, fill=X, expand=1)
						Button(frame, text='Browse...', width=10, command=self.browse).pack(side=RIGHT)
						frame.pack(fill=X)
						if not focuson:
							focuson = entry
					else:
						frame = Frame(self)
						vscroll = Scrollbar(frame)
						self.extraentry = Text(frame, yscrollcommand=vscroll.set, width=1, height=3, wrap=WORD)
						self.extraentry.pack(side=LEFT, fill=X, expand=1)
						vscroll.config(command=self.extraentry.yview)
						vscroll.pack(side=RIGHT, fill=Y)
						frame.pack(fill=X)
				else:
					entry = Entry(self, textvariable=d[1])
					setattr(self, d[2], entry)
					entry.pack(fill=X)
					if not focuson:
						focuson = entry

		options = Frame(self)
		Checkbutton(options, text='Case Sensitive', variable=self.casesens).pack(side=LEFT, padx=3)
		Checkbutton(options, text='Regular Expressions', variable=self.regex).pack(side=LEFT, padx=3)
		options.pack(pady=3)

		listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, selectmode=[EXTENDED,BROWSE][self.findstr], activestyle=DOTBOX, font=couriernew, width=1, height=1, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.bind('<ButtonRelease-1>', self.update)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(fill=BOTH, padx=2, pady=2, expand=1)

		buttons = Frame(self)
		Button(buttons, text='Find', width=10, command=self.find, default=NORMAL).pack(side=LEFT, padx=3, pady=3)
		self.select = Button(buttons, text='Select', width=10, command=self.select, state=DISABLED)
		self.select.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		buttons.pack()

		self.bind('<Return>', self.find)

		if ['findscriptwindow','findstringwindow'][self.findstr] in self.parent.settings:
			loadsize(self, self.parent.settings, ['findscriptwindow','findstringwindow'][self.findstr], True)

		return focuson

	def update(self, e=None):
		self.select['state'] = NORMAL

	def updatecolor(self):
		if self.reset:
			if self.resettimer:
				self.after_cancel(self.resettimer)
				self.resettimer = None
			self.reset['bg'] = self.reset.c
			self.reset = None

	def selectall(self, e=None):
		if self.listbox.size():
			self.listbox.select_set(0, END)
			self.select['state'] = NORMAL

	def browse(self):
		try:
			s = int(self.stringid.get())
		except:
			s = 0
		s = StringEditor(self, 'Select a String', True, s)
		if s.result != None:
			self.stringid.set(s.result)

	def find(self):
		self.updatecolor()
		self.listbox.delete(0,END)
		self.select['state'] = DISABLED
		if self.findstr:
			m = []
			for t,e in [(self.stringid, self.stringidentry), (self.string, self.stringentry)]:
				if self.regex.get():
					regex = t.get()
					if not regex.startswith('\\A'):
						regex = '.*' + regex
					if not regex.endswith('\\Z'):
						regex = regex + '.*'
				else:
					regex = '.*%s.*)' % re.escape(t.get())
				try:
					m.append(re.compile(regex, [re.I,0][self.casesens.get()]))
				except:
					e.c = e['bg']
					e['bg'] = '#FFB4B4'
					self.reset = e
					self.resettimer = self.after(1000, self.updatecolor)
					return
			pad = len(str(len(self.tbl.strings)))
			for n,s in enumerate(self.tbl.strings):
				l = TBL.decompile_string(s)
				if m[0].match(str(n)) and m[1].match(l):
					self.listbox.insert(END, '%s%s     %s)' % (' ' * (pad - len(str(n))), n, l))
		else:
			m = []
			for t,e in [(self.id, self.identry), (self.flags, self.flagsentry), (self.stringid, self.stringidentry), (self.string, self.stringentry), (self.extra, self.extraentry), (None, self.extraentry)]:
				if self.regex.get():
					if t:
						regex = t.get()
					else:
						regex = self.extraentry.get(1.0,END)
					if not regex.startswith('\\A'):
						regex = '.*' + regex
					if not regex.endswith('\\Z'):
						regex = regex + '.*'
				else:
					if t:
						regex = t.get()
					else:
						regex = self.extraentry.get(1.0,END)
					regex = '.*%s.*)' % re.escape(regex)
				try:
					m.append(re.compile(regex, [re.I,0][self.casesens.get()]))
				except:
					e.c = e['bg']
					e['bg'] = '#FFB4B4'
					self.reset = e
					self.resettimer = self.after(1000, self.updatecolor)
					return
			for id,ai in self.ai.ais.items():
				flags = AIBIN.convflags(ai[2])
				string = TBL.decompile_string(self.tbl.strings[ai[1]])
				if m[0].match(id) and (not self.bw.get() or min(ai[0],1) != self.bw.get()-1) and m[1].match(flags) and m[2].match(str(ai[1])) and m[3].match(string):
					self.listbox.insert(END,'%s     %s     %s     %s)' % (id, ['BW','  '][min(ai[0],1)], flags, string))

	def select(self):
		if self.findstr:
			index = re.split(r'\s+', self.listbox.get(self.listbox.curselection()[0]).strip())[0]
			self.parent.listbox.select_clear(0,END)
			self.parent.listbox.select_set(index)
			self.parent.listbox.see(index)
		else:
			indexs = self.listbox.curselection()
			ids = []
			for index in indexs:
				ids.append(self.listbox.get(index)[:4])
			self.parent.listbox.select_clear(0,END)
			see = True
			for index in range(self.parent.listbox.size()):
				if self.parent.listbox.get(index)[:4] in ids:
					self.parent.listbox.select_set(index)
					if see:
						self.parent.listbox.see(index)
						see = False
		self.ok()

	def ok(self):
		savesize(self, self.parent.settings, ['findscriptwindow','findstringwindow'][self.findstr])
		PyMSDialog.ok(self)

class ExternalDefDialog(PyMSDialog):
	def __init__(self, parent):
		PyMSDialog.__init__(self, parent, 'External Definitions')

	def widgetize(self):
		self.bind('<Insert>', self.add)
		self.bind('<Delete>', self.remove)
		buttons = [
			('add', self.add, 'Add File (Insert)', NORMAL),
			('remove', self.remove, 'Remove File (Delete)', DISABLED),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = get_img(btn[0])
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				button.tooltip = Tooltip(button, btn[2], couriernew)
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.pack(side=TOP, fill=X, padx=2, pady=1)

		##Listbox
		listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, font=couriernew, yscrollcommand=scrollbar.set, activestyle=DOTBOX, width=1, height=1, bd=0, highlightthickness=0, exportselection=0)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(fill=BOTH, expand=1)
		self.update()

		##Buttons
		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		buttons.pack()

		self.minsize(200,150)
		if 'externaldefwindow' in self.parent.settings:
			loadsize(self, self.parent.settings, 'externaldefwindow', True)
		return ok

	def add(self, key=None):
		iimport = self.parent.select_file('Add External Definition File', True, '.txt', [('Text Files','*.txt'),('All Files','*')], self)
		if iimport and iimport not in self.parent.extdefs:
			self.parent.extdefs.append(iimport)
			self.update()
			self.listbox.select_set(END)
			self.listbox.see(END)

	def remove(self, key=None):
		if key and self.buttons['remove']['state'] == DISABLED:
			return
		index = int(self.listbox.curselection()[0])
		del self.parent.extdefs[index]
		if self.parent.extdefs and index == len(self.parent.extdefs):
			self.listbox.select_set(index-1)
			self.listbox.see(index-1)
		self.update()

	def update(self):
		sel = 0
		if self.listbox.size():
			sel = self.listbox.curselection()[0]
			self.listbox.delete(0, END)
		if self.parent.extdefs:
			self.buttons['remove']['state'] = NORMAL
			for file in self.parent.extdefs:
				self.listbox.insert(END, file)
			self.listbox.select_set(sel)
		else:
			self.buttons['remove']['state'] = DISABLED

	def ok(self):
		savesize(self, self.parent.settings, 'externaldefwindow')
		PyMSDialog.ok(self)

class ImportListDialog(PyMSDialog):
	def __init__(self, parent):
		PyMSDialog.__init__(self, parent, 'List Importing')

	def widgetize(self):
		self.bind('<Insert>', self.add)
		self.bind('<Delete>', self.remove)
		self.bind('<Control-i>', self.iimport)
		buttons = [
			('add', self.add, 'Add File (Insert)', NORMAL),
			('remove', self.remove, 'Remove File (Delete)', DISABLED),
			10,
			('import', self.iimport, 'Import Selected Script (Ctrl+I)', DISABLED),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = get_img(btn[0])
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				button.tooltip = Tooltip(button, btn[2], couriernew)
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.pack(side=TOP, fill=X, padx=2, pady=1)

		##Listbox
		listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, font=couriernew, yscrollcommand=scrollbar.set, activestyle=DOTBOX, width=1, height=1, bd=0, highlightthickness=0, exportselection=0)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(fill=BOTH, expand=1)

		##Buttons
		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		self.importbtn = Button(buttons, text='Import All', width=10, command=self.iimportall, state=[NORMAL,DISABLED][not self.parent.imports])
		self.importbtn.pack(padx=3, pady=3)
		buttons.pack()

		if self.parent.imports:
			self.update()
			self.listbox.select_set(0)
			self.listbox.see(0)

		self.minsize(200,150)
		if 'listimportwindow' in self.parent.settings:
			loadsize(self, self.parent.settings, 'listimportwindow', True)
		return ok

	def select_files(self):
		path = self.parent.settings.get('lastpath', BASE_DIR)
		file = tkFileDialog.askopenfilename(parent=self, title='Add Imports', defaultextension='.txt', filetypes=[('Text Files','*.txt'),('All Files','*')], initialdir=path, multiple=True)
		if file:
			self.parent.settings['lastpath'] = os.path.dirname(file[0])
		return file

	def add(self, key=None):
		iimport = self.select_files()
		if iimport:
			for i in iimport:
				if i not in self.parent.imports:
					self.parent.imports.append(i)
			self.update()
			self.listbox.select_clear(0,END)
			self.listbox.select_set(END)
			self.listbox.see(END)

	def remove(self, key=None):
		if key and self.buttons['remove']['state'] == DISABLED:
			return
		index = int(self.listbox.curselection()[0])
		del self.parent.imports[index]
		if self.parent.imports and index == len(self.parent.imports):
			self.listbox.select_set(index-1)
			self.listbox.see(index-1)
		self.update()

	def iimport(self, key=None):
		if key and self.buttons['import']['state'] == DISABLED:
			return
		self.parent.iimport(iimport=self.listbox.get(self.listbox.curselection()[0]), parent=self)

	def iimportall(self):
		self.parent.iimport(iimport=self.parent.imports, parent=self)

	def update(self):
		sel = 0
		if self.listbox.size():
			sel = self.listbox.curselection()[0]
			self.listbox.delete(0, END)
		if self.parent.imports:
			self.buttons['remove']['state'] = NORMAL
			self.buttons['import']['state'] = NORMAL
			self.importbtn['state'] = NORMAL
			for file in self.parent.imports:
				self.listbox.insert(END, file)
			self.listbox.select_set(sel)
		else:
			self.buttons['remove']['state'] = DISABLED
			self.buttons['import']['state'] = NORMAL
			self.importbtn['state'] = DISABLED

	def ok(self):
		savesize(self, self.parent.settings, 'listimportwindow')
		PyMSDialog.ok(self)

class ContinueImportDialog(PyMSDialog):
	def __init__(self, parent, id):
		self.id = id
		self.cont = 0
		PyMSDialog.__init__(self, parent, 'Continue Importing?')

	def widgetize(self):
		Label(self, text="The AI Script with ID '%s' already exists, overwrite it?)" % self.id).pack(pady=10)
		frame = Frame(self)
		yes = Button(frame, text='Yes', width=10, command=self.yes)
		yes.pack(side=LEFT, padx=3)
		Button(frame, text='Yes to All', width=10, command=self.yestoall).pack(side=LEFT, padx=3)
		Button(frame, text='No', width=10, command=self.ok).pack(side=LEFT, padx=3)
		Button(frame, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3)
		frame.pack(pady=10, padx=3)
		return yes

	def yes(self):
		self.cont = 1
		self.ok()

	def yestoall(self):
		self.cont = 2
		self.ok()

	def cancel(self):
		self.cont = 3
		self.ok()

class EditScriptDialog(PyMSDialog):
	def __init__(self, parent, id='MYAI', flags=0, string=0, aiinfo='', title='Edit AI ID, String and Extra Info.', initial=''):
		self.initialid = initial
		self.validid = id
		self.id = StringVar()
		self.id.set(id)
		self.id.trace('w', self.editid)
		self.flags = flags
		self.validstring = string
		self.string = StringVar()
		self.string.set(string)
		self.string.trace('w', self.editstring)
		self.actualstring = StringVar()
		self.actualstring.set(TBL.decompile_string(parent.ai.tbl.strings[string]))
		self.aiinfo = aiinfo

		self.ai = parent.ai
		self.tbl = parent.tbl
		self.settings = parent.settings
		self.edittbl = parent.edittbl
		self.stattxt = parent.stattxt
		self.strings = parent.strings
		self.resort = parent.resort
		self.select_file = parent.select_file
		PyMSDialog.__init__(self, parent, title)

	def widgetize(self):
		frame = Frame(self)

		##Entries
		entries = Frame(frame)
		id = Frame(entries)
		Label(id, text='AI ID:', width=10, anchor=E).pack(side=LEFT)
		identry = Entry(id, justify=LEFT, textvariable=self.id, width=10, validate='key', vcmd=self.editid).pack(side=LEFT)
		Button(id, text='Flags', width=10, command=self.editflags).pack(side=RIGHT, padx=1, pady=2) 
		id.pack(fill=X)
		string = Frame(entries)
		Label(string, text='String:', width=10, anchor=E).pack(side=LEFT)
		stringid = Entry(string, justify=LEFT, textvariable=self.string, width=10, vcmd=self.editstring)
		stringid.pack(side=LEFT)
		Label(string, textvariable=self.actualstring, anchor=W, width=1).pack(side=LEFT, fill=X, expand=1)
		Button(string, text='Browse...', width=10, command=self.browse).pack(side=RIGHT, padx=1, pady=2) 
		string.pack(fill=X)

		##Extra info
		aiinfo = Frame(entries)
		Label(aiinfo, text='Extra Info:', width=10, anchor=NE).pack(side=LEFT, fill=Y)
		vscroll = Scrollbar(aiinfo)
		self.info = Text(aiinfo, yscrollcommand=vscroll.set, width=1, height=1, wrap=WORD)
		self.info.insert(1.0, self.aiinfo)
		self.info.pack(side=LEFT, fill=BOTH, expand=1)
		vscroll.config(command=self.info.yview)
		vscroll.pack(side=RIGHT, fill=Y)
		aiinfo.pack(fill=BOTH, expand=1)

		entries.pack(side=LEFT, fill=BOTH, expand=1)
		frame.pack(fill=BOTH, expand=1)

		##Buttons
		buttonframe = Frame(self)
		self.okbtn = Button(buttonframe, text='Ok', width=10, command=self.ok)
		self.okbtn.pack(side=LEFT, padx=3, pady=3)
		Button(buttonframe, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		buttonframe.pack()

		self.minsize(300,200)
		if 'scripteditwindow' in self.parent.settings:
			loadsize(self, self.parent.settings, 'scripteditwindow', True)

		return identry

	def editflags(self):
		f = FlagEditor(self, self.flags)
		if f.flags != None:
			self.flags = f.flags

	def editid(self, *_):
		new = self.id.get()
		if len(new) > 4 or [x for x in ',():' if x in new]:
			self.id.set(self.validid)
		else:
			self.validid = new
		if hasattr(self, 'okbtn'):
			if len(new) < 4:
				self.okbtn['state'] = DISABLED
			elif len(new) == 4:
				self.okbtn['state'] = NORMAL

	def editstring(self, *_):
		s = self.string.get()
		if s:
			try:
				s = int(self.string.get())
				if s < 0:
					raise
			except:
				s = self.validstring
			else:
				strs = len(self.ai.tbl.strings)-1
				if s > strs:
					s = sts
			self.string.set(s)
		else:
			s = 0
		self.validstring = s
		self.actualstring.set(TBL.decompile_string(self.ai.tbl.strings[s]))

	def browse(self):
		s = StringEditor(self, 'Select a String', True, self.string.get())
		if s.result != None:
			self.string.set(s.result)

	def ok(self):
		id = self.id.get()
		if self.initialid != id and id in self.parent.ai.ais:
			replace = askquestion(parent=self, title='Replace Script?', message="The script with ID '%s' already exists, replace it?)" % id, default=YES, type=YESNOCANCEL)
			if replace == 'yes':
				if not self.ai.ais[id][0]:
					del self.ai.bwscript.ais[id]
				if id in self.ai.aiinfo:
					del self.ai.aiinfo[id]
			else:
				if replace == 'no':
					self.cancel()
				return
		if not self.string.get():
			self.string.set(0)
		self.aiinfo = self.info.get(1.0, END)[:-1]
		savesize(self, self.parent.settings, 'scripteditwindow')
		PyMSDialog.ok(self)

	def cancel(self):
		savesize(self, self.parent.settings, 'scripteditwindow')
		self.id.set('')
		PyMSDialog.ok(self)

class EditStringDialog(PyMSDialog):
	def __init__(self, parent, string, title='Edit String'):
		self.string = string
		PyMSDialog.__init__(self, parent, title)

	def widgetize(self):
		Label(self, text='String:', anchor=W).pack(fill=X)

		##Text
		info = Frame(self)
		vscroll = Scrollbar(info)
		self.info = Text(info, yscrollcommand=vscroll.set, width=1, height=1, wrap=WORD)
		self.info.insert(1.0, self.string)
		self.info.pack(side=LEFT, fill=BOTH, expand=1)
		vscroll.config(command=self.info.yview)
		vscroll.pack(side=RIGHT, fill=Y)
		info.pack(fill=BOTH, expand=1)

		##Buttons
		buttonframe = Frame(self)
		self.okbtn = Button(buttonframe, text='Ok', width=10, command=self.ok)
		self.okbtn.pack(side=LEFT, padx=3, pady=3)
		Button(buttonframe, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		buttonframe.pack()

		self.minsize(300,100)
		if 'stringeditwindow' in self.parent.parent.settings:
			loadsize(self, self.parent.settings, 'stringeditwindow', True)

		return self.info

	def ok(self):
		string = TBL.compile_string(self.info.get(1.0, END)[:-1])
		if not string.endswith('\x00'):
			string += '\x00'
		savesize(self, self.parent.parent.settings, 'stringeditwindow')
		self.string = string
		PyMSDialog.ok(self)

	def cancel(self):
		savesize(self, self.parent.parent.settings, 'stringeditwindow')
		PyMSDialog.ok(self)

class StringEditor(PyMSDialog):
	def __init__(self, parent, title='String Editor', cancel=False, index=0):
		self.result = None
		self.cancelbtn = cancel
		self.index = index

		self.ai = parent.ai
		self.tbl = parent.tbl
		self.settings = parent.settings
		self.edittbl = parent.edittbl
		self.stattxt = parent.stattxt
		self.strings = parent.strings
		self.resort = parent.resort
		self.select_file = parent.select_file
		PyMSDialog.__init__(self, parent, '%s (%s))' % (title, parent.stattxt()))

	def widgetize(self):
		self.bind('<Control-o>', self.open)
		self.bind('<Control-d>', self.opendefault)
		self.bind('<Control-s>', self.save)
		self.bind('<Control-Alt-s>', self.saveas)
		self.bind('<Insert>', self.add)
		self.bind('<Delete>', self.remove)
		self.bind('<Control-f>', self.find)
		self.bind('<Control-e>', self.edit)
		#Toolbar
		buttons = [
			('open', self.open, 'Open (Ctrl+O)', NORMAL),
			('opendefault', self.opendefault, 'Open Default TBL (Ctrl+D)', NORMAL),
			('save', self.save, 'Save (Ctrl+S)', NORMAL),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+S)', NORMAL),
			10,
			('add', self.add, 'Add String (Insert)', NORMAL),
			('remove', self.remove, 'Remove String (Delete)', NORMAL),
			4,
			('find', self.find, 'Find String (Ctrl+F)', NORMAL),
			10,
			('edit', self.edit, 'Edit String (Ctrl+E)', NORMAL),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = get_img(btn[0])
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				button.tooltip = Tooltip(button, btn[2], couriernew)
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.pack(side=TOP, fill=X, padx=2, pady=1)

		##Listbox
		listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, font=couriernew, bd=0, activestyle=DOTBOX, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0)
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', self.home),
			('<End>', self.end),
			('<Up>', self.up),
			('<Down>', self.down),
			('<Prior>', self.pageup),
			('<Next>', self.pagedown),
		]
		for b in bind:
			self.bind(*b)
		self.listbox.bind('<ButtonRelease-3>', self.popup)
		self.listbox.bind('<Double-Button-1>', self.edit)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(fill=BOTH, expand=1)

		listmenu = [
			('Add String', self.add, 4), # 0
			('Remove String', self.remove, 0), # 1
			None,
			('Edit String', self.edit, 8), # 3
		]
		self.listmenu = Menu(self, tearoff=0)
		for m in listmenu:
			if m:
				l,c,u = m
				self.listmenu.add_command(label=l, command=c, underline=u)
			else:
				self.listmenu.add_separator()

		##Buttons
		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		if self.cancelbtn:
			Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		##Statusbar
		self.status = StringVar()
		statusbar = Label(self, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W).pack(side=BOTTOM, fill=X)

		self.update()
		self.listbox.select_clear(0,END)
		self.listbox.select_set(self.index)
		self.listbox.see(self.index)

		self.minsize(300,300)
		if 'stringeditorwindow' in self.parent.settings:
			loadsize(self, self.parent.settings, 'stringeditorwindow', True)
		return ok

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def home(self, e):
		self.listbox.yview('moveto', 0.0)

	def end(self, e):
		self.listbox.yview('moveto', 1.0)

	def up(self, e):
		self.listbox.yview('scroll', -1, 'units')

	def down(self, e):
		self.listbox.yview('scroll', 1, 'units')

	def pageup(self, e):
		self.listbox.yview('scroll', -1, 'pages')

	def pagedown(self, e):
		self.listbox.yview('scroll', 1, 'pages')

	def popup(self, e):
		if not self.listbox.curselection():
			s = DISABLED
		else:
			s = NORMAL
		for i in [1,3]:
			self.listmenu.entryconfig(i, state=s)
		self.listmenu.post(e.x_root, e.y_root)

	def find(self, e=None):
		if self.listbox.size():
			FindDialog(self, True)

	def ok(self):
		self.result = int(self.listbox.curselection()[0])
		savesize(self, self.parent.settings, 'stringeditorwindow')
		PyMSDialog.ok(self)

	def cancel(self):
		self.result = None
		savesize(self, self.parent.settings, 'stringeditorwindow')
		PyMSDialog.ok(self)

	def update(self):
		sel = 0
		if self.listbox.size():
			sel = self.listbox.curselection()[0]
			self.listbox.delete(0, END)
		size = len(self.parent.tbl.strings)
		pad = len(str(size))
		for n,s in enumerate(self.parent.tbl.strings):
			self.listbox.insert(END, '%s%s     %s)' % (' ' * (pad - len(str(n))), n, TBL.decompile_string(s)))
		self.listbox.select_set(sel)
		self.listbox.see(sel)
		self.status.set('Strings: %s)' % size)

	def open(self, file=None):
		if self.parent.edittbl():
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?)" % self.parent.stattxt(), default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return
				if self.tbl:
					self.save()
				else:
					self.saveas()
		if file == None:
			file = self.parent.select_file('Open stat_txt.tbl', True, '.tbl', [('TBL Files','*.tbl'),('All Files','*')], self)
		if file:
			tbl = TBL.TBL()
			try:
				tbl.load_file(file)
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			max = len(tbl.strings)
			ids = {}
			for s,i in self.parent.strings.items():
				if s >= max:
					ids[s] = i
			if ids:
				pass
			if self.parent.ai:
				self.parent.ai.tbl = tbl
			self.parent.tbl = tbl
			self.parent.stattxt(file)
			self.title('String Editor (%s))' % file)
			self.update()
			self.parent.edittbl(False)

	def opendefault(self):
		self.open(os.path.join(BASE_DIR, 'Libs', 'MPQ', 'rez' 'stat_txt.tbl'))

	def save(self, key=None, file=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		if file == None:
			file = self.parent.stattxt()
		try:
			self.tbl.compile(file)
			self.parent.stattxt(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.tbledited = False

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		file = self.parent.select_file('Save stat_txt.tbl', False, '.tbl', [('TBL Files','*.tbl'),('All Files','*')], self)
		if not file:
			return
		self.save(None, file)

	def add(self, key=None):
		if key and self.buttons['add']['state'] != NORMAL:
			return
		e = EditStringDialog(self, '', 'Add String')
		if e.string:
			self.parent.tbl.strings.append(e.string)
			self.update()
			self.listbox.select_clear(0, END)
			self.listbox.select_set(END)
			self.listbox.see(END)
			self.parent.edittbl(True)
			if self.parent.ai:
				self.parent.resort()

	def remove(self, key=None):
		if key and self.buttons['remove']['state'] != NORMAL:
			return
		string = int(self.listbox.curselection()[0])
		if self.parent.ai:
			ids = {}
			for s,i in self.parent.strings.items():
				if s > string:
					ids[s] = i
			if ids:
				plural = 0
				i = ''
				e = 0
				for s,x in ids.items():
					if e < 6:
						i += '    '
					comma = False
					for n in x:
						if plural < 2:
							plural += 1
						if e < 6 and comma:
							i += ", "
						else:
							comma = True
						if e < 6:
							i += n
					if e < 6:
						i += ': %s\n)' % s
					e += 1
				if e > 5:
					i += 'And %s other scripts. )' % (e-5)
				if plural == 2:
					plural = 1
				if not askquestion(parent=self, title='Remove String?', message="Deleting string '%s' will effect the AI Script%s:\n%sContinue removing string anyway?)" % (string, 's' * plural, i), default=YES):
					return
				end = self.listbox.size()-1
				if end in self.parent.strings:
					new = self.listbox.size()-2
					for id in self.parent.strings[end]:
						self.parent.ai.ais[id][1] = new
					if not new in self.parent.strings:
						self.parent.strings[new] = []
					self.parent.strings[new].extend(self.parent.strings[end])
					del self.parent.strings[string]
				if self.parent.ai:
					self.parent.resort()
		del self.parent.tbl.strings[string]
		if string:
			self.listbox.select_set(string-1)
		else:
			self.listbox.select_set(0)
		self.parent.edittbl(True)
		self.update()

	def edit(self, key=None):
		if key and self.buttons['edit']['state'] != NORMAL:
			return
		id = int(self.listbox.curselection()[0])
		string = TBL.decompile_string(self.parent.tbl.strings[id])
		e = EditStringDialog(self, string)
		if string != e.string:
			self.parent.edittbl(True)
			self.parent.tbl.strings[id] = e.string
			self.update()
			if self.parent.ai:
				self.parent.resort()
class FlagEditor(PyMSDialog):
	def __init__(self, parent, flags):
		self.flags = flags
		self.location = IntVar()
		self.location.set(not not flags & 1)
		self.visible = IntVar()
		self.visible.set(not not flags & 2)
		self.bwonly = IntVar()
		self.bwonly.set(not not flags & 4)
		PyMSDialog.__init__(self, parent, 'Flag Editor')

	def widgetize(self):
		self.resizable(False, False)
		choices = Frame(self)
		Checkbutton(choices, text='Requires a Location', variable=self.location).grid(sticky=W)
		Checkbutton(choices, text='Invisible in StarEdit', variable=self.visible).grid(sticky=W)
		Checkbutton(choices, text='BroodWar Only', variable=self.bwonly).grid(sticky=W)
		choices.pack(pady=3, padx=3)
		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=1, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=1, pady=3)
		buttons.pack(pady=3, padx=3)
		return ok

	def ok(self):
		self.flags = self.location.get() + 2 * self.visible.get() + 4 * self.bwonly.get()
		PyMSDialog.ok(self)

class ListboxTooltip(Tooltip):
	def __init__(self, widget, font=None, delay=750, press=False):
		Tooltip.__init__(self, widget, '', font, delay, press)
		self.index = None

	def enter(self, e):
		if self.widget.size():
			self.motion(e)
			Tooltip.enter(self,e)

	def leave(self, e=None):
		Tooltip.leave(self,e)
		if e and e.type == '4':
			self.enter(e)

	def motion(self, e):
		if self.tip and self.index != self.widget.nearest(e.y):
			self.leave()
			self.enter(e)
		self.pos = (e.x,e.y)
		Tooltip.motion(self, e)

	def showtip(self):
		if self.tip:
			return
		self.tip = Toplevel(self.widget)
		self.tip.maxsize(640,400)
		self.tip.wm_overrideredirect(1)
		pos = list(self.widget.winfo_pointerxy())
		self.index = self.widget.nearest(pos[1] - self.widget.winfo_rooty())
		item = self.widget.get_entry(self.index)
		id = item[0]
		flags = ''
		comma = False
		for d,f in zip(['BroodWar Only','Invisible in StarEdit','Requires a Location'],item[2]):
			if f == '1':
				if comma:
					flags += ', '
				else:
					comma = True
				if not flags:
					flags = 'Flags             : '
				flags += d
		if flags:
			flags += '\n'
		text = "Script ID         : %s\nIn bwscript.bin   : %s\n%sString ID         : %s\n)" % (id, ['No','Yes'][item[1]], flags, item[3])
		ai = self.widget.master.master.ai
		text += fit('String            : ', TBL.decompile_string(ai.tbl.strings[ai.ais[id][1]]), end=True)
		if id in ai.aiinfo and ai.aiinfo[id][0]:
			text += 'Extra Information : %s)' % ai.aiinfo[id][0].replace('\n','\n                    ')
		else:
			text = text[:-1]
		frame = Frame(self.tip, background='#FFFFC8', relief=SOLID, borderwidth=1)
		Label(frame, text=text, justify=LEFT, font=self.font, background='#FFFFC8', relief=FLAT).pack(padx=1, pady=1)
		frame.pack()
		self.tip.wm_geometry('+%d+%d)' % (pos[0],pos[1]+22))
		self.tip.update_idletasks()
		move = False
		if pos[0] + self.tip.winfo_reqwidth() > self.tip.winfo_screenwidth():
			move = True
			pos[0] = self.tip.winfo_screenwidth() - self.tip.winfo_reqwidth()
		if pos[1] + self.tip.winfo_reqheight() + 22 > self.tip.winfo_screenheight():
			move = True
			pos[1] -= self.tip.winfo_reqheight() + 44
		if move:
			self.tip.wm_geometry('+%d+%d)' % (pos[0],pos[1]+22))

class PyAI(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyAI',
			{
				'stat_txt':os.path.join(BASE_DIR, 'Libs', 'MPQ', 'rez', 'stat_txt.tbl'),
				'unitsdat':'MPQ:arr\\units.dat',
				'upgradesdat':'MPQ:arr\\upgrades.dat',
				'techdatadat':'MPQ:arr\\techdata.dat',
			}
		)
		# Remove sometime (now 2.2)
		if 'datdialog' in self.settings:
			del self.settings['datdialog']

		#Window
		Tk.__init__(self)
		self.title('No files loaded')
		try:
			self.icon = os.path.join(BASE_DIR, 'Images','PyAI.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s)' % os.path.join(BASE_DIR, 'Images','PyAI.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		setup_trace(self, 'PyAI')

		self.aiscript = None
		self.bwscript = None
		self.stat_txt = self.settings['stat_txt']
		self.tbl = TBL.TBL()
		try:
			self.tbl.load_file(self.stat_txt)
		except:
			self.stat_txt = None
			self.tbl = None
		self.tbledited = False
		self.unitsdat = None
		self.upgradesdat = None
		self.techdat = None
		self.ai = None
		self.strings = {}
		self.edited = False
		self.undos = []
		self.redos = []
		self.imports = []
		self.extdefs = []
		for t,l in [('imports',self.imports),('extdefs',self.extdefs)]:
			if t in self.settings:
				for f in self.settings.get(t):
					if os.path.exists(f):
						l.append(f)
		self.highlights = self.settings.get('highlights', None)
		self.findhistory = []
		self.replacehistory = []

		self.sort = StringVar()
		self.reference = IntVar()
		self.reference.set(self.settings.get('reference', 0))
		self.extrainfo = IntVar()
		self.extrainfo.set(self.settings.get('extrainfo', 1))

		#Menu
		menus = odict()
		menus['File'] = [
			('New', self.new, NORMAL, 'Ctrl+N', 0), # 0
			('Open', self.open, NORMAL, 'Ctrl+O', 0), # 1
			('Open Default Scripts', self.open_default, NORMAL, 'Ctrl+D', 5), # 2
			('Open MPQ', self.open_mpq, [NORMAL,DISABLED][FOLDER], 'Ctrl+Alt+O', 5), # 3
			('Save', self.save, DISABLED, 'Ctrl+S', 0), # 4
			('Save As...', self.saveas, DISABLED, 'Ctrl+Alt+A', 5), # 5
			('Save MPQ', self.savempq, [NORMAL,DISABLED][FOLDER], 'Ctrl+Alt+M', 1), # 6
			('Close', self.close, DISABLED, 'Ctrl+W', 0), # 7
			None,
			('Set as default *.bin editor (Windows Only)', self.register, [DISABLED,NORMAL][win_reg], '', 2),
			None,
			('Exit', self.exit, NORMAL, 'Alt+F4', 0), # 7
		]
		menus['Edit'] = [
			('Undo', self.undo, DISABLED, 'Ctrl+Z', 0), # 0
			('Redo', self.redo, DISABLED, 'Ctrl+Y', 3), # 1
			None,
			('Select All', self.select_all, DISABLED, 'Ctrl+A', 7), # 3
			('Add Blank Script', self.add, DISABLED, 'Insert', 4), # 4
			('Remove Scripts', self.remove, DISABLED, 'Delete', 0), # 5
			('Find Scripts', self.find, DISABLED, 'Ctrl+F', 0), # 6
			None,
			('Export Scripts', self.export, DISABLED, 'Ctrl+Alt+E', 0), # 8
			('Import Scripts', self.iimport, DISABLED, 'Ctrl+Alt+I', 0), # 9
			('Import a List of Files', self.listimport, DISABLED, 'Ctrl+L', 9), # 10
			('Print Reference when Decompiling', self.reference, NORMAL, '', 6, True), # 11
			('Save Information Comments and Labels', self.extrainfo, NORMAL, '', 0, True), # 12
			None,
			('Edit AI Script', self.edit, DISABLED, 'Ctrl+E', 0), #14
			('Edit AI ID, String, and Extra Info.', self.edit, DISABLED, 'Ctrl+I', 8), # 15
			('Edit Flags', self.editflags, DISABLED, 'Ctrl+G', 8), # 16
			None,
			('Manage External Definition Files', self.extdef, NORMAL, 'Ctrl+X', 8), # 18
			('Manage TBL File', self.managetbl, NORMAL, 'Ctrl+T', 7), # 19
			('Manage MPQ and DAT Settings', self.managedat, NORMAL, 'Ctrl+U', 7), # 20
		]
		menus['View'] = [
			('File Order', self.order, NORMAL, '', 5, 'order'), # 0
			('Sort by ID', self.idsort, NORMAL, '', 8, 'idsort'), # 1
			('Sort by BroodWar', self.bwsort, NORMAL, '', 8, 'bwsort'), # 2
			('Sort by Flags', self.flagsort, NORMAL, '', 8, 'flagsort'), # 3
			('Sort by Strings', self.stringsort, NORMAL, '', 8, 'stringsort'), # 4
		]
		menus['Help'] = [
			('View Help File', self.help, NORMAL, 'F1', 5), # 0
			None,
			('About PyAI', self.about, NORMAL, '', 0), # 2
		]
		self.menus = {}
		menubar = Menu(self)
		self.config(menu=menubar)
		for name,menu in menus.items():
			self.menus[name] = Menu(menubar, tearoff=0)
			for n,m in enumerate(menu):
				if m:
					if name == 'View':
						l,c,s,a,u,v = m
						self.menus[name].add_radiobutton(label=l, command=c, state=s, accelerator=a, underline=u, variable=self.sort, value=v)
					elif len(m) == 6:
						l,v,s,a,u,_ = m
						self.menus[name].add_checkbutton(label=l, state=s, accelerator=a, underline=u, variable=v)
					else:
						l,c,s,a,u = m
						self.menus[name].add_command(label=l, command=c, state=s, accelerator=a, underline=u)
					if a:
						if not a.startswith('F'):
							self.bind('<%s%s>)' % (a[:-1].replace('Ctrl','Control').replace('+','-'), a[-1].lower()), c)
						else:
							self.bind('<%s>)' % a, c)
				else:
					self.menus[name].add_separator()
			menubar.add_cascade(label=name, menu=self.menus[name], underline=0)

		#Toolbar
		bars = [
			[
				('new', self.new, 'New (Ctrl+N)', NORMAL),
				('open', self.open, 'Open (Ctrl+O)', NORMAL),
				('opendefault', self.open_default, 'Open Default Scripts (Ctrl+D)', NORMAL),
				('openmpq', self.open_mpq, 'Open MPQ (Ctrl+Alt+O)', [NORMAL,DISABLED][FOLDER]),
				('save', self.save, 'Save (Ctrl+S)', DISABLED),
				('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', DISABLED),
				('savempq', self.savempq, 'Save MPQ (Ctrl+Alt+M)', DISABLED),
				('close', self.close, 'Close (Ctrl+W)', DISABLED),
				10,
				('undo', self.undo, 'Undo (Ctrl+Z)', DISABLED),
				('redo', self.redo, 'Redo (Ctrl+Y)', DISABLED),
				10,
				('order', self.order, 'File Order', NORMAL, True),
				('idsort', self.idsort, 'Sort by ID', NORMAL, True),
				('bwsort', self.bwsort, 'Sory by BroodWar', NORMAL, True),
				('flagsort', self.flagsort, 'Sort by Flags', NORMAL, True),
				('stringsort', self.stringsort, 'Sort by String', NORMAL, True),
				10,
				('register', self.register, 'Set as default *.bin editor (Windows Only)', [DISABLED,NORMAL][win_reg]),
				('help', self.help, 'Help (F1)', NORMAL),
				('about', self.about, 'About PyAI', NORMAL),
				10,
				('exit', self.exit, 'Exit (Alt+F4)', NORMAL)
			],
			[
				('add', self.add, 'Add Blank Script (Insert)', DISABLED),
				('remove', self.remove, 'Remove Scripts (Delete)', DISABLED),
				4,
				('find', self.find, 'Find Scripts (Ctrl+F)', DISABLED),
				10,
				('export', self.export, 'Export Scripts (Ctrl+Alt+E)', DISABLED),
				('import', self.iimport, 'Import Scripts (Ctrl+Alt+I)', DISABLED),
				('listimport', self.listimport, 'Import a List of Files (Ctrl+L)', DISABLED),
				4,
				('reference', self.reference, 'Print Reference when Decompiling', NORMAL, False),
				('saveextra', self.extrainfo, 'Save Information Comments and Labels', NORMAL, False),
				10,
				('codeedit', self.codeedit, 'Edit AI Script (Ctrl+E)', DISABLED),
				('edit', self.edit, 'Edit AI ID, String, and Extra Info. (Ctrl+I)', DISABLED),
				('flags', self.editflags, 'Edit Flags (Ctrl+G)', DISABLED),
				10,
				('extdef', self.extdef, 'Manage External Definition Files (Ctrl+X)', NORMAL),
				('tbl', self.managetbl, 'Manage TBL file (Ctrl+T)', NORMAL),
				('asc3topyai', self.managedat, 'Manage MPQ and DAT Settings (Ctrl+U)', NORMAL),
				4,
				('openset', self.openset, 'Open TBL and DAT Settings', NORMAL),
				('saveset', self.saveset, 'Save TBL and DAT Settings', NORMAL),
			]
		]
		self.buttons = {}
		for pad,bar,buttons in zip([2,1],[Frame(self),Frame(self)],bars):
			for btn in buttons:
				if isinstance(btn, tuple):
					image = get_img(btn[0])
					if len(btn) == 4:
						button = Button(bar, image=image, width=20, height=20, command=btn[1], state=btn[3])
					elif btn[4]:
						button = Radiobutton(bar, image=image, width=20, height=20, command=btn[1], state=btn[3], indicatoron=0, variable=self.sort, value=btn[0])
					else:
						button = Checkbutton(bar, image=image, width=20, height=20, state=btn[3], indicatoron=0, variable=btn[1])
					button.image = image
					button.tooltip = Tooltip(button, btn[2], couriernew)
					button.pack(side=LEFT)
					if button.winfo_reqwidth() > 26:
						button['width'] = 18
					if button.winfo_reqheight() > 26:
						button['height'] = 18
					self.buttons[btn[0]] = button
				else:
					Frame(bar, width=btn).pack(side=LEFT)
			bar.pack(side=TOP, fill=X, padx=2, pady=pad)
		self.sort.set('order')

		#Listbox
		listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, selectmode=EXTENDED, font=couriernew, activestyle=DOTBOX, width=1, height=1, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0)
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
		for b in bind:
			self.bind(*b)
		self.listbox.bind('<ButtonRelease-3>', self.popup)
		self.listbox.bind('<Double-Button-1>', self.codeedit)
		self.listbox.tooltip = ListboxTooltip(self.listbox, couriernew)
		self.listbox.get_entry = self.get_entry
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(fill=BOTH, padx=2, pady=2, expand=1)

		listmenu = [
			('Add Blank Script (Insert)', self.add, 4), # 0
			('Remove Scripts (Delete)', self.remove, 0), # 1
			None,
			('Export Scripts (Ctrl+Alt+E)', self.export, 0), # 3
			('Import Scripts (Ctrl+Alt+I)', self.iimport, 0), # 4
			None,
			('Edit AI Script (Ctrl+E)', self.codeedit, 5), #6
			('Edit Script ID, String, and AI Info (Ctrl+I)', self.edit, 8), # 7
			('Edit Flags (Ctrl+G)', self.editflags, 8), # 8
		]
		self.listmenu = Menu(self, tearoff=0)
		for m in listmenu:
			if m:
				l,c,u = m
				self.listmenu.add_command(label=l, command=c, underline=u)
			else:
				self.listmenu.add_separator()

		#Statusbar
		self.status = StringVar()
		self.scriptstatus = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		image = get_img('save')
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, textvariable=self.scriptstatus, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load your files or create new ones.')
		statusbar.pack(side=BOTTOM, fill=X)

		if 'window' in self.settings:
			loadsize(self, self.settings, 'window', True)

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if not 'mpqs' in self.settings:
			self.mpqhandler.add_defaults()
		e = self.open_files()

		if guifile:
			self.open(aiscript=guifile)

		start_new_thread(check_update, (self,))

		if e:
			self.managedat(err=e)

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			unitsdat = DAT.UnitsDAT()
			upgradesdat = DAT.UpgradesDAT()
			techdat = DAT.TechDAT()
			unitsdat.load_file(self.mpqhandler.get_file(self.settings['unitsdat']))
			upgradesdat.load_file(self.mpqhandler.get_file(self.settings['upgradesdat']))
			techdat.load_file(self.mpqhandler.get_file(self.settings['techdatadat']))
			if not self.tbl:
				file = self.select_file('Open a stat_txt.tbl first', True, '.tbl', [('TBL Files','*.tbl'),('All Files','*')])
				if not file:
					r = True
				tbl = TBL.TBL()
				tbl.load_file(file)
				self.stat_txt = file
				self.tbl = tbl
		except PyMSError as e:
			err = e
		else:
			self.unitsdatdat = unitsdat
			self.upgrades = upgradesdat
			self.techdat = techdat
			if self.ai:
				self.ai.unitsdat = unitsdat
				self.ai.upgradesdat = upgradesdat
				self.ai.techdat = techdat
		self.mpqhandler.close_mpqs()
		return err

	# Misc. functions
	def title(self, text=None):
		global LONG_VERSION
		if not text:
			text = self.titletext
		Tk.title(self,'PyAI %s (%s))' % (LONG_VERSION, text))
		self.titletext = text

	def get_entry(self, index):
		match = re.match(r'(....)\s{5}(\s\s|BW)\s{5}([01]{3})\s{5}(.+)', self.listbox.get(index))
		id = match.group(1)
		return (id, match.group(2) == 'BW', match.group(3), self.ai.ais[id][1], match.group(4))

	def entry_text(self, id, bw, flags, string):
		if isinstance(string, int):
			string = TBL.decompile_string(self.ai.tbl.strings[string])
		if len(string) > 50:
			string = string[:47] + '...'
		aiinfo = ''
		if id in self.ai.aiinfo:
			aiinfo = self.ai.aiinfo[id][0]
		return '%s     %s     %s     %s%s%s)' % (id, ['  ','BW'][bw], flags, string, ' ' * (55-len(string)), aiinfo)

	def set_entry(self, index, id, bw, flags, string):
		if index != END:
			self.listbox.delete(index)
		self.listbox.insert(index, self.entry_text(id, bw, flags, string))

	def resort(self):
		{'order':self.order,'idsort':self.idsort,'bwsort':self.bwsort,'flagsort':self.flagsort,'stringsort':self.stringsort}[self.sort.get()]()

	def select_file(self, title, open=True, ext='.bin', filetypes=[('AI Scripts','*.bin'),('All Files','*')], parent=None):
		if parent == None:
			parent = self
		path = self.settings.get('lastpath', BASE_DIR)
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](parent=parent, title=title, defaultextension=ext, filetypes=filetypes, initialdir=path)
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def add_undo(self, type, data):
		max = self.settings.get('undohistory', 10)
		if not max:
			return
		if self.redos:
			self.redos = []
			self.buttons['redo']['state'] = DISABLED
			self.menus['Edit'].entryconfig(1, state=DISABLED)
		if not self.undos:
			self.buttons['undo']['state'] = NORMAL
			self.menus['Edit'].entryconfig(0, state=NORMAL)
		self.undos.append((type, data))
		if len(self.undos) > max:
			del self.undos[0]

	def action_states(self):
		file = [NORMAL,DISABLED][not self.ai]
		select = [NORMAL,DISABLED][not self.listbox.curselection()]
		for entry in [4,5,6,7]:
			self.menus['File'].entryconfig(entry, state=file)
		for entry in [3,4,9,10,11,14,19,20]:
			self.menus['Edit'].entryconfig(entry, state=file)
		for btn in ['save','saveas','close','add','import','listimport','codeedit']:
			self.buttons[btn]['state'] = file
		if not FOLDER:
			self.buttons['savempq']['state'] = file
		for entry in [5,6,8,15,16]:
			self.menus['Edit'].entryconfig(entry, state=select)
		for btn in ['remove','find','export','edit','flags']:
			self.buttons[btn]['state'] = select

	def unsaved(self):
		if self.tbledited:
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?)" % self.stat_txt, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				self.tbl.compile(self.stat_txt)
				self.tbledited = False
		if self.ai and self.edited:
			aiscript = self.aiscript
			if not aiscript:
				aiscript = 'aiscript.bin'
			bwscript = self.bwscript
			if not bwscript:
				bwscript = 'bwscript.bin'
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s' and '%s'?)" % (aiscript, bwscript), default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.aiscript:
					self.save()
				else:
					return self.saveas()

	def edittbl(self, edited=None):
		if edited == None:
			return self.tbledited
		self.tbledited = edited

	def stattxt(self, file=None):
		if file == None:
			return self.stat_txt
		self.stat_txt = file

	def popup(self, e):
		if self.ai:
			if not self.listbox.curselection():
				s = DISABLED
			else:
				s = NORMAL
			for i in [1,3,7,8]:
				self.listmenu.entryconfig(i, state=s)
			self.listmenu.post(e.x_root, e.y_root)

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def move(self, e, a):
		if self.listbox.curselection():
			if a == END:
				a = self.listbox.size()-2
			elif a not in [0,END]:
				a = max(min(self.listbox.size()-1, int(self.listbox.curselection()[0]) + a),0)
			self.listbox.select_clear(0,END)
			self.listbox.select_set(a)
			self.listbox.see(a)

	# Acitions
	def new(self, key=None):
		if not self.unsaved():
			self.ai = AIBIN.AIBIN(False, self.unitsdat, self.upgradesdat, self.techdat, self.tbl)
			self.ai.bwscript = AIBIN.BWBIN(self.unitsdat, self.upgradesdat, self.techdat, self.tbl)
			self.ai.bwscript.tbl = self.tbl
			self.strings = {}
			self.aiscript = None
			self.bwscript = None
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.undos = []
			self.redos = []
			self.title('aiscript.bin, bwscript.bin')
			self.status.set('Editing new file!')
			self.listbox.delete(0, END)
			self.action_states()
			self.scriptstatus.set('aiscript.bin: 0 (0 B)     bwscript.bin: 0 (0 B)')

	def open(self, key=None, aiscript=None, bwscript=None):
		if not self.unsaved():
			if not aiscript:
				aiscript = self.select_file('Open aiscript.bin')
				if not aiscript:
					return
				if not bwscript:
					bwscript = self.select_file('Open bwscript.bin (Cancel to only open aiscript.bin)')
			warnings = []
			try:
				ai = AIBIN.AIBIN(bwscript, self.unitsdat, self.upgradesdat, self.techdat, self.tbl)
				warnings.extend(ai.warnings)
				warnings.extend(ai.load_file(aiscript, True))
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.ai = ai
			self.strings = {}
			for id,ai in self.ai.ais.items():
				if not ai[1] in self.strings:
					self.strings[ai[1]] = []
				self.strings[ai[1]].append(id)
			self.aiscript = aiscript
			self.bwscript = bwscript
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.undos = []
			self.redos = []
			if not bwscript:
				bwscript = 'bwscript.bin'
			self.title('%s, %s)' % (aiscript,bwscript))
			self.status.set('Load Successful!')
			self.resort()
			self.action_states()
			s = 'aiscript.bin: %s (%s B) )' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
			if self.ai.bwscript:
				s += '     bwscript.bin: %s (%s B))' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
			self.scriptstatus.set(s)
			if warnings:
				WarningDialog(self, warnings)

	def open_default(self, key=None):
		self.open(key, os.path.join(BASE_DIR, 'Libs','MPQ','Scripts','aiscript.bin'),os.path.join(BASE_DIR, 'Libs','MPQ','Scripts','bwscript.bin'))

	def open_mpq(self):
		file = self.select_file('Open MPQ', True, '.mpq', [('MPQ Files','*.mpq'),('Embedded MPQ Files','*.exe'),('All Files','*')])
		if not file:
			return
		h = SFileOpenArchive(file)
		if SFInvalidHandle(h):
			ErrorDialog(self, PyMSError('Open','Could not open MPQ "%s")' % file))
			return
		ai = SFile(file='scripts\\aiscript.bin')
		bw = SFile(file='scripts\\bwscirpt.bin')
		for t in ['ai','bw']:
			f = SFileOpenFileEx(h, 'scripts\\%sscript.bin)' % t)
			if f in [None,-1]:
				if t == 'ai':
					SFileCloseArchive(h)
					ErrorDialog(self, PyMSError('Open','Could not find aiscript.bin in the MPQ.'))
					return
				bw = None
				continue
			r = SFileReadFile(f)
			SFileCloseFile(f)
			if t == 'ai':
				ai.text = r[0]
			else:
				bw.text = r[0]
		SFileCloseArchive(h)
		self.open(None,ai,bw)

	def save(self, key=None, ai=None, bw=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		if ai == None:
			ai = self.aiscript
		if bw == None and self.ai.bwscript.ais:
			bw = self.bwscript
		if ai == None:
			self.saveas()
			return
		if self.tbledited:
			file = self.select_file("Save stat_txt.tbl (Cancel doesn't stop bin saving)", False, '.tbl', [('TBL Files','*.tbl'),('All Files','*')])
			if file:
				self.stat_txt = file
				try:
					self.tbl.compile(file, extra=self.extrainfo.get())
				except PyMSError as e:
					ErrorDialog(self, e)
					return
				self.tbledited = False
		try:
			self.ai.compile(ai, bw, extra=self.extrainfo.get())
			self.aiscript = ai
			if bw != None:
				self.bwscript = bw
			self.status.set('Save Successful!')
		except PyMSError as e:
			ErrorDialog(self, e)

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		aiscript = self.select_file('Save aiscript.bin As', False)
		if not aiscript:
			return True
		bwscript = None
		if self.ai.bwscript.ais:
			bwscript = self.select_file('Save bwscript.bin As (Cancel to save aiscript.bin only)', False)
		if self.save(ai=aiscript, bw=bwscript):
			self.tbledited = False
			self.title('%s, %s)' % (self.aiscript,self.bwscript))

	def savempq(self, key=None):
		file = self.select_file('Save MPQ to...', False, '.mpq', [('MPQ Files','*.mpq'),('Self-executing MPQ','*.exe'),('All Files','*')], self)
		if file:
			if file.endswith('%sexe)' % os.extsep):
				if os.path.exists(file):
					h = MpqOpenArchiveForUpdate(file, MOAU_OPEN_ALWAYS | MOAU_MAINTAIN_LISTFILE)
				else:
					try:
						copy(os.path.join(BASE_DIR,'Libs','Data','SEMPQ.exe'), file)
						h = MpqOpenArchiveForUpdate(file, MOAU_OPEN_ALWAYS | MOAU_MAINTAIN_LISTFILE)
					except:
						h = -1
			else:
				h = MpqOpenArchiveForUpdate(file, MOAU_OPEN_ALWAYS | MOAU_MAINTAIN_LISTFILE)
			if h == -1:
				ErrorDialog(self, PyMSError('Saving','Could not open %sMPQ "%s".)' % (['','SE'][file.endswith('%sexe)' % os.extsep)],file)))
				return
			ai = SFile()
			bw = SFile()
			try:
				self.ai.compile(ai, bw, self.extrainfo.get())
			except PyMSError as e:
				ErrorDialog(self, e)
			undone = []
			for f,s in [('ai',ai),('bw',bw)]:
				try:
					MpqAddFileFromBuffer(h, s.text, 'scripts\\%sscript.bin)' % f, MAFA_COMPRESS | MAFA_REPLACE_EXISTING)
				except:
					undone.append('scripts\\%sscript.bin)' % f)
			MpqCloseUpdatedArchive(h)
			if undone:
				askquestion(parent=self, title='Save problems', message='%s could not be saved to the MPQ.)' % ' and '.join(undone), type=OK)

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		if not self.unsaved():
			self.ai = None
			self.strings = {}
			self.aiscript = None
			self.bwscript = None
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.undos = []
			self.redos = []
			self.title('No files loaded')
			self.status.set('Load your files or create new ones.')
			self.listbox.delete(0, END)
			self.action_states()
			self.scriptstatus.set('')

	def register(self, e=None):
		try:
			register_registry('PyAI','AI','bin',os.path.join(BASE_DIR, 'PyAI.pyw'),os.path.join(BASE_DIR,'Images','PyAI.ico'))
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s)' % os.path.join(BASE_DIR, 'Docs', 'PyAI.html'))

	def about(self):
		thanks = [
			('bajadulce',"Testing, support, and hosting! I can't thank you enough!"),
			('ashara','Lots of help with beta testing and ideas'),
			('MamiyaOtaru','Found lots of bugs, most importantly ones on Mac and Linux.'),
			('Heinerman','File specs and command information'),
			('modmaster50','Lots of ideas, testing, and support, thanks a lot!')
		]
		AboutDialog(self, 'PyAI', LONG_VERSION, thanks)

	def exit(self, e=None):
		if not self.unsaved():
			savesize(self, self.settings)
			self.settings['stat_txt'] = self.stat_txt
			self.settings['highlights'] = self.highlights
			self.settings['reference'] = self.reference.get()
			self.settings['extrainfo'] = self.extrainfo.get()
			self.settings['imports'] = self.imports
			self.settings['extdefs'] = self.extdefs
			try:
				f = file(os.path.join(BASE_DIR,'Settings','PyAI.txt'),'w')
				f.write(pprint(self.settings))
				f.close()
			except:
				pass
			self.destroy()

	def order(self, key=None):
		if self.ai:
			sel = []
			if self.listbox.size():
				for index in self.listbox.curselection():
					try:
						sel.append(self.get_entry(index)[0])
					except:
						pass
				self.listbox.delete(0, END)
			for id,ai in self.ai.ais.items():
				self.set_entry(END, id, not ai[0], AIBIN.convflags(ai[2]), ai[1])
				if sel and id in sel:
					self.listbox.select_set(END)
			if not sel:
				self.listbox.select_set(0)

	def idsort(self, key=None):
		if self.ai:
			sel = []
			if self.listbox.size():
				for index in self.listbox.curselection():
					try:
						sel.append(self.get_entry(index)[0])
					except:
						pass
				self.listbox.delete(0, END)
			ais = list(self.ai.ais.keynames)
			ais.sort()
			for id in ais:
				ai = self.ai.ais[id]
				self.set_entry(END, id, not ai[0], AIBIN.convflags(ai[2]), ai[1])
				if sel and id in sel:
					self.listbox.select_set(END)
					self.listbox.see(END)
			if not sel:
				self.listbox.select_set(0)

	def bwsort(self, key=None):
		if self.ai:
			sel = []
			if self.listbox.size():
				for index in self.listbox.curselection():
					try:
						sel.append(self.get_entry(index)[0])
					except:
						pass
				self.listbox.delete(0, END)
			ais = []
			for id,ai in self.ai.ais.items():
				ais.append('%s %s)' % (ai[0], id))
			ais.sort()
			for a in ais:
				id = a.split(' ',1)[1]
				ai = self.ai.ais[id]
				self.set_entry(END, id, not ai[0], AIBIN.convflags(ai[2]), ai[1])
				if sel and id in sel:
					self.listbox.select_set(END)
			if not sel:
				self.listbox.select_set(0)

	def flagsort(self, key=None):
		if self.ai:
			sel = []
			if self.listbox.size():
				for index in self.listbox.curselection():
					try:
						sel.append(self.get_entry(index)[0])
					except:
						pass
				self.listbox.delete(0, END)
			ais = []
			for id,ai in self.ai.ais.items():
				ais.append('%s %s)' % (AIBIN.convflags(ai[2]), id))
			ais.sort()
			ais.reverse()
			for a in ais:
				id = a.split(' ',1)[1]
				ai = self.ai.ais[id]
				self.set_entry(END, id, not ai[0], AIBIN.convflags(ai[2]), ai[1])
				if sel and id in sel:
					self.listbox.select_set(END)
			if not sel:
				self.listbox.select_set(0)

	def stringsort(self, key=None):
		if self.ai:
			sel = []
			if self.listbox.size():
				for index in self.listbox.curselection():
					try:
						sel.append(self.get_entry(index)[0])
					except:
						pass
				self.listbox.delete(0, END)
			ais = []
			for id,ai in self.ai.ais.items():
				ais.append('%s\x00%s)' % (TBL.decompile_string(self.ai.tbl.strings[ai[1]]), id))
			ais.sort()
			for a in ais:
				id = a.split('\x00')[-1]
				ai = self.ai.ais[id]
				self.set_entry(END, id, not ai[0], AIBIN.convflags(ai[2]), ai[1])
				if sel and id in sel:
					self.listbox.select_set(END)
			if not sel:
				self.listbox.select_set(0)

	def undo(self, key=None):
		if key and self.buttons['undo']['state'] != NORMAL:
			return
		max = self.settings.get('redohistory', 10)
		undo = self.undos.pop()
		if max:
			if not self.redos:
				self.buttons['redo']['state'] = NORMAL
				self.menus['Edit'].entryconfig(1, state=NORMAL)
			self.redos.append(undo)
			if len(self.redos) > max:
				del self.redos[0]
		if not self.undos:
			self.buttons['undo']['state'] = DISABLED
			self.menus['Edit'].entryconfig(0, state=DISABLED)
			self.edited = False
			self.editstatus['state'] = DISABLED
		if undo[0] == 'remove':
			start = self.listbox.size()
			for id,ai,bw,info,s in undo[1]:
				self.ai.ais[id] = ai
				if bw:
					self.ai.bwscript.ais[id] = ai
					self.ai.bwscript.aisizes[id] = s
				else:
					self.ai.aisizes[id] = s
				if info:
					self.ai.aiinfo[id] = info
				if not ai[1] in self.strings:
					self.strings[ai[1]] = []
				if id not in self.strings[ai[1]]:
					self.strings[ai[1]].append(id)
				self.set_entry(END, id, not ai[0], AIBIN.convflags(ai[2]), ai[1])
			self.listbox.select_clear(0, END)
			self.listbox.select_set(start, END)
			self.listbox.see(start)
			self.action_states()
			s = 'aiscript.bin: %s (%s B) )' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
			if self.ai.bwscript:
				s += '     bwscript.bin: %s (%s B))' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
			self.scriptstatus.set(s)
		elif undo[0] == 'add':
			id = undo[1][0]
			del self.ai.ais[id]
			del self.ai.aisizes[id]
			if id in self.ai.aiinfo:
				del self.ai.aiinfo[id]
			self.strings[undo[1][1][1]].remove(id)
			if not self.strings[undo[1][1][1]]:
				del self.strings[undo[1][1][1]]
			self.resort()
			self.action_states()
			s = 'aiscript.bin: %s (%s B) )' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
			if self.ai.bwscript:
				s += '     bwscript.bin: %s (%s B))' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
			self.scriptstatus.set(s)
		elif undo[0] == 'edit':
			oldid,id,oldflags,flags,oldstrid,strid,oldaiinfo,aiinfo = undo[1]
			if oldid != id:
				self.ai.ais[oldid] = self.ai.ais[id]
				if not self.ai.ais[id][0]:
					self.ai.bwscript.ais[old] = self.ai.bwscript.ais[id]
					del self.ai.bwscript.ais[id]
				del self.ai.ais[id]
				if id in self.ai.aiinfo:
					self.ai.aiinfo[oldid] = self.ai.aiinfo[id]
					del self.ai.aiinfo[id]
				id = oldid
			self.ai.ais[id][1] = oldstrid
			self.ai.ais[id][2] = oldflags
			if oldaiinfo != aiinfo:
				if not id in self.ai.aiinfo:
					self.ai.aiinfo[id] = ['',odict(),[]]
				self.ai.aiinfo[id][0] = oldaiinfo
			self.resort()
		elif undo[0] == 'flags':
			self.ai.ais[undo[1][0]][2] = undo[1][1]
			self.resort()

	def redo(self, key=None):
		if key and self.buttons['redo']['state'] != NORMAL:
			return
		self.edited = True
		self.editstatus['state'] = NORMAL
		max = self.settings.get('undohistory', 10)
		redo = self.redos.pop()
		if max:
			if not self.undos:
				self.buttons['undo']['state'] = NORMAL
				self.menus['Edit'].entryconfig(0, state=NORMAL)
			self.undos.append(redo)
			if len(self.undos) > max:
				del self.undos[0]
		if not self.redos:
			self.buttons['redo']['state'] = DISABLED
			self.menus['Edit'].entryconfig(1, state=DISABLED)
		if redo[0] == 'remove':
			for id,ai,bw,info,s in redo[1]:
				del self.ai.ais[id]
				if bw:
					del self.ai.bwscript.ais[id]
					del self.ai.bwscript.aisizes[id]
				else:
					del self.ai.aisizes[id]
				if id in self.ai.aiinfo:
					del self.ai.aiinfo[id]
				self.strings[ai[1]].remove(id)
				if not self.strings[ai[1]]:
					del self.strings[ai[1]]
			self.resort()
			self.action_states()
			s = 'aiscript.bin: %s (%s B) )' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
			if self.ai.bwscript:
				s += '     bwscript.bin: %s (%s B))' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
			self.scriptstatus.set(s)
		elif redo[0] == 'add':
			id = redo[1][0]
			ai = redo[1][1]
			self.ai.ais[id] = ai
			self.ai.aisizes[id] = 1
			if redo[1][2]:
				self.ai.aiinfo = [redo[1][2],odict(),[]]
			if not ai[1] in self.strings:
				self.strings[ai[1]] = []
			if id not in self.strings[ai[1]]:
				self.strings[ai[1]].append(id)
			self.resort()
			self.action_states()
			s = 'aiscript.bin: %s (%s B) )' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
			if self.ai.bwscript:
				s += '     bwscript.bin: %s (%s B))' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
			self.scriptstatus.set(s)
		elif redo[0] == 'edit':
			id,oldid,flags,oldflags,strid,oldstrid,aiinfo,oldaiinfo = redo[1]
			if oldid != id:
				self.ai.ais[oldid] = self.ai.ais[id]
				if not self.ai.ais[id][0]:
					self.ai.bwscript.ais[old] = self.ai.bwscript.ais[id]
					del self.ai.bwscript.ais[id]
				del self.ai.ais[id]
				if id in self.ai.aiinfo:
					self.ai.aiinfo[oldid] = self.ai.aiinfo[id]
					del self.ai.aiinfo[id]
				id = oldid
			self.ai.ais[id][1] = oldstrid
			self.ai.ais[id][2] = oldflags
			if oldaiinfo != aiinfo:
				if not id in self.ai.aiinfo:
					self.ai.aiinfo[id] = ['',odict(),[]]
				self.ai.aiinfo[id][0] = oldaiinfo
			self.resort()
		elif redo[0] == 'flags':
			self.ai.ais[redo[1][0]][2] = redo[1][2]
			self.resort()

	def select_all(self, key=None):
		self.listbox.select_set(0, END)

	def add(self, key=None):
		if key and self.buttons['add']['state'] != NORMAL:
			return
		s = 2+sum(self.ai.aisizes.values())
		if s > 65535:
			ErrorDialog(PyMSError('Adding',"There is not enough room in your aiscript.bin to add a new script"))
			return
		e = EditScriptDialog(self, title='Adding New AI Script')
		id = e.id.get()
		if id:
			ai = [1,int(e.string.get()),e.flags,[[36]],[]]
			self.ai.ais[id] = ai
			self.ai.aisizes[id] = 1
			if e.aiinfo:
				if not id in self.ai.aiinfo:
					self.ai.aiinfo[id] = ['',odict(),[]]
				self.ai.aiinfo[id][0] = e.aiinfo
			if not ai[1] in self.strings:
				self.strings[ai[1]] = []
			if id not in self.strings[ai[1]]:
				self.strings[ai[1]].append(id)
			self.set_entry(END, id, False, '000', ai[1])
			self.listbox.select_clear(0, END)
			self.listbox.select_set(END)
			self.resort()
			self.listbox.see(self.listbox.curselection()[0])
			self.action_states()
			self.edited = True
			self.editstatus['state'] = NORMAL
			self.add_undo('add', [id, ai, e.aiinfo])
			s = 'aiscript.bin: %s (%s B) )' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
			if self.ai.bwscript:
				s += '     bwscript.bin: %s (%s B))' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
				self.scriptstatus.set(s)

	def remove(self, key=None):
		if key and self.buttons['remove']['state'] != NORMAL:
			return
		indexs = self.listbox.curselection()
		ids = []
		cantremove = {}
		for index in indexs:
			external = []
			e = self.get_entry(index)
			if e[0] in self.ai.externaljumps[e[1]][0]:
				for d in self.ai.externaljumps[e[1]][0][e[0]].items():
					for id in d[1]:
						if not id in external:
							external.append(id)
			if external:
				cantremove[e[0]] = external
			else:
				ids.append(index)
		if cantremove:
			more = len(cantremove) != len(indexs)
			t = '\n'.join(['\t%s referenced by: %s)' % (id,', '.join(refs)) for id,refs in cantremove.items()])
			cont = askquestion(parent=self, title='Removing', message="These scripts can not be removed because they are referenced by other scripts:\n%s%s)" % (t,['','\n\nContinue removing the other scripts?'][more]), default=[None,YES][more], type=[OK,YESNOCANCEL][more])
		undo = []
		n = 0
		for index in ids:
			index = int(index) - n
			item = self.get_entry(index)
			id = item[0]
			ai = self.ai.ais[id]
			del self.ai.ais[id]
			bw = None
			if item[1]:
				bw = self.ai.bwscript.ais[id]
				del self.ai.bwscript.ais[id]
				s = self.ai.bwscript.aisizes[id]
				del self.ai.bwscript.aisizes[id]
			else:
				s = self.ai.aisizes[id]
				del self.ai.aisizes[id]
			if item[0] in self.ai.aiinfo:
				del self.ai.aiinfo[id]
			self.strings[ai[1]].remove(id)
			if not self.strings[ai[1]]:
				del self.strings[ai[1]]
			undo.append((item[0], ai, bw, self.ai.aiinfo.get(item[0]), s))
			self.listbox.delete(index)
			n += 1
		if self.listbox.size():
			if indexs[0] != '0':
				self.listbox.select_set(int(indexs[0])-1)
			else:
				self.listbox.select_set(0)
		self.action_states()
		self.edited = True
		self.editstatus['state'] = NORMAL
		self.add_undo('remove', undo)
		s = 'aiscript.bin: %s (%s B) )' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
		if self.ai.bwscript:
			s += '     bwscript.bin: %s (%s B))' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
		self.scriptstatus.set(s)

	def find(self, key=None):
		if key and self.buttons['find']['state'] != NORMAL:
			return
		FindDialog(self)

	def export(self, key=None):
		if key and self.buttons['export']['state'] != NORMAL:
			return
		export = self.select_file('Export To', False, '.txt', [('Text Files','*.txt'),('All Files','*')])
		if export:
			indexs = self.listbox.curselection()
			external = []
			ids = []
			for index in indexs:
				e = self.get_entry(index)
				ids.append(e[0])
				if ids[-1] in self.ai.externaljumps[e[1]][1]:
					for id in self.ai.externaljumps[e[1]][1][ids[-1]]:
						if not id in external:
							external.append(id)
			if external:
				for i in ids:
					if i in external:
						external.remove(i)
				if external:
					ids.extend(external)
			try:
				warnings = self.ai.decompile(export, self.extdefs, self.reference.get(), 1, ids)
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			if warnings:
				WarningDialog(self, warnings)
			if external:
				askquestion(parent=self, title='External References', message='One or more of the scripts you are exporting references an external block, so the scripts that are referenced have been exported as well:\n    %s)' % '\n    '.join(external), type=OK)

	def iimport(self, key=None, iimport=None, c=True, parent=None, extra=None):
		if key and self.buttons['import']['state'] != NORMAL:
			return
		if parent == None:
			parent = self
		if extra == None:
			extra = self.extrainfo.get()
		if not iimport:
			iimport = self.select_file('Import From', True, '.txt', [('Text Files','*.txt'),('All Files','*')], parent)
		if iimport:
			i = AIBIN.AIBIN(False, self.unitsdat, self.upgradesdat, self.techdat, self.stat_txt)
			i.bwscript = AIBIN.BWBIN(self.unitsdat, self.upgradesdat, self.techdat, self.stat_txt)
			try:
				warnings = i.interpret(iimport, self.extdefs, extra)
				for id in i.ais.keys():
					if id in self.ai.externaljumps[0]:
						for o,l in self.ai.externaljumps[0]:
							for cid in l:
								if not cid in i.ais:
									raise PyMSError('Interpreting',"You can't edit scripts (%s) that are referenced externally with out editing the scripts with the external references (%s) at the same time.)" % (id,cid))
			except PyMSError as e:
				ErrorDialog(parent, e)
				return -1
			cont = c
			if warnings:
				w = WarningDialog(parent, warnings, True)
				cont = w.cont
			if cont:
				for id,ai in i.ais.items():
					if id in self.ai.ais and (cont == True or cont != 2):
						x = ContinueImportDialog(parent, id)
						cont = x.cont
						if not cont:
							continue
						elif cont == 3:
							break
					self.ai.ais[id] = ai
					if not ai[0]:
						self.ai.bwscript.ais[id] = i.bwscript.ais[id]
					for a,b in ((0,0),(0,1),(1,0),(1,1)):
						if id in i.externaljumps[a][b]:
							self.ai.externaljumps[a][b][id] = i.externaljumps[a][b][id]
						elif id in self.ai.externaljumps[a][b]:
							del self.ai.externaljumps[a][b][id]
					if id in i.aiinfo:
						self.ai.aiinfo[id] = i.aiinfo[id]
					elif id in self.ai.aiinfo:
						del self.ai.aiinfo[id]
					if id in i.bwscript.aiinfo:
						self.ai.bwscript.aiinfo[id] = i.bwscript.aiinfo[id]
					elif id in self.ai.bwscript.aiinfo:
						del self.ai.bwscript.aiinfo[id]
					if not ai[1] in self.strings:
						self.strings[ai[1]] = []
					if id not in self.strings[ai[1]]:
						self.strings[ai[1]].append(id)
					self.resort()
			s = 'aiscript.bin: %s (%s B) )' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
			if self.ai.bwscript:
				s += '     bwscript.bin: %s (%s B))' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
			self.scriptstatus.set(s)
			self.action_states()
			self.edited = True
			self.editstatus['state'] = NORMAL
			return cont

	def listimport(self, key=None):
		if key and self.buttons['listimport']['state'] != NORMAL:
			return
		ImportListDialog(self)

	def codeedit(self, key=None):
		if key and self.buttons['codeedit']['state'] != NORMAL:
			return
		indexs = self.listbox.curselection()
		external = []
		ids = []
		for index in indexs:
			e = self.get_entry(index)
			ids.append(e[0])
			if ids[-1] in self.ai.externaljumps[e[1]][1]:
				for id in self.ai.externaljumps[e[1]][1][ids[-1]]:
					if not id in external:
						external.append(id)
		if external:
			for i in external:
				if not i in ids:
					ids.append(i)
		CodeEditDialog(self, ids)

	def edit(self, key=None):
		if key and self.buttons['edit']['state'] != NORMAL:
			return
		id = self.get_entry(self.listbox.curselection()[0])[0]
		aiinfo = ''
		if id in self.ai.aiinfo:
			aiinfo = self.ai.aiinfo[id][0]
		e = EditScriptDialog(self, id, self.ai.ais[id][2], self.ai.ais[id][1], aiinfo, initial=id)
		if e.id.get():
			undo = (id,e.id.get(),self.ai.ais[id][2],e.flags,self.ai.ais[id][1],int(e.string.get()),aiinfo,e.aiinfo)
			if e.id.get() != id:
				self.ai.ais[e.id.get()] = self.ai.ais[id]
				if not self.ai.ais[id][0]:
					self.ai.bwscript.ais[e.id.get()] = self.ai.bwscript.ais[id]
					del self.ai.bwscript.ais[id]
				del self.ai.ais[id]
				if id in self.ai.aiinfo:
					self.ai.aiinfo[e.id.get()] = self.ai.aiinfo[id]
					del self.ai.aiinfo[id]
				id = e.id.get()
			self.ai.ais[id][1] = int(e.string.get())
			self.ai.ais[id][2] = e.flags
			if e.aiinfo != aiinfo:
				if not id in self.ai.aiinfo:
					self.ai.aiinfo[id] = ['',odict(),[]]
				self.ai.aiinfo[id][0] = e.aiinfo
			self.add_undo('edit', undo)
			self.resort()

	def editflags(self, key=None):
		if key and self.buttons['flags']['state'] != NORMAL:
			return
		id = self.get_entry(self.listbox.curselection()[0])[0]
		f = FlagEditor(self, self.ai.ais[id][2])
		if f.flags != None:
			self.add_undo('flags', [id,self.ai.ais[id][2],f.flags])
			self.ai.ais[id][2] = f.flags
			self.resort()
			self.edited = True
			self.editstatus['state'] = NORMAL

	def extdef(self, key=None):
		if key and self.buttons['extdef']['state'] != NORMAL:
			return
		ExternalDefDialog(self)

	def managetbl(self, key=None):
		i = 0
		if self.listbox.size():
			i = self.get_entry(self.listbox.curselection()[0])[3]
		StringEditor(self, index=i)

	def managedat(self, key=None, err=None):
		data = [
			('DAT  Settings',[
				('units.dat', 'Used to check if a unit is a Building or has Air/Ground attacks', 'unitsdat', 'UnitsDAT'),
				('upgrades.dat', 'Used to specify upgrade string entries in stat_txt.tbl', 'upgradesdat', 'UpgradesDAT'),
				('techdata.dat', 'Used to specify technology string entries in stat_txt.tbl', 'techdatadat', 'TechDAT')
			])
		]
		SettingsDialog(self, data, (340,295), err)

	def openset(self, key=None):
		file = self.select_file('Load Settings', True, '.txt', [('Text Files','*.txt'),('All Files','*')])
		if file:
			try:
				files = open(file,'r').readlines()
			except:
				showerror('Invalid File',"Could not open '%s'.)" % file)
			sets = [
				TBL.TBL(),
				DAT.UnitsDAT(),
				DAT.UpgradesDAT(),
				DAT.TechDAT(),
			]
			for n,s in enumerate(sets):
				try:
					s.load_file(files[n] % {'path':BASE_DIR})
				except PyMSError as e:
					ErrorDialog(self, e)
					return
			self.tbl = sets[0]
			self.stat_txt = files[0]
			self.units = sets[1]
			self.unitsdat = files[1]
			self.upgrades = sets[2]
			self.upgradesdat = files[2]
			self.tech = sets[3]
			self.techdat = files[3]

	def saveset(self, key=None):
		file = self.select_file('Save Settings', False, '.txt', [('Text Files','*.txt'),('All Files','*')])
		if file:
			try:
				set = open(file,'w')
			except:
				showerror('Invalid File',"Could not save to '%s'.)" % file)
			set.write(('%s\n%s\n%s\n%s)' % (self.stat_txt, self.settings['self.unitsdat'], self.settings['self.upgradesdat'], self.settings['self.techdat'])).replace(BASE_DIR, '%(path)s'))
			set.close()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pyai.py','pyai.pyw','pyai.exe']):
		gui = PyAI()
		gui.mainloop()
	else:
		p = optparse.OptionParser(usage='usage: PyAI [options] <inp|aiscriptin bwscriptin> [out|aiscriptout bwscriptout]', version='PyAI %s)' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile AI's from aiscript.bin and/or bwscript.bin [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile AI's to an aiscript.bin and/or bwscript.bin")
		p.add_option('-e', '--extrainfo', action='store_true', help="Save extra info from your script (variables, label names, and information comments) [default: Off]", default=False)
		p.add_option('-u', '--units', help="Specify your own units.dat file for unit data lookups [default: Libs\\MPQ\\arr\\units.dat]", default=os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr', 'units.dat'))
		p.add_option('-g', '--upgrades', help="Specify your own upgrades.dat file for upgrade data lookups [default: Libs\\MPQ\\arr\\upgrades.dat]", default=os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr', 'upgrades.dat'))
		p.add_option('-t', '--techdata', help="Specify your own techdata.dat file for technology data lookups [default: Libs\\MPQ\\arr\\techdata.dat]", default=os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr', 'techdata.dat'))
		p.add_option('-s', '--scripts', help="A list of AI Script ID's to decompile (seperated by commas) [default: All]", default='')
		p.add_option('-a', '--aiscript', help="Used to signify the base aiscript.bin file to compile on top of", default='')
		p.add_option('-b', '--bwscript', help="Used to signify the base bwscript.bin file to compile on top of", default='')
		p.add_option('-m', '--mpq', help="Used to signify mpq to add scripts to", default='')
		p.add_option('-l', '--longlabels', action='store_false', help="Used to signify that you want decompiled scripts to use desriptive command names [default: Off]", default=True)
		p.add_option('-x', '--stattxt', help="Used to signify the stat_txt.tbl file to use [default: Libs\\MPQ\\rez\\stat_txt.tbl]", default=os.path.join(BASE_DIR, 'Libs', 'MPQ', 'rez', 'stat_txt.tbl'))
		p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for commands and parameters [default: Off]", default=False)
		p.add_option('-w', '--hidewarns', action='store_true', help="Hides any warning produced by compiling your code [default: Off]", default=False)
		p.add_option('-f', '--deffile', help="Specify an External Definition file containing variables to be used when interpreting/decompiling [default: None]", default=None)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyAI(opt.gui)
			gui.mainloop()
		else:
			if not len(args) in [2,3]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			if len(args) != 3:
				if opt.convert:
					if len(args) < 2:
						p.error('Invalid amount of arguments, missing bwscript.bin')
					args.append('%s%s%s)' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, 'txt'))
				else:
					if len(args) < 2:
						args.append('%s%s%s)' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, 'bin'))
					args.append('%s%s%s)' % (os.path.join(path,'bw' + os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, 'bin'))
			warnings = []
			try:
				if opt.convert:
					if opt.scripts:
						ids = []
						for i in opt.scripts.split(','):
							if len(i) != 4:
								print('Invalid ID: %s' % ids[-1])
								return
							ids.append(i)
					else:
						ids = None
					print("Loading bwscript.bin '%s', units.dat '%s', upgrades.dat '%s', techdata.dat '%s', and stat_txt.tbl '%s'" % (args[1],opt.units,opt.upgrades,opt.techdata,opt.stattxt))
					bin = AIBIN.AIBIN(args[1],opt.units,opt.upgrades,opt.techdata,opt.stattxt)
					warnings.extend(bin.warnings)
					print(" - Loading finished successfully\nReading BINs '%s' and '%s'..." % (args[0],args[1]))
					warnings.extend(bin.load_file(args[0]))
					print(" - BINs read successfully\nWriting AI Scripts to '%s'..." % args[2])
					warnings.extend(bin.decompile(args[2],opt.deffile,opt.reference,opt.longlabels,ids))
					print(" - '%s' written succesfully" % args[2])
				else:
					if opt.bwscript:
						print("Loading base bwscript.bin '%s', units.dat '%s', upgrades.dat '%s', techdata.dat '%s', and stat_txt.tbl '%s'" % (os.path.abspath(opt.bwscript),opt.units,opt.upgrades,opt.techdata,opt.stattxt))
						bin = AIBIN.AIBIN(os.path.abspath(opt.bwscript),opt.units,opt.upgrades,opt.techdata,opt.stattxt)
					else:
						bin = AIBIN.AIBIN('',opt.units,opt.upgrades,opt.techdata,opt.stattxt)
					if opt.aiscript:
						print("Loading base aiscript.bin '%s'..." % os.path.abspath(opt.aiscript))
						bin.load_file(os.path.abspath(opt.aiscript))
					print("Interpreting file '%s'..." % args[0])
					warnings.extend(bin.interpret(args[0],opt.deffile))
					print("Compiling to '%s' and '%s'..." % (args[1], args[2]))
					bin.compile(args[1], args[2], opt.extrainfo)
					if(opt.mpq):
						print("Saving to " + opt.mpq)
						h = MpqOpenArchiveForUpdate(opt.mpq, MOAU_OPEN_ALWAYS | MOAU_MAINTAIN_LISTFILE)
						MpqAddFileToArchive(h, args[1], 'scripts\\aiscript.bin', MAFA_COMPRESS | MAFA_REPLACE_EXISTING)
						MpqAddFileToArchive(h, args[2], 'scripts\\bwscript.bin', MAFA_COMPRESS | MAFA_REPLACE_EXISTING)
						MpqCloseUpdatedArchive(h)
				if not opt.hidewarns:
					for warning in warnings:
						print(repr(warning))
			except PyMSError as e:
				if warnings and not opt.hidewarns:
					for warning in warnings:
						print(repr(warning))
				print(repr(e))

if __name__ == '__main__':
	main()