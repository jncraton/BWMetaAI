from utils import *
import TBL,DAT

import struct, re, os
try:
	from cPickle import *
except ImportError:
	from pickle import *
from zlib import compress, decompress

# import sys
# sys.stdout = open('stdieo.txt','w')

TYPE_HELP = {
	'Frame':'The index of a frame in a GRP, in decimal or hexadecimal (number in the range 0 to 65535. framesets are increments of 17, so 17 or 0x11, 34 or 0x22, 51 or 0x33, etc.)',
	'Byte':'A number in the range 0 to 255',
	'SByte':'A number in the range -128 to 127',
	'Label':'A label name of a block in the script',
	'ImageID':'The ID of an images.dat entry',
	'SpriteID':'The ID of a sprites.dat entry',
	'FlingyID':'The ID of a flingy.dat entry',
	'OverlayID':'The ID of an overlay',
	'FlipState':'The flip state to set on the current image overlay',
	'SoundID':'The ID of a sfxdata.dat entry',
	'Sounds':'How many sounds to pick from',
	'SignalID':'A signal order ID',
	'Weapon':'Either 1 for ground attack, or not 1 for air attack',
	'WeaponID':'The ID of a weapons.dat entry',
	'Speed':'The speed to set on the flingy.dat entry of the current flingy',
	'GasOverlay':'The ID of a gas overlay',
	'Short':'A number in the range 0 to 65535',
}
HEADER_HELP = [
	'Initial animation',
	'Death animation',
	'Initial ground attack animation',
	'Initial air attack animation',
	'Unknown/unused animation',
	'Repeated ground attack animation',
	'Repeated air attack animation',
	'Spell casting animation',
	'Animation for returning to an idle state after a ground attack',
	'Animation for returning to an idle state after an air attack',
	'Unknown/unused animation',
	'Walking/moving animation',
	'Animation for returning to an idle state after walking/moving',
	'Some sort of category of special animations, in some cases an in-transit animation, sometimes used for special orders, sometimes having to do with the animation when something finishes morphing, or the first stage of a construction animation',
	'Some sort of category of special animations, in some cases a burrowed animation, sometimes used for special orders, sometimes having to do with the animation when canceling a morph, or the second stage of a construction animation',
	'An animation for one part of the building process',
	'Final animation before finishing being built',
	'Landing animation',
	'Lifting off animation',
	'Animation for when researching an upgrade/technology or training/building units and some other animations for some sort of work being done',
	'Animation for returning to an idle state after IsWorking',
	'Warping in animation',
	'Unknown/unused animation',
	'Previously called InitTurret, this is actually an alternate initial animation for StarEdit a.k.a. the Campaign Editor',
	'Animation for becoming disabled, either through the "Set Doodad State" trigger action or by not being in the psi field of any pylons',
	'Burrowing animation',
	'Unburrowing animation',
	'Animation for becoming enabled, either through the "Set Doodad State" trigger action or by being in the psi field of a pylon',
	'The iscript id of this animation set; it is referenced by images.dat, each set has a unique id',
	'This is the type of set; there are 28 different types, each with a different number of animations',
]
CMD_HELP = [
	'Display Frame(1), adjusted for direction.',
	'Display Frame(1) dependant on tileset.',
	'Set the horizontal offset of the current image overlay to Byte(1).',
	'Set the vertical position of an image overlay to Byte(1).',
	'Set the horizontal and vertical position of the current image overlay to Byte(1) and Byte(2) respectively.',
	'Pauses script execution for a Byte(1) number of ticks.',
	'Pauses script execution for a random number of ticks between Byte(1) and Byte(2).',
	'Unconditionally jumps to code block Label(1).',
	'Display ImageID(1) as an active image overlay at an animation level higher than the current image overlay at offset position (Byte(1),Byte(2)).',
	'Display ImageID(1) as an active image overlay at an animation level lower than the current image overlay at offset position (Byte(1),Byte(2)).',
	'Display ImageID(1) as an active image overlay at an animation level higher than the current image overlay at the relative origin offset position.',
	'Only for powerups, this is hypothesised to replace the image overlay that was first created by the current image overlay.', #WTF?
	'Unknown.',
	'Displays an active image overlay at an animation level higher than the current image overlay, using a LO* file to determine the offset position.', #WTF?
	'Displays an active image overlay at an animation level lower than the current image overlay, using a LO* file to determine the offset position.', #WTF?
	'Spawns SpriteID(1) one animation level above the current image overlay at offset position (Byte(1),Byte(2)).',
	'Spawns SpriteID(1) at the highest animation level at offset position (Byte(1),Byte(2)).',
	'spawns SpriteID(1) at the lowest animation level at offset position (Byte(1),Byte(2)).',
	'Create FlingyID(1) with restrictions; supposedly crashes in most cases.',
	'Spawns SpriteID(1) one animation level below the current image overlay at offset position (Byte(1),Byte(2)). The new sprite inherits the direction of the current sprite. Requires LO* file for unknown reason.',
	'Spawns SpriteID(1) one animation level below the current image overlay at offset position (Byte(1),Byte(2)). The new sprite inherits the direction of the current sprite.',
	'Spawns SpriteID(1) one animation level above the current image overlay, using a specified LO* file for the offset position information. The new sprite inherits the direction of the current sprite.', #WTF?
	'Destroys the current active image overlay, also removing the current sprite if the image overlay is the last in one in the current sprite.',
	'Sets the flip state of the current image overlay to FlipState(1).',
	'Plays SoundID(1).',
	"Plays a random sound from a list containing Sounds(1) number of SoundID(1)'s.",
	'Plays a random sound between SoundID(1) and SoundID(2) inclusively.',
	'Causes the damage of a weapon flingy to be applied according to its weapons.dat entry.',
	"Applies damage to target without creating a flingy and plays a random sound from a list containing Sounds(1) number of SoundID(1)'s..",
	'Causes the current image overlay to display the same frame as the parent image overlay.',
	'Randomly jump to Label(1) with a chance of Byte(1) out of 255.',
	'Turns the flingy counterclockwise by Byte(1) direction units.',
	'Turns the flingy clockwise by Byte(1) direction units.',
	'Turns the flingy clockwise by one direction unit.',
	'Turns the flingy by Byte(1) direction units in a random direction, with a heavy bias towards turning clockwise.',
	'in specific situations, performs a natural rotation to the direction Byte(1).',
	"Allows the current unit's order to proceed if it has paused for an animation to be completed.", #WTF?
	'Attack with either the ground or air weapon depending on Weapon(1).',
	'Attack with either the ground or air weapon depending on target.',
	"Identifies when a spell should be cast in a spellcasting animation. The spell is determined by the unit's current order.",
	'Makes the unit use WeaponID(1) on its target.',
	'Sets the unit to move forward Byte(1) pixels at the end of the current tick.',
	"Signals to StarCraft that after this point, when the unit's cooldown time is over, the repeat attack animation can be called.",
	'Plays Frame(1), often used in engine glow animations.',
	'Plays the frame set Frame(1), often used in engine glow animations.',
	'Hypothesised to hide the current image overlay until the next animation.',
	'Holds the processing of player orders until a nobrkcodeend is encountered.',
	'Allows the processing of player orders after a nobrkcodestart instruction.',
	'Conceptually, this causes the script to stop until the next animation is called.',
	'Creates the weapon flingy at a distance of Byte(1) in front of the unit.',
	'Sets the current image overlay state to hidden.',
	'Sets the current image overlay state to visible.',
	'Sets the current direction of the flingy to Byte(1).',
	'Calls the code block Label(1).',
	'Returns from call.',
	'Sets the flingy.dat speed of the current flingy to Short(1).',
	'Creates gas image overlay GasOverlay(1) at offsets specified by LO* files.',
	'Jumps to code block Label(1) if the current unit is a powerup and it is currently picked up.',
	'Jumps to code block Label(1) depending on the distance to the target.', #WTF?
	'Jumps to code block Label(1) depending on the current angle of the target.', #WTF?
	'Only for units. Jump to code block Label(1) if the current sprite is facing a particular direction.', #WTF?
	'Displays an active image overlay at the shadow animation level at a offset position (Byte(1),Byte(2)). The image overlay that will be displayed is the one that is after the current image overlay in images.dat.',
	'Unknown.',
	'Jumps to code block Label(1) when the current unit is a building that is lifted off.',
	"Hypothesised to display Frame(1) from the current image overlay clipped to the outline of the parent image overlay.",
	"Most likely used with orders that continually repeat, like the Medic's healing and the Valkyrie's afterburners (which no longer exist), to clear the sigorder flag to stop the order.", #WTF?
	'Spawns SpriteID(1) one animation level above the current image overlay at offset position (Byte(1),Byte(2)), but only if the current sprite is over ground-passable terrain.',
	'Unknown.',
	'Applies damage like domissiledmg when on ground-unit-passable terrain.',
]

#stages: 0 = size, 1 = decompile, 2 = interpret
def type_frame(stage, bin, data=None):
	"""Frame"""
	if data == None:
		return 2
	if stage == 1:
		if data % 17:
			return (str(data),'Frame set %s, direction %s' % (data/17,data%17))
		return ('0x' + hex(data)[2:].zfill(2),'Frame set %s' % (data/17))
	try:
		if data.startswith('0x'):
			v = int(data[2:], 16)
		else:
			v = int(data)
		if 0 > v or v > 65535:
			raise
		if bin and bin.grpframes and v > bin.grpframes:
			raise PyMSWarning('Parameter',"'%s' is an invalid frame for one or more of the GRP's specified in the header, and may cause a crash (max frame value is %s, or frameset 0x%02x)" % (data, bin.grpframes, (bin.grpframes - 17) / 17 * 17),extra=v)
		if bin and bin.grpframes and v > bin.grpframes - 17:
			raise PyMSWarning('Parameter',"'%s' is an invalid frameset for one or more of the GRP's specified in the header, and may cause a crash (max frame value is %s, or frameset 0x%02x)" % (data, bin.grpframes , (bin.grpframes - 17) / 17 * 17),extra=v)
	except PyMSWarning:
		raise
	except:
		raise PyMSError('Parameter',"Invalid Frame value '%s', it must be a number in the range 0 to 65535 in decimal or hexidecimal (framesets are increments of 17: 17 or 0x11, 34 or 0x22, 51 or 0x33, etc.)" % data)
	return v

def type_bframe(stage, bin, data=None):
	"""BFrame"""
	if data == None:
		return 1
	if stage == 1:
		return (str(data),'')
	try:
		v = int(data)
		if 0 > v or v > 255:
			raise
	except:
		raise PyMSError('Parameter',"Invalid BFrame value '%s', it must be a number in the range 0 to 256" % data)
	return v

def type_byte(stage, bin, data=None):
	"""Byte"""
	if data == None:
		return 1
	if stage == 1:
		return (str(data),'')
	try:
		v = int(data)
		if 0 > v or v > 255:
			raise
	except:
		raise PyMSError('Parameter',"Invalid Byte value '%s', it must be a number in the range 0 to 255" % data)
	return v

def type_sbyte(stage, bin, data=None):
	"""SByte"""
	if data == None:
		return 1
	if stage == 1:
		if data > 127:
			data = -(256 - data)
		return (str(data),'')
	try:
		v = int(data)
		if -128 > v or v > 127:
			raise
		if v < 0:
			v = 256 + v
	except:
		raise PyMSError('Parameter',"Invalid SByte value '%s', it must be a number in the range -128 to 127" % data)
	return v

def type_label(stage, bin):
	"""Label"""
	return 2

def type_imageid(stage, bin, data=None):
	"""ImageID"""
	if data == None:
		return 2
	if stage == 1:
		return (str(data),'%s (%s)' % (DAT.DATA_CACHE['Images.txt'][data], TBL.decompile_string(bin.imagestbl.strings[bin.imagesdat.get_value(data,'GRPFile')-1][:-1])))
	try:
		v = int(data)
		if 0 > v or v > DAT.ImagesDAT.count:
			raise
	except:
		raise PyMSError('Parameter',"Invalid ImageID value '%s', it must be a number in the range 0 to %s" % (data,DAT.ImagesDAT.count))
	return v

def type_spriteid(stage, bin, data=None):
	"""SpriteID"""
	if data == None:
		return 2
	if stage == 1:
		return (str(data),'%s (%s)' % (DAT.DATA_CACHE['Sprites.txt'][data], TBL.decompile_string(bin.imagestbl.strings[bin.imagesdat.get_value(bin.spritesdat.get_value(data,'ImageFile'),'GRPFile')-1][:-1])))
	try:
		v = int(data)
		if 0 > v or v > DAT.SpritesDAT.count:
			raise
	except:
		raise PyMSError('Parameter',"Invalid SpriteID value '%s', it must be a number in the range 0 to %s" % (data,DAT.SpritesDAT.count))
	return v

def type_flingy(stage, bin, data=None):
	"""FlingyID"""
	if data == None:
		return 2
	if stage == 1:
		return (str(data),'%s (%s)' % (DAT.DATA_CACHE['Flingy.txt'][data], TBL.decompile_string(bin.imagestbl.strings[bin.imagesdat.get_value(bin.spritesdat.get_value(bin.flingydat.get_value(data,'Sprite'),'ImageFile'),'GRPFile')-1][:-1])))
	try:
		v = int(data)
		if 0 > v or v > DAT.FlingyDAT.count:
			raise
	except:
		raise PyMSError('Parameter',"Invalid FlingyID value '%s', it must be a number in the range 0 to %s" % (data,DAT.FlingyDAT.count))
	return v

def type_overlayid(stage, bin, data=None):
	"""OverlayID"""
	if data == None:
		return 1
	if stage == 1:
		return (str(data),'')
	try:
		v = int(data)
		if 0 > v or v > 255:
			raise
	except:
		raise PyMSError('Parameter',"Invalid OverlayID value '%s', it must be a number in the range 0 to 255" % data)
	return v # Restrictions?
	# /"Overlay 1" renamed to "Attack"
	# /"Overlay 2" renamed to "HP Damage"
	# /"Overlay 3" renamed to "Special"
	# /"Overlay 4" renamed to "Landing Dust"
	# /"Overlay 5" renamed to "Lift-off Dust"

def type_flipstate(stage, bin, data=None):
	"""FlipState"""
	if data == None:
		return 1
	if stage == 1:
		return (str(data),'')
	try:
		v = int(data)
		if 0 > v or v > 255:
			raise
	except:
		raise PyMSError('Parameter',"Invalid FlipState value '%s', it must be a number in the range 0 to 255" % data)
	return v

def type_soundid(stage, bin, data=None):
	"""SoundID"""
	if data == None:
		return 2
	if stage == 1:
		return (str(data), TBL.decompile_string(bin.sfxdatatbl.strings[bin.soundsdat.get_value(data,'SoundFile')-1][:-1]))
	try:
		v = int(data)
		if 0 > v or v > DAT.SoundsDAT.count:
			raise
	except:
		raise PyMSError('Parameter',"Invalid SoundID value '%s', it must be a number in the range 0 to %s" % (data,DAT.SoundsDAT.count))
	return v

def type_sounds(stage, bin, data=None):
	"""Sounds"""
	if data == None:
		return -1
	if stage == 1:
		return (str(data),'')
	try:
		v = int(data)
		if 0 > v or v > 255:
			raise
	except:
		raise PyMSError('Parameter',"Invalid Sounds value '%s', it must be a number in the range 0 to 255" % data)
	return v

def type_signalid(stage, bin, data=None):
	"""SignalID"""
	if data == None:
		return 1
	if stage == 1:
		return (str(data),'')
	try:
		v = int(data)
		if 0 > v or v > 255:
			raise
	except:
		raise PyMSError('Parameter',"Invalid SignalID value '%s', it must be a number in the range 0 to 255" % data)
	return v

def type_weapon(stage, bin, data=None):
	"""Weapon"""
	if data == None:
		return 1
	if stage == 1:
		return (str(data),'')
	try:
		v = int(data)
		if 0 > v or v > 255:
			raise
	except:
		raise PyMSError('Parameter',"Invalid Weapon value '%s', it must be 1 for ground attack or not 1 for air attack." % data)
	return v

def type_weaponid(stage, bin, data=None):
	"""WeaponID"""
	if data == None:
		return 1
	if stage == 1:
		return (str(data),'%s (%s)' % (DAT.DATA_CACHE['Weapons.txt'][data], TBL.decompile_string(bin.tbl.strings[bin.weaponsdat.get_value(data,'Label')-1][:-1])))
	try:
		v = int(data)
		if 0 > v or v > DAT.WeaponsDAT.count:
			raise
	except:
		raise PyMSError('Parameter',"Invalid WeaponID value '%s', it must be a number in the range 0 to %s" % (data,DAT.WeaponsDAT.count))
	return v

def type_speed(stage, bin, data=None):
	"""Speed"""
	if data == None:
		return 2
	if stage == 1:
		return (str(data),'')
	try:
		v = int(data)
		if 0 > v or v > 65535:
			raise
	except:
		raise PyMSError('Parameter',"Invalid Speed value '%s', it must be a number in the range 0 to 65535" % data)
	return v

def type_gasoverlay(stage, bin, data=None):
	"""GasOverlay"""
	if data == None:
		return 1
	if stage == 1:
		return (str(data),'')
	try:
		v = int(data)
		if 0 > v or v > 255:
			raise
	except:
		raise PyMSError('Parameter',"Invalid GasOverlay value '%s', it must be a number in the range 0 to 255" % data) # restrictions?
	return v

def type_short(stage, bin, data=None):
	"""Short"""
	if data == None:
		return 2
	if stage == 1:
		return (str(data),'')
	try:
		v = int(data)
		if 0 > v or v > 65535:
			raise
	except:
		raise PyMSError('Parameter',"Invalid Short value '%s', it must be a number in the range 0 to 65535" % data)
	return v

ENTRY_TYPES = {0:2,1:2,2:4,12:14,13:14,14:16,15:16,20:22,21:22,23:24,24:26,26:28,27:28,28:28,29:28}

HEADER = [
	('Init',),
	('Death',),
	('GndAttkInit',),
	('AirAttkInit',),
	('Unused1',),
	('GndAttkRpt',),
	('AirAttkRpt',),
	('CastSpell',),
	('GndAttkToIdle',),
	('AirAttkToIdle',),
	('Unused2',),
	('Walking',),
	('WalkingToIdle',),
	('SpecialState1',),
	('SpecialState2',),
	('AlmostBuilt',),
	('Built',),
	('Landing',),
	('LiftOff',),
	('IsWorking',),
	('WorkingToIdle',),
	('WarpIn',),
	('Unused3',),
	('StarEditInit',),
	('Disable',),
	('Burrow',),
	('UnBurrow',),
	('Enable',),
]

OPCODES = [
	[('playfram',), [type_frame]],               #0
	[('playframtile',), [type_frame]],
	[('sethorpos',), [type_sbyte]],
	[('setvertpos',), [type_sbyte]],
	[('setpos',), [type_sbyte,type_sbyte]],
	[('wait',), [type_byte]],
	[('waitrand',), [type_byte,type_byte]],
	[('goto',), [type_label]],                                 #7
	[('imgol',), [type_imageid,type_sbyte,type_sbyte]],
	[('imgul',), [type_imageid,type_sbyte,type_sbyte]],
	[('imgolorig',), [type_imageid]],
	[('switchul',), [type_imageid]],
	[('__0c',), []],
	[('imgoluselo',), [type_imageid,type_sbyte,type_sbyte]],
	[('imguluselo',), [type_imageid,type_sbyte,type_sbyte]],
	[('sprol',), [type_spriteid,type_sbyte,type_sbyte]],
	[('highsprol',), [type_spriteid,type_sbyte,type_sbyte]],
	[('lowsprul',), [type_spriteid,type_sbyte,type_sbyte]],
	[('uflunstable',), [type_flingy]],
	[('spruluselo',), [type_spriteid,type_sbyte,type_sbyte]],
	[('sprul',), [type_spriteid,type_sbyte,type_sbyte]],
	[('sproluselo',), [type_spriteid,type_overlayid]],
	[('end',), []],                     #22
	[('setflipstate',), [type_flipstate]],
	[('playsnd',), [type_soundid]],
	[('playsndrand',), [type_sounds,type_soundid]],
	[('playsndbtwn',), [type_soundid,type_soundid]],
	[('domissiledmg',), []],
	[('attackmelee',), [type_sounds,type_soundid]],
	[('followmaingraphic',), []],
	[('randcondjmp',), [type_byte,type_label]],         #30
	[('turnccwise',), [type_byte]],
	[('turncwise',), [type_byte]],
	[('turnlcwise',), []],
	[('turnrand',), [type_byte]],
	[('setspawnframe',), [type_byte]],
	[('sigorder',), [type_signalid]],
	[('attackwith',), [type_weapon]],
	[('attack',), []],
	[('castspell',), []],
	[('useweapon',), [type_weaponid]],
	[('move',), [type_byte]],
	[('gotorepeatattk',), []],
	[('engframe',), [type_bframe]],
	[('engset',), [type_frame]],
	[('__2d',), []],
	[('nobrkcodestart',), []],
	[('nobrkcodeend',), []],
	[('ignorerest',), []],
	[('attkshiftproj',), [type_byte]],
	[('tmprmgraphicstart',), []],
	[('tmprmgraphicend',), []],
	[('setfldirect',), [type_byte]],
	[('call',), [type_label]],                   #53
	[('return',), []],                  #54
	[('setflspeed',), [type_speed]],
	[('creategasoverlays',), [type_gasoverlay]],
	[('pwrupcondjmp',), [type_label]],           #57
	[('trgtrangecondjmp',), [type_short,type_label]],    #
	[('trgtarccondjmp',), [type_short,type_short,type_label]],   #
	[('curdirectcondjmp',), [type_short,type_short,type_label]], #
	[('imgulnextid',), [type_sbyte,type_sbyte]],
	[('__3e',), []],
	[('liftoffcondjmp',), [type_label]],
	[('warpoverlay',), [type_frame]],
	[('orderdone',), [type_signalid]],
	[('grdsprol',), [type_spriteid,type_sbyte,type_sbyte]],
	[('__43',), []],
	[('dogrddamage',), []],
]

REV_HEADER = {'IsId':-2,'Type':-1}
for h,n in enumerate(HEADER):
	for name in n:
		REV_HEADER[name] = h

REV_OPCODES = {}
for o,c in enumerate(OPCODES):
	for name in c[0]:
		REV_OPCODES[name] = o

class IScriptBIN:
	def __init__(self, weaponsdat=None, flingydat=None, imagesdat=None, spritesdat=None, soundsdat=None, stat_txt=None, imagestbl=None, sfxdatatbl=None):
		if weaponsdat == None:
			weaponsdat = os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr', 'weapons.dat')
		if flingydat == None:
			flingydat = os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr', 'flingy.dat')
		if imagesdat == None:
			imagesdat = os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr', 'images.dat')
		if spritesdat == None:
			spritesdat = os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr', 'sprites.dat')
		if soundsdat == None:
			soundsdat = os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr', 'sfxdata.dat')
		if stat_txt == None:
			stat_txt = os.path.join(BASE_DIR, 'Libs', 'MPQ', 'rez', 'stat_txt.tbl')
		if imagestbl == None:
			imagestbl = os.path.join(BASE_DIR, 'Libs', 'MPQ', 'rez', 'images.tbl')
		if sfxdatatbl == None:
			sfxdatatbl = os.path.join(BASE_DIR, 'Libs', 'MPQ', 'rez', 'sfxdata.tbl')
		self.headers = {}
		self.offsets = {}
		self.code = odict()
		self.extrainfo = {}
		if isinstance(stat_txt, TBL.TBL):
			self.tbl = stat_txt
		else:
			self.tbl = TBL.TBL()
			self.tbl.load_file(stat_txt)
		if isinstance(weaponsdat, DAT.WeaponsDAT):
			self.weaponsdat = weaponsdat
		else:
			self.weaponsdat = DAT.WeaponsDAT(self.tbl)
			self.weaponsdat.load_file(weaponsdat)
		if isinstance(flingydat, DAT.FlingyDAT):
			self.flingydat = flingydat
		else:
			self.flingydat = DAT.FlingyDAT(self.tbl)
			self.flingydat.load_file(flingydat)
		if isinstance(imagesdat, DAT.ImagesDAT):
			self.imagesdat = imagesdat
		else:
			self.imagesdat = DAT.ImagesDAT(self.tbl)
			self.imagesdat.load_file(imagesdat)
		if isinstance(spritesdat, DAT.SpritesDAT):
			self.spritesdat = spritesdat
		else:
			self.spritesdat = DAT.SpritesDAT()
			self.spritesdat.load_file(spritesdat)
		if isinstance(soundsdat, DAT.SoundsDAT):
			self.soundsdat = soundsdat
		else:
			self.soundsdat = DAT.SoundsDAT()
			self.soundsdat.load_file(soundsdat)
		if isinstance(imagestbl, TBL.TBL):
			self.imagestbl = imagestbl
		else:
			self.imagestbl = TBL.TBL()
			self.imagestbl.load_file(imagestbl)
		if isinstance(sfxdatatbl, TBL.TBL):
			self.sfxdatatbl = sfxdatatbl
		else:
			self.sfxdatatbl = TBL.TBL()
			self.sfxdatatbl.load_file(sfxdatatbl)

	def load_file(self, file):
		try:
			if isstr(file):
				f = open(file,'rb')
				data = f.read()
				f.close()
			else:
				data = file.read()
		except:
			raise PyMSError('Load',"Could not load iscript.bin '%s'" % file)
		try:
			headers = {}
			offsets = {}
			code = {}
			extrainfo = {}
			entry_tblstart = struct.unpack('<H', data[:2])[0]
			cur_offset = entry_tblstart
			def load_offset(o, id):
				curoffset = o
				if not o in offsets:
					offsets[o] = [id]
				elif not id in offsets[o]:
					offsets[o].append(id)
				while curoffset < len(data):
					co = curoffset
					if co in code:
						break
					c,curoffset = ord(data[curoffset]),co + 1
					if c >= len(OPCODES):
						raise PyMSError('Load','Invalid command, could possibly be a corrrupt iscript.bin')
					cmd = [c]
					params = OPCODES[c][1]
					if params:
						firstparam = params[0](0, self)
						if firstparam > 0:
							for param in params:
								p = param(0, self)
								cmd.append(struct.unpack(['','B','<H'][p], data[curoffset:curoffset+p])[0])
								curoffset += p
						else:
							secondparam = params[1](0, self)
							a,curoffset = ord(data[curoffset:curoffset-firstparam]),curoffset - firstparam
							cmd.extend((a,) + struct.unpack('<%s%s' % (a,['','B','H'][secondparam]), data[curoffset:curoffset+secondparam*a]))
							curoffset += secondparam*a
					code[co] = cmd
					if c == 7:
						load_offset(cmd[1],id)
						break
					elif c in [22,54]: #end,return
						break
					elif c in [30,53,57,58,59,60,63]: #randcondjump,call,pwrupcondjmp,trgtrangecondjmp,trgtarccondjmp,curdirectcondjmp,liftoffcondjump
						load_offset(cmd[-1],id)
				return curoffset
			while cur_offset < len(data)-3:
				id,offset = struct.unpack('<HH', data[cur_offset:cur_offset+4])
				#print '%s - %s' % (id,offset)
				if id == 65535 and offset == 0:
					if cur_offset+4 < len(data):
						try:
							extrainfo = loads(decompress(data[cur_offset+4:]))
						except:
							pass
					break
				if id in headers:
					raise PyMSError('Load',"Duplicate entry ID's, could possibly be a corrupt iscript.bin")
				if data[offset:offset+4] != 'SCPE':
					raise PyMSError('Load','Invalid iscript entry (missing header), could possibly be a corrupt iscript.bin')
				try:
					header = [ord(data[offset+4]),offset,[]]
					for n,p in enumerate(struct.unpack('<%sH' % ENTRY_TYPES[header[0]],data[offset+8:offset+8+2*ENTRY_TYPES[header[0]]])):
						if p:
							header[2].append(p)
							if not p in offsets:
								offsets[p] = [[id,n]]
							elif not [id,n] in offsets[p]:
								offsets[p].append([id,n])
						else:
							header[2].append(None)
				except:
					raise PyMSError('Load','Invalid iscript entry header, could possibly be a corrupt iscript.bin')
				headers[id] = header
				cur_offset += 4
			for id,dat in headers.iteritems():
				for n,o in enumerate(dat[2]):
					if o != None:
						if not o in offsets:
							offsets[o] = [[id,n]]
						elif not [id,n] in offsets[o]:
							offsets[o].append([id,n])
						load_offset(o, id)
			k = code.keys()
			k.sort()
			ocode = odict(code,k)
			self.headers = headers
			self.offsets = offsets
			self.code = ocode
			self.extrainfo = extrainfo
		except PyMSError:
			raise
		except:
			raise PyMSError('Load',"Unsupported aiscript.bin '%s', could possibly be invalid or corrupt" % file)

	def remove_code(self, o, id=None, code=None, offsets=None):
		if code == None:
			code = self.code
		if offsets == None:
			offsets = self.offsets
		if o in offsets and id != None:
			x = 0
			for n,i in enumerate(list(offsets[o])):
				if (isinstance(i,list) and i[0] == id) or (isinstance(i,int) and i == id):
					del offsets[o][n-x]
					x += 1
		if (not o in offsets and id == None) or not offsets[o]:
			if o in offsets :
				del offsets[o]
			curcmd = code.index(o)
			while curcmd < len(code):
				co = code.getkey(curcmd)
				if co != o and co in offsets:
					self.remove_code(co,id,code,offsets)
					break
				cmd = code[co]
				del code[co]
				c = cmd[0]
				if c == 7:
					if cmd[1] in offsets:
						self.remove_code(cmd[1],id,code,offsets)
					break
				elif c in [22,54]: #end,return
					break
				elif c in [30,53,57,58,59,60,63]: #randcondjump,call,pwrupcondjmp,trgtrangecondjmp,trgtarccondjmp,curdirectcondjmp,liftoffcondjump
					if cmd[-1] in offsets:
						self.remove_code(cmd[-1],id,code,offsets)

	def interpret(self, files, offset=None, checkframes=None):
		if not isinstance(files, list):
			files = [files]
		alldata = []
		for file in files:
			try:
				if isstr(file):
					f = open(file,'r')
					alldata.append(f.readlines())
					f.close()
				else:
					alldata.append(file.readlines())
					file.close()
			except:
				raise PyMSError('Interpreting',"Could not load file '%s'" % file)
		warnings = []
		def interpret_params(cmd,p,d):
			try:
				cmd.append(p(2, self, d))
			except PyMSWarning, w:
				cmd.append(w.extra)
				# ai[4][-1].append(w.extra)
				w.line = n + 1
				w.code = line
				warnings.append(w)
				# if var:
					# var.warning += ' when the above warning happened'
					# warnings.append(var)
			except PyMSError, e:
				e.line = n + 1
				e.code = line
				e.warnings = warnings
				# if var:
					# var.warning += ' when the above error happened'
					# e.warnings.append(var)
				raise e
			except:
				raise PyMSError('Parameter',"Invalid parameter data '%s', looking for type '%s'" % (d,p.__doc__),n,line, warnings=warnings)
			s = p(0, self)
			return s
		headers = {}
		offsets = {}
		code = {}
		labels = {}
		extrainfo = {}
		findlabels = odict()
		unused = []
		flowthrough = 1
		if offset == None:
			try:
				offset = self.code.getkey(len(self.code)-1)
				cmd = self.code[offset]
				ps = OPCODES[cmd[0]][1]
				if ps:
					p1 = ps[0](0,self)
					if p1 < 0:
						offset += sum([-p1,ps[1](0,self)*cmd[1]])
					else:
						offset += sum([p(0,self) for p in ps])
				offset += 1
			except:
				offset = 0
		state = 0
		# state: 0 = headerstart, 1 = id, 2 = type, 3 = header, 4 = code
		for data in alldata:
			for n,l in enumerate(data):
				if len(l) > 1:
					m = re.match('\\A\\s*##GRP:\\s+(.+?)\\s*\\Z', l, re.I)
					if checkframes and m:
						if not state in [0,4]:
							warnings.append(PyMSWarning('Interpreting','The special "##GRP:" extension must be used inside a scripts header. This is being treated simply as a comment.'),n,line)
						else:
							if self.grpframes:
								self.grpframes = min(self.grpframes,checkframes(m.group(1)))
							else:
								self.grpframes = checkframes(m.group(1))
						continue
					m = re.match('\\A\\s*##Name:\\s+(.+?)\\s*\\Z', l, re.I)
					if m:
						if state != 3:
							warnings.append(PyMSWarning('Interpreting','The special "##Name:" extension must be used inside a scripts header after the IsId header descriptor. This is being treated simply as a comment.'),n,line)
						elif ':' in m.group(1):
							warnings.append(PyMSWarning('Interpreting','Names defined with the special "##Name:" extension can not contain a colon (":"). This is being treated simply as a comment.'),n,line)
						else:
							extrainfo[id] = m.group(1)
						continue
					line = l.strip().split('#',1)[0]
					# print line
					if line:
						if re.match('\\A\\.headerstart\\s*\\Z',line):
							if not state in [0,4]:
								raise PyMSError('Interpreting','Unexpected ".headerstart"',n,line, warnings=warnings)
							state = 1
							header = []
							self.grpframes = None
						elif re.match('\\A\\.headerend\\s*\\Z',line):
							if state != 3:
								raise PyMSError('Interpreting','Unexpected ".headerend"',n,line, warnings=warnings)
							if len(header[3]) != ENTRY_TYPES[header[1]]:
								raise PyMSError('Interpreting','Unexpected ".headerend", expected a "%s" header descriptor' % HEADER[len(header[3])][0],n,line, warnings=warnings)
							state = 4
							headers[header[0]] = header[1:]
						elif state == 1:
							m = re.match('\\AIsId\\s+(.+)\\s*\\Z',line)
							if not m:
								raise PyMSError('Interpreting', 'Expected "IsId" header descriptor',n,line, warnings=warnings)
							try:
								id = int(m.group(1))
								if 0 > id or id > 65535:
									raise
							except:
								raise PyMSError('Interpreting', 'Invalid IScript ID, must be a number in te range 0 to 65535',n,line, warnings=warnings)
							header.append(id)
							state = 2
						elif state == 2:
							m = re.match('\\AType\\s+(.+)\\s*\\Z',line)
							if not m:
								raise PyMSError('Interpreting', 'Expected "Type" header descriptor',n,line, warnings=warnings)
							try:
								type = int(m.group(1))
								if not type in ENTRY_TYPES:
									raise
							except:
								raise PyMSError('Interpreting', 'Invalid Type value, must be one of the numbers: %s' % ', '.join([str(n) for n in ENTRY_TYPES.keys()]))
							header.extend([type,0,[]])
							state = 3
						elif state == 3:
							if len(header[3]) == ENTRY_TYPES[header[1]]:
								raise PyMSError('Interpreting', 'Expected ".headerend"',n,line, warnings=warnings)
							m = re.match('\\A(\\S+)\\s+(\\S+)\\s*\\Z',line)
							if not m.group(1) in HEADER[len(header[3])]:
								raise PyMSError('Interpreting', 'Expected "%s" header descriptor' % HEADER[len(header[3])][0],n,line, warnings=warnings)
							label = m.group(2)
							if label in labels:
								header[3].append(labels[label])
							else:
								if label != '[NONE]':
									if not label in findlabels:
										findlabels[label] = [(header,len(header[3]))]
									else:
										findlabels[label].append((header,len(header[3])))
								header[3].append(None)
						elif state == 4:
							m = re.match('\\A(\\S+):\\s*\\Z', line)
							if m:
								label = m.group(1)
								if label in labels:
									raise PyMSError('Interpreting', 'Duplicate label name "%s"' % label,n,line, warnings=warnings)
								labels[label] = offset
								if label in findlabels:
									#print label
									for d in findlabels[label]:
										#print d
										if isinstance(d, tuple):
											d[0][3][d[1]] = offset
											if not offset in offsets:
												offsets[offset] = [[d[0][0],d[1]]]
											elif not [d[0][0],d[1]] in offsets[offset]:
												offsets[offset].append([d[0][0],d[1]])
										else:
											d[0][d[1]] = offset
											if not offset in offsets:
												offsets[offset] = [d[2]]
											elif not d[2] in offsets[offset]:
												offsets[offset].append(d[2])
									del findlabels[label]
								elif flowthrough < 1:
									unused.append(label)
							else:
								m = re.match('\\A\\t*(\\S+)(?:\\s+(.+?))?\\s*\\Z', line)
								if m:
									opcode,dat = m.group(1),[]
									if m.group(2):
										dat = re.split('\\s+',m.group(2))
									if not opcode in REV_OPCODES:
										raise PyMSError('Interpreting', 'Unknown opcode "%s"' % opcode,n,line, warnings=warnings)
									c = REV_OPCODES[opcode]
									if c in [7,22,54]:
										flowthrough = -1
									cmd = [c]
									code[offset] = cmd
									params = OPCODES[c][1]
									if params:
										if params[0](0,self) < 0:
											if not dat:
												raise PyMSError('Interpreting','Incorrect amount of parameters (need at least 1)',n,line, warnings=warnings)
											offset += interpret_params(cmd,params[0],dat[0])
											if len(dat)-1 != cmd[-1]:
												raise PyMSError('Interpreting','Incorrect amount of parameters (got %s, needed %s)' % (len(dat)-1, cmd[-1]),n,line, warnings=warnings)
											for v in dat[1:]:
												offset += interpret_params(cmd,params[1],v)
										else:
											if params and len(dat) != len(params):
												raise PyMSError('Interpreting','Incorrect amount of parameters (got %s, needed %s)' % (len(dat), len(params)),n,line, warnings=warnings)
											if not params and dat:
												raise PyMSError('Interpreting','Command requires no parameters, but got %s' % len(dat),n,line, warnings=warnings)
											if params and dat:
												for d,p in zip(dat,params):
													if p == type_label:
														if not d in labels:
															if not d in findlabels:
																findlabels[d] = [[cmd,len(cmd),id]]
															else:
																findlabels[d].append([cmd,len(cmd),id])
															cmd.append(None)
														else:
															cmd.append(labels[d])
															if not labels[d] in offsets:
																offsets[labels[d]] = [id]
															elif not id in offsets[labels[d]]:
																offsets[labels[d]].append(id)
														if d in unused:
															unused.remove(d)
														offset += p(0, self)
														continue
													offset += interpret_params(cmd,p,d)
									offset += 1
								else:
									raise PyMSError('Interpreting','Invalid syntax, unknown line format',n,line, warnings=warnings)
						flowthrough += 1
		if state == 1:
			raise PyMSError('Interpreting', 'Unexpected end of file, expected "IsId" header descriptor',n,line, warnings=warnings)
		if state == 2:
			raise PyMSError('Interpreting', 'Unexpected end of file, expected "Type" header descriptor',n,line, warnings=warnings)
		if state == 3:
			raise PyMSError('Interpreting', 'Unexpected end of file, expected "%s" header descriptor' % HEADER[len(header[3])][0],n,line, warnings=warnings)
		if findlabels:
			raise PyMSError('Interpreting', "The label '%s' was not found" % findlabels.getkey(0),n,line, warnings=warnings)
		if unused:
			for l in unused:
				warnings.append(PyMSWarning('Interpeting', "The label '%s' is unused, label is discarded" % l))
				r = odict(code, sorted(code.keys()))
				self.remove_code(labels[l], code=r, offsets=offsets)
				code = r.dict
		# print 'Headers: ' + pprint(headers)
		# print 'Offsets: ' + pprint(offsets)
		# print 'Code   : ' + pprint(code)
		# print 'Labels : ' + pprint(labels)
		# print 'FLabels: ' + pprint(findlabels)
		for id in headers.keys():
			if id in self.headers:
				for o in self.headers[id][2]:
					if o != None and o in self.offsets:
						self.remove_code(o,id)
			self.headers[id] = headers[id]
		for o,i in offsets.iteritems():
			self.offsets[o] = i
		c = dict(self.code.dict)
		for o,cmd in code.iteritems():
			c[o] = cmd
		k = c.keys()
		k.sort()
		self.code = odict(c,k)
		self.extrainfo.update(extrainfo)
		return warnings

	def decompile(self, file, reference=False, ids=None):
		if isstr(file):
			try:
				f = open(file, 'w')
			except:
				raise PyMSError('Decompile',"Could not load file '%s'" % file, warnings=warnings)
		else:
			f = file
		if ids == None:
			ids = self.header.keys()
		longheader = max([len(h[0]) for h in HEADER] + [13]) + 1
		longopcode = max([len(o[0][0]) for o in OPCODES] + [13]) + 1
		warnings = []
		labels = {}
		completed = []
		def setlabel(o,local,entry):
			entry = re.sub('[\\/\\(\\)-]','_',entry.replace(' ','').replace("'",''))
			f = []
			for i in self.offsets[o]:
				if isinstance(i,list) and i[0] == id:
					f.append(i[1])
			if f:
				f.sort()
				labels[o] = entry + HEADER[f[0]][0]
				return 0
			labels[o] = entry + 'Local' + str(local).zfill(2)
			return 1
		def decompile_offset(o,code,local,id):
			if id in self.extrainfo:
				entry = self.extrainfo[id].replace(' ','_')
			elif id < len(DAT.DATA_CACHE['IscriptIDList.txt']):
				entry = DAT.DATA_CACHE['IscriptIDList.txt'][id]
			else:
				entry = 'Unnamed Custom Entry'
			if not o in completed:
				completed.append(o)
				if not o in labels:
					labels[o] = re.sub('[\\/\\(\\)-]','_',entry.replace(' ','').replace("'",'')) + 'Local%s' % local
					local += 1
				code += labels[o] + ':\n'
				curcmd = self.code.index(o)
				# print '\t%s' % o
				donext = []
				while True:
					# print curcmd
					co = self.code.getkey(curcmd)
					# print co
					if co in self.offsets and not co in labels:
						local += setlabel(co,local,entry)
						completed.append(co)
						code += '%s:\n' % labels[co]
					cmd = self.code.getitem(curcmd)
					c = OPCODES[cmd[0]][0][0]
					if cmd[0] == 7:
						if not cmd[1] in labels:
							local += setlabel(cmd[1],local,entry)
						code += '	%s%s	%s\n\n' % (c,' ' * (longopcode-len(c)),labels[cmd[1]])
						code,local,curcmd = decompile_offset(cmd[1],code,local,id)
						break
					elif cmd[0] in [22,54]: #end,return
						code += '	%s\n\n' % c
						break
					elif cmd[0] in [30,53,57,58,59,60,63]: #randcondjump,call,pwrupcondjmp,trgtrangecondjmp,trgtarccondjmp,curdirectcondjmp,liftoffcondjump
						if cmd[-1] not in labels:
							local += setlabel(cmd[-1],local,entry)
						if not cmd[-1] in donext:
							donext.append(cmd[-1])
						extra = []
						code += '	%s%s	' % (c,' ' * (longopcode-len(c)))
						for v,t in zip(cmd[1:-1],OPCODES[cmd[0]][1][:-1]):
							p,e = t(1,self,v)
							if e:
								extra.append(e)
							code += p + ' '
						code += labels[cmd[-1]]
						if extra:
							code = code[:-1] + '\t# ' + ' | '.join(extra)
						code += '\n'
						curcmd += 1
					else:
						extra = []
						code += '	' + c
						if OPCODES[cmd[0]][1]:
							code += ' ' * (longopcode-len(c)) + '\t'
							d,o = cmd[1:],OPCODES[cmd[0]][1]
							if OPCODES[cmd[0]][1][0](0,self) == -1:
								n = OPCODES[cmd[0]][1][0](1,self,d[0])[0]
								code += n + ' '
								o = [OPCODES[cmd[0]][1][1]] * int(n)
								del d[0]
							for v,t in zip(d,o):
								p,e = t(1,self,v)
								if e:
									extra.append(e)
								code += p + ' '
							if extra:
								code = code[:-1] + '\t# ' + ' | '.join(extra)
						code += '\n'
						curcmd += 1
				if donext:
					for d in donext:
						code,local,curcmd = decompile_offset(d,code,local,id)
				return (code,local,curcmd)
			return (code,local,-1)
		usedby = {}
		for i in range(DAT.ImagesDAT.count):
			id = self.imagesdat.get_value(i, 'IscriptID')
			if id in ids:
				if not id in usedby:
					usedby[id] = '# This header is used by images.dat entries:\n'
				usedby[id] += '# %s %s (%s)\n' % (str(i).zfill(3), DAT.DATA_CACHE['Images.txt'][i], TBL.decompile_string(self.imagestbl.strings[self.imagesdat.get_value(i,'GRPFile')-1][:-1]))
		invalid = []
		unknownid = 0
		for id in ids:
			code = ''
			local = 0
			if not id in self.headers:
				invalid.append(id)
				continue
			type, offset, header = self.headers[id]
			u = ''
			if id in usedby:
				u = usedby[id]
			f.write('# ----------------------------------------------------------------------------- #\n%s.headerstart\nIsId          	%s\nType          	%s\n' % (u, id, type))
			for o,l in zip(header,HEADER[:ENTRY_TYPES[type]]):
				if o == None:
					label = '[NONE]'
				elif o in labels:
					label = labels[o]
				else:
					if id in self.extrainfo:
						entry = self.extrainfo[id].replace(' ','_')
					elif id < len(DAT.DATA_CACHE['IscriptIDList.txt']):
						entry = DAT.DATA_CACHE['IscriptIDList.txt'][id]
					else:
						entry = 'Unnamed Custom Entry'
					local += setlabel(o,local,entry)
					label = labels[o]#'%s%s' % (DAT.DATA_CACHE['IscriptIDList.txt'][id],l[0])
				f.write('%s%s	%s\n' % (l[0],' ' * (longheader-len(l[0])),label))
				if o != None:
					code,local,curcmd = decompile_offset(o,code,local,id)
			if id in self.extrainfo:
				f.write('##Name: %s\n' % self.extrainfo[id])
			f.write('.headerend\n# ----------------------------------------------------------------------------- #\n\n' + code)
		f.close()

	def compile(self, file):
		try:
			f = open(file, 'wb')
		except:
			raise PyMSError('Compile',"Could not load file '%s'" % file)
		code = ''
		offsets = {}
		offset = 1372
		for o,cmd in self.code.iteritems():
			offsets[o] = offset
			#print sum([1] + [p(0,self) for p in OPCODES[cmd[0]][1]])
			offset += 1
			ps = OPCODES[cmd[0]][1]
			if ps:
				p1 = ps[0](0,self)
				if p1 < 0:
					offset += sum([-p1,ps[1](0,self)*cmd[1]])
				else:
					offset += sum([p(0,self) for p in ps])
		for o,cmd in self.code.iteritems():
			ps = OPCODES[cmd[0]][1]
			if ps:
				p1 = ps[0](0,self)
				if p1 < 0:
					code += struct.pack('<B%s%s%s' % (['','B','H'][-p1],len(cmd)-2,['','B','H'][ps[1](0,self)]), *cmd)
				else:
					code += chr(cmd[0])
					for v,p in zip(cmd[1:],ps):
						if p == type_label:
							code += struct.pack('<H',offsets[v])
						else:
							code += struct.pack(['','B','<H'][p(0,self)], v)
			else:
				code += chr(cmd[0])
		# print offset-1372
		# print len(code)
		table = ''
		for id,dat in self.headers.iteritems():
			table += struct.pack('<HH', id,offset)
			entry = 'SCPE%s\x00\x00\x00' % chr(dat[0])
			for o in dat[2]:
				if o == None:
					entry += '\x00\x00'
				else:
					entry += struct.pack('<H', offsets[o])
			offset += len(entry)
			code += entry
		f.write('%s%s\xFF\xFF\x00\x00' % (struct.pack('<H',offset),'\x00' * 1366) + code + table + '\xFF\xFF\x00\x00')
		if self.extrainfo:
			f.write(compress(dumps(self.extrainfo),9))
		f.close()

#if __name__ == '__main__':
	## import sys
	## sys.stdout = open('stdieo.txt','w')
	# gwarnings = []
	# try:
		# i = IScriptBIN()
		## i.load_file('iscript.bin')
		## i.compile('test.bin')
		# i.load_file('test.bin')
		# i.decompile('test.txt',[27])
		## gwarnings.append(i.interpret('test.txt'))
		## i.decompile('test2.txt',[27])
	# except PyMSError, e:
		# if gwarnings:
			# for warning in gwarnings:
				# print repr(warning)
		# print repr(e)
	# except:
		# raise
	# else:
		# if gwarnings:
			# for warning in gwarnings:
				# print repr(warning)