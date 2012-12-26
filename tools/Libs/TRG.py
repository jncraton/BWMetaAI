from utils import *
import TBL, AIBIN

import struct, re, os

REGISTER = []

keywords = [
	'include',
	'Current Player',
	'Player',
	'Set To',
	'Equals',
	'At Least',
	'Exactly',
	'At Most',
	'Foes',
	'Allies',
	'Neutral Players',
	'All Players',
	'Force',
	'Unused',
	'Non Allied Victory Players',
	'None',
	'Any Unit',
	'Men',
	'Buildings',
	'Factories',
	'Anywhere',
	'Location',
	'Ore',
	'Gas',
	'Ore and Gas',
	'Total',
	'Units',
	'Units and Buildings',
	'Kills',
	'Razings',
	'Kills and Razings',
	'Custom',
	'Switch',
	'Set',
	'Clear',
	'Cleared',
	'Add',
	'Subtract',
	'Move',
	'All',
	'Attack',
	'Patrol',
	'Default String',
	'String',
	'WAV',
	'Property',
	'Toggle',
	'Randomize',
	'Multiply',
	'Divide',
	'Cloaked',
	'Burrowed',
	'In Transit',
	'Hallucinated',
	'Invincible',
	'Unknown1',
	'Unknown2',
	'Unknown3',
	'Unknown4',
	'Unknown5',
	'Unknown6',
	'Unknown7',
	'Unknown8',
	'Unknown9',
	'Unknown10',
	'Unknown11',
	'Owner',
	'Health',
	'Shields',
	'Energy',
	'Resources',
	'AmountInHanger',
	'Unknown'
	'Always Display',
	'Only With Subtitles',
	'Zerg Available',
	'Zerg Used',
	'Zerg Max',
	'Terran Available',
	'Terran Used',
	'Terran Max',
	'Protoss Available',
	'Protoss Used',
	'Protoss Max',
	'Turn On',
	'Turn Off',
]

player_ids = [
	'Player 1',
	'Player 2',
	'Player 3',
	'Player 4',
	'Player 5',
	'Player 6',
	'Player 7',
	'Player 8',
	'Player 9',
	'Player 10',
	'Player 11',
	'Player 12',
	'Player 13',
	'Current Player',
	'Foes',
	'Allies',
	'Neutral Players',
	'All Players',
	'Force 1',
	'Force 2',
	'Force 3',
	'Force 4',
	'Unused 1',
	'Unused 2',
	'Unused 3',
	'Unused 4',
	'Non Allied Victory Players'
]

resource_types = [
	'Ore',
	'Gas',
	'Ore and Gas'
]

unit_types = [
	'None',
	'Any Unit',
	'Men',
	'Buildings',
	'Factories'
]

score_types = [
	'Total',
	'Units',
	'Buildings',
	'Units and Buildings',
	'Kills',
	'Razings',
	'Kills and Razings',
	'Custom',
]

unit_orders = [
	'Move',
	'Patrol',
	'Attack'
]

ally_status = [
	'Enemy',
	'Ally',
	'Allied Victory'
]

unit_properties = [
	'Cloaked',
	'Burrowed',
	'In Transit',
	'Hallucinated',
	'Invincible',
	'Unknown1',
	'Unknown2',
	'Unknown3',
	'Unknown4',
	'Unknown5',
	'Unknown6',
	'Unknown7',
	'Unknown8',
	'Unknown9',
	'Unknown10',
	'Unknown11'
]

unit_data = [
	'Owner',
	'Health',
	'Shields',
	'Energy',
	'Resources',
	'AmountInHanger',
	'Unknown'
]

TYPE_HELP = {}

def condition_number(trg, decompile, condition, data=None):
	"""Number         - Any number in the range 0 to 4294967295"""
	if decompile:
		return condition[2]
	try:
		n = int(data)
		if -1 < n < 4294967296:
			condition[2] = n
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid Number (value must be in the range 0 to 4294967295)" % data)

def condition_player(trg, decompile, condition, data=None):
	"""Player         - A number in the range 0 to 255 (with or without the keyword Player before it), or any keyword from this list: Current Player, Foes, Allies, Neutral Players, All Players, Force 1, Force 2, Force 3, Force 4, Unused 1, Unused 2, Unused 3, Unused 4, Non Allied Victory Players"""
	if decompile:
		if condition[1] < 27:
			return player_ids[condition[1]]
		return condition[1]
	if data in player_ids:
		condition[1] = player_ids.index(data)
		return
	try:
		p = int(data)
		if -1 < p < 256:
			condition[1] = p
		return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid Player (value must be in the range 0 to 255, or on of the keywords: Current Player, Foes, Allies, Neutral Players, All Players, Force 1, Force 2, Force 3, Force 4, Unused 1, Unused 2, Unused 3, Unused 4, Non Allied Victory Players)" % data)

def condition_comparison(trg, decompile, condition, data=None):
	"""Comparison     - One of the keywords: At Least, Exactly, At Most"""
	if decompile:
		if not condition[4]:
			return 'At Least'
		elif condition[4] == 1:
			return 'At Most'
		elif condition[4] == 10:
			return 'Exactly'
		raise
	if data in ['At Least','Exactly','At Most']:
		if data == 'At Least':
			condition[4] = 0
		elif data == 'At Most':
			condition[4] = 1
		else:
			condition[4] = 10
		return
	raise PyMSError('Parameter',"'%s' is an invalid Comparison (value must be one of the keywords: At Least, Exactly, At Most)" % data)

def condition_tunit(trg, decompile, condition, data=None):
	"""TUnit          - A unit ID from 0 to 227 (and extended unit ID 233 to 65535), a full unit name (in the TBL, its the part before the first <0>), or a type from the list: None, Any Unit, Men, Buildings, Factories"""
	if decompile:
		if -1 < condition[3] < 228:
			s = trg.stat_txt.strings[condition[3]].split('\x00')
			if s[1] != '*':
				return TBL.decompile_string('\x00'.join(s[:2]), include='(,)')
			else:
				return TBL.decompile_string(s[0], include='(,)')
		if condition[3] < 233:
			return unit_types[condition[3] - 228]
		return condition[3]
	if data in unit_types:
		condition[3] = unit_types.index(data) + 228
		condition[7] ^= 16
		return
	try:
		u = int(data)
		if -1 < u < 65536:
			condition[3] = u
			return
	except:
		pass
	for i,name in enumerate(trg.stat_txt.strings[:228]):
		n = name.split('\x00')
		if TBL.compile_string(data) == n[0] or (n[1] != '*' and TBL.compile_string(data) == '\x00'.join(n[:2])):
			condition[3] = i
			return
	raise PyMSError('Parameter',"'%s' is an invalid TUnit (value must be in the range 0 to 227, a full unit name, or a type from the list: None, Any Unit, Men, Buildings, Factories)" % data)

def condition_location(trg, decompile, condition, data=None):
	"""Location       - A number in the range 0 to 254 (with or without the keyword Location before it), or the keyword Anywhere (Anywhere is Location 63)"""
	if decompile:
		if condition[0] == 64:
			return 'Anywhere'
		return 'Location %s' % (condition[0]-1)
	if data == 'Anywhere':
		condition[0] = 64
		return
	else:
		l = None
		try:
			if data.startswith('Location '):
				l = int(data.split(' ',1)[1])
			else:
				l = int(data)
		except:
			pass
		if l != None and 0 <= l < 255:
			condition[0] = l + 1
			return
	raise PyMSError('Parameter',"'%s' is an invalid Location (value must be in the range 0 to 254, or the keyword Anywhere, which is Location 63)" % data)

def condition_restype(trg, decompile, condition, data=None):
	"""ResType        - One of the keywords: Ore, Gas, Ore and Gas"""
	if decompile:
		return resource_types[condition[6]]
	if data in resource_types:
		condition[6] = resource_types.index(data)
		return
	raise PyMSError('Parameter',"'%s' is an invalid ResType (value must be one of the keywords: Ore, Gas, Ore and Gas)" % data)

def condition_score(trg, decompile, condition, data=None):
	"""ScoreType      - One of the keywords: Total, Units, Buildings, Units and Buildings, Kills, Razings, Kills and Razings, Custom"""
	if decompile:
		return score_types[condition[6]]
	if data in score_types:
		condition[6] = score_types.index(data)
		return
	raise PyMSError('Parameter',"'%s' is an invalid Score (value must be one of the keywords: Total, Units, Buildings, Units and Buildings, Razings, Kills and Razings, Custom)" % data)

def condition_switch(trg, decompile, condition, data=None):
	"""Switch         - A number in the range 0 to 255 (with or without the keyword Switch before it)"""
	if decompile:
		return 'Switch %s' % condition[6]
	l = None
	try:
		if data.startswith('Switch '):
			l = int(data.split(' ',1)[1])
		else:
			l = int(data)
	except:
		pass
	if l != None and -1 < l < 256:
		condition[6] = l
		return
	raise PyMSError('Parameter',"'%s' is an invalid Switch (value must be in the range 0 to 255)" % data)

def condition_set(trg, decompile, condition, data=None):
	"""Set            - Either the keyword Set, or Cleared"""
	if decompile:
		if condition[4] == 2:
			return 'Set'
		elif condition[4] == 3:
			return 'Cleared'
		raise
	if data in ['Set','Cleared']:
		if data == 'Set':
			condition[4] = 2
		else:
			condition[4] = 3
		return
	raise PyMSError('Parameter',"'%s' is an invalid Set (value must be one of the keywords: Set, Cleared)" % data)

def condition_raw(trg, decompile, condition, data=None, place=0):
	"""Raw            - A raw value."""
	if decompile:
		return condition[place]
	s = [4294967296,4294967296,4294967296,65535,255,255,255,255][place]
	try:
		n = int(data)
		if -1 < n < s:
			condition[place] = n
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid Raw (value at that position must be in the range 0 to %s)" % (data,s))
#
def action_time(trg, decompile, action, strings, properties, data=None):
	"""Time           - Like number, can be any number in the range 0 to 4294967295"""
	if decompile:
		return action[3]
	try:
		t = int(data)
		if -1 < t < 4294967296:
			action[3] = t
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid Time (value must be in the range 0 to 4294967295)" % data)

def action_string(trg, decompile, action, strings, properties, data=None):
	"""String         - A number corrisponding to a string (with or without the keyword String before it)"""
	if decompile:
		return 'String %s' % action[1]
	s = None
	try:
		if data.startswith('String '):
			s = int(data.split(' ',1)[1])
		else:
			s = int(data)
	except:
		pass
	if s != None and s in strings:
		action[1] = s
		return
	raise PyMSError('Parameter',"'%s' is an invalid String (value must be a number corrisponding to a string)" % data)

def action_dstring(trg, decompile, action, strings, properties, data=None):
	"""DString        - A number corrisponding to a string (with or without the keyword String before it), or the keyword Default String"""
	if decompile:
		if not action[1]:
			return 'Default String'
		return 'String %s' % action[1]
	if data == 'Default String':
		action[1] = 0
		return
	s = None
	try:
		if data.startswith('String '):
			s = int(data.split(' ',1)[1])
		else:
			s = int(data)
	except:
		pass
	if s != None and s in strings:
		action[1] = s
		return
	raise PyMSError('Parameter',"'%s' is an invalid String (value must be a number corrisponding to a string)" % data)

def action_unit(trg, decompile, action, strings, properties, data=None):
	"""Unit           - A unit ID from 0 to 227 (and extended unit ID 233 to 65535), a full unit name (in the TBL, its the part before the first <0>)"""
	if decompile:
		if action[6] < 228:
			s = trg.stat_txt.strings[action[6]].split('\x00')
			if s[1] != '*':
				return TBL.decompile_string('\x00'.join(s[:2]), include='(,)')
			else:
				return TBL.decompile_string(s[0], include='(,)')
		return action[6]
	try:
		i = int(data)
		if -1 < i < 65536:
			action[6] = i
			return
	except:
		pass
	for i,name in enumerate(trg.stat_txt.strings[:228]):
		n = name.split('\x00')
		if TBL.compile_string(data) == n[0] or (n[1] != '*' and TBL.compile_string(data) == '\x00'.join(n[:2])):
			action[6] = i
			return
	raise PyMSError('Parameter',"'%s' is an invalid Unit (value must be in the range 0 to 227, or a full unit name)" % data)

def action_location(trg, decompile, action, strings, properties, data=None):
	"""Location"""
	if decompile:
		if action[0] == 64:
			return 'Anywhere'
		return 'Location %s' % (action[0]-1)
	if data == 'Anywhere':
		action[0] = 64
		return
	l = None
	try:
		if data.startswith('Location '):
			l = int(data.split(' ',1)[1])
		else:
			l = int(data)
	except:
		pass
	if l != None and 0 <= l < 255:
		action[0] = l + 1
		return
	raise PyMSError('Parameter',"'%s' is an invalid Location (value must be in the range 0 to 254, or the keyword Anywhere, which is Location 63)" % data)

def action_destlocation(trg, decompile, action, strings, properties, data=None):
	"""DestLocation   - A number in the range 0 to 254 (with or without the keyword Location before it), or the keyword Anywhere"""
	if decompile:
		if action[5] == 64:
			return 'Anywhere'
		return 'Location %s' % (action[5]-1)
	if data == 'Anywhere':
		action[5] = 64
		return
	l = None
	try:
		if data.startswith('Location '):
			l = int(data.split(' ',1)[1])
		else:
			l = int(data)
	except:
		pass
	if l != None and 0 <= l < 255:
		action[5] = l + 1
		return
	raise PyMSError('Parameter',"'%s' is an invalid DestLocation (value must be in the range 0 to 254, or the keyword Anywhere)" % data)

def action_modifier(trg, decompile, action, strings, properties, data=None):
	"""Modifier       - One of the keywords: Set To, Add, Subtract"""
	if decompile:
		if action[8] == 7:
			return 'Set To'
		elif action[8] == 8:
			return 'Add'
		elif action[8] == 9:
			return 'Subtract'
		raise
	if data in ['Set To', 'Add', 'Subtract']:
		if data == 'Set To':
			action[8] = 7
		elif data == 'Add':
			action[8] = 8
		else:
			action[8] = 9
		return
	raise PyMSError('Parameter',"'%s' is an invalid Modifier (value must be one of the keywords: Set To, Add, Subtract)" % data)

def action_wav(trg, decompile, action, strings, properties, data=None):
	"""WAV            - A number corrisponding to a WAV (with or without the keyword WAV before it)"""
	if decompile:
		return 'WAV %s' % action[2]
	s = None
	try:
		if data.startswith('WAV '):
			s = int(data.split(' ',1)[1])
		else:
			s = int(data)
	except:
		pass
	if s != None and s in strings:
		action[2] = s
		return
	raise PyMSError('Parameter',"'%s' is an invalid WAV (value must be a number corrisponding to a string)" % data)

def action_display(trg, decompile, action, strings, properties, data=None):
	"""Display        - Either the keyword Always Display, or Only With Subtitles"""
	if decompile:
		if action[9] & 4:
			return 'Always Display'
		return 'Only With Subtitles'
	if data == 'Always Display':
		action[9] ^= 4
		return
	elif data == 'Only With Subtitles':
		return
	raise PyMSError('Parameter',"'%s' is an invalid Display type (value must be one of the keywords: Always Display, Only With Subtitles)" % data)

def action_player(trg, decompile, action, strings, properties, data=None):
	"""Player"""
	if decompile:
		if action[4] < 27:
			return player_ids[action[4]]
		return action[4]
	if data in player_ids:
		action[4] = player_ids.index(data)
		return
	try:
		p = int(data)
		if -1 < p < 256:
			action[4] = p
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid Player (value must be in the range 0 to 255, or on of the keywords: Current Player, Foes, Allies, Neutral Players, All Players, Force 1, Force 2, Force 3, Force 4, Unused 1, Unused 2, Unused 3, Unused 4, Non Allied Victory Players)" % data)

def action_destplayer(trg, decompile, action, strings, properties, data=None):
	"""DestPlayer     - A number in the range 0 to 255 (with or without the keyword Player before it), or any keyword from this list: Current Player, Foes, Allies, Neutral Players, All Players, Force 1, Force 2, Force 3, Force 4, Unused 1, Unused 2, Unused 3, Unused 4, Non Allied Victory Players"""
	if decompile:
		if action[5] < 27:
			return player_ids[action[5]]
		return action[5]
	if data in player_ids:
		action[5] = player_ids.index(data)
		return
	try:
		p = int(data)
		if -1 < p < 256:
			action[5] = p
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid DestPlayer (value must be in the range 0 to 255, or on of the keywords: Current Player, Foes, Allies, Neutral Players, All Players, Force 1, Force 2, Force 3, Force 4, Unused 1, Unused 2, Unused 3, Unused 4, Non Allied Victory Players)" % data)

def action_number(trg, decompile, action, strings, properties, data=None):
	"""Number"""
	if decompile:
		return action[5]
	try:
		n = int(data)
		if -1 < n < 4294967296:
			action[5] = n
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid Number (value must be in the range 0 to 4294967295)" % data)

def action_qnumber(trg, decompile, action, strings, properties, data=None):
	"""QNumber        - Any number in the range 1 to 4294967295, or the keyword All"""
	if decompile:
		if action[8]:
			return action[8]
		return 'All'
	if data == 'All':
		action[5] = 0
		return
	try:
		n = int(data)
		if 0 < n < 256:
			action[8] = n
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid QNumber (value must be in the range 1 to 255, or the keyword All)" % data)

def action_property(trg, decompile, action, strings, properties, data=None):
	"""Property       - A number corrisponding to a Property (with or without the keyword Property before it)"""
	if decompile:
		return 'Property %s' % action[5]
	p = None
	try:
		if data.startswith('Property '):
			p = int(data.split(' ',1)[1])
		else:
			p = int(data)
	except:
		pass
	if p != None and p in properties:
		action[5] = p
		action[9] ^= 8
		return
	raise PyMSError('Parameter',"'%s' is an invalid Property (value must be a number corrisponding to a property)" % data)

def action_switch(trg, decompile, action, strings, properties, data=None):
	"""Switch"""
	if decompile:
		return 'Switch %s' % action[5]
	s = None
	try:
		if data.startswith('Switch '):
			s = int(data.split(' ',1)[1])
		else:
			s = int(data)
	except:
		pass
	if -1 < s < 256:
		action[5] = s
		return
	raise PyMSError('Parameter',"'%s' is an invalid Switch (value must be in the range 0 to 255)" % data)

def action_switchaction(trg, decompile, action, strings, properties, data=None):
	"""SwitchAction   - One of the keywords: Set, Clear, Toggle, Randomize"""
	if decompile:
		if action[8] == 4:
			return 'Set'
		elif action[8] == 5:
			return 'Clear'
		elif action[8] == 6:
			return 'Toggle'
		elif action[8] == 11:
			return 'Randomize'
		raise
	if data in ['Set','Clear','Toggle','Randomize']:
		if data == 'Set':
			action[8] = 4
		elif data == 'Clear':
			action[8] = 5
		elif data == 'Toggle':
			action[8] = 6
		else:
			action[8] = 11
		return
	raise PyMSError('Parameter',"'%s' is an invalid SwitchAction (value must be one of the keywords: Set, Clear, Toggle, Randomize)" % data)

def action_aiscript(trg, decompile, action, strings, properties, data=None):
	"""AIScript       - The name of an AIScript (a list of all the AIScript values is given below)"""
	if decompile:
		ai = struct.pack('<L', action[5])
		if ai in trg.ais[0][0]:
			return trg.ais[0][0][ai]
		if ai in trg.ais[1][0]:
			return trg.ais[1][0][ai]
		return ai
	if data in trg.ais_rev[0][0]:
		action[5] = struct.unpack('<L',trg.ais_rev[0][0][data])[0]
		return
	if data in trg.ais_rev[1][0]:
		action[5] = struct.unpack('<L',trg.ais_rev[1][0][data])[0]
		return
	if len(data) == 4:
		action[5] = struct.unpack('<L',data)[0]
		return
	raise PyMSError('Parameter',"'%s' is an invalid AIScript (value must be an AIScript, check the reference for a list)" % data)

def action_aiscript_loc(trg, decompile, action, strings, properties, data=None):
	"""AIScriptLoc    - The name of a location based AIScript (a list of all location based AIScripts is given below)"""
	if decompile:
		ai = struct.pack('<L', action[5])
		if ai in trg.ais[0][1]:
			return trg.ais[0][1][ai]
		if ai in trg.ais[1][1]:
			return trg.ais[1][1][ai]
		return ai
	if data in trg.ais_rev[0][1]:
		action[5] = struct.unpack('<L',trg.ais_rev[0][1][data])[0]
		return
	if data in trg.ais_rev[1][1]:
		action[5] = struct.unpack('<L',trg.ais_rev[1][1][data])[0]
		return
	if len(data) == 4:
		action[5] = struct.unpack('<L',data)[0]
		return
	raise PyMSError('Parameter',"'%s' is an invalid AIScriptLoc (value must be an AIScript, check the reference for a list)" % data)

def action_tunit(trg, decompile, action, strings, properties, data=None):
	"""TUnit"""
	if decompile:
		if -1 < action[6] < 228:
			s = trg.stat_txt.strings[action[6]].split('\x00')
			if s[1] != '*':
				return TBL.decompile_string('\x00'.join(s[:2]), include='(,)')
			else:
				return TBL.decompile_string(s[0], include='(,)')
		if action[6] < 233:
			return unit_types[action[6] - 228]
		return action[6]
	if data in unit_types:
		action[6] = unit_types.index(data) + 228
		action[9] ^= 16
		return
	try:
		i = int(data)
		if -1 < i < 65536:
			action[6] = i
			return
	except:
		pass
	for i,name in enumerate(trg.stat_txt.strings[:228]):
		n = name.split('\x00')
		if TBL.compile_string(data) == n[0] or (n[1] != '*' and TBL.compile_string(data) == '\x00'.join(n[:2])):
			action[6] = i
			return
	raise PyMSError('Parameter',"'%s' is an invalid TUnit value must be in the range 0 to 227, a full unit name, or a type from the list: None, Any Unit, Men, Buildings, Factories)" % data)

def action_restype(trg, decompile, action, strings, properties, data=None):
	"""ResType"""
	if decompile:
		return resource_types[action[6]]
	if data in resource_types:
		action[6] = resource_types.index(data)
		return
	raise PyMSError('Parameter',"'%s' is an invalid ResType (value must be one of the keywords: Ore, Gas, Ore and Gas)" % data)

def action_score(trg, decompile, action, strings, properties, data=None):
	"""ScoreType"""
	if decompile:
		return score_types[action[6]]
	if data in score_types:
		action[6] = score_types.index(data)
		return
	raise PyMSError('Parameter',"'%s' is an invalid ScoreType (value must be one of the keywords: Total, Units, Buildings, Units and Buildings, Razings, Kills and Razings, Custom)" % data)

def action_state(trg, decompile, action, strings, properties, data=None):
	"""State          - One of the keywords: Set, Clear, Toggle"""
	if decompile:
		if action[8] == 4:
			return 'Set'
		elif action[8] == 5:
			return 'Clear'
		elif action[8] == 6:
			return 'Toggle'
		raise
	if data in ['Set','Clear','Toggle']:
		if data == 'Set':
			action[8] = 4
		elif data == 'Clear':
			action[8] = 5
		else:
			action[8] = 6
		return
	raise PyMSError('Parameter',"'%s' is an invalid State (value must be one of the keywords: Set, Clear, Toggle)" % data)

def action_order(trg, decompile, action, strings, properties, data=None):
	"""Order          - One of the keywords: Move, Patrol, Attack"""
	if decompile:
		return unit_orders[action[8]]
	if data in unit_orders:
		action[8] = unit_orders.index(data)
		return
	raise PyMSError('Parameter',"'%s' is an invalid Order (value must be one of the keywords: Move, Patrol, Attack)" % data)

def action_percentage(trg, decompile, action, strings, properties, data=None):
	"""Percentage     - A number from 0 to 100 (with or without a trailing %)"""
	if decompile:
		if action[5] > 100:
			raise
		return '%s%%' % action[2]
	try:
		if data.endswith('%'):
			p = int(data[:-1])
		else:
			p = int(data)
		if -1 < p < 101:
			action[2] = p
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid Percentage (value must be in the range 0 to 100)" % data)

def action_allystatus(trg, decompile, action, strings, properties, data=None):
	"""AllyStatus     - One of the keywords: Enemy, Ally, Allied Victory"""
	if decompile:
		return ally_status[action[6]]
	if data in ally_status:
		action[6] = ally_status.index(data)
		return
	raise PyMSError('Parameter',"'%s' is an invalid AllyStatus (value must be one of the keywords: Enemy, Ally, Allied Victory)" % data)

def action_raw(trg, decompile, action, strings, properties, data=None, place=0):
	"""Raw            - A raw value."""
	if decompile:
		return action[place]
	s = ([4294967296]*6+ [65535,255,255,255])[place]
	try:
		n = int(data)
		if -1 < n < s:
			action[place] = n
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid Raw (value at that position must be in the range 0 to %s)" % (data,s))

#
def new_memory(trg, decompile, action, strings, properties, data=None):
	"""MemoryLocation - A memory location either in hexadecimal (preceded by 0x or h, ex: 0xFF or hFF) or decimal in the range 0 to 4294967295"""
	if decompile:
		return '0x' + hex(action[0])[2:].upper()
	base,s = 10,0
	if data.startswith('0x'):
		base,s = 16,2
	elif data.startswith('h'):
		base,s = 16,1
	try:
		i = int(data[s:], base)
		if -1 < i < 4294967296:
			action[0] = i
	except:
		raise PyMSError('Parameter',"'%s' is an invalid MemoryLocation (value must be hexadecimal or decimal and in the range 0 to 4294967295)" % data)

def new_value(trg, decompile, action, strings, properties, data=None):
	"""NewValue       - A number in the range 0 to 4294967295"""
	if decompile:
		return action[5]
	try:
		n = int(data)
		if -1 < n < 4294967296:
			action[5] = n
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid NewValue (value must be in the range 0 to 4294967295)" % data)

def new_modifier(trg, decompile, action, strings, properties, data=None):
	"""Modifier"""
	if decompile:
		if action[8] == 7:
			return 'Set To'
		elif action[8] == 8:
			return 'Add'
		elif action[8] == 9:
			return 'Subtract'
		raise
	if data in ['Set To', 'Add', 'Subtract']:
		if data == 'Set To':
			action[8] = 7
		elif data == 'Add':
			action[8] = 8
		else:
			action[8] = 9
		return
	raise PyMSError('Parameter',"'%s' is an invalid Modifier (value must be one of the keywords: Set To, Add, Subtract)" % data)

def new_memoryend(trg, decompile, action, strings, properties, data=None):
	"""MemoryLocEnd   - An end memory location either in hexadecimal (preceded by 0x or h, ex: 0xFF or hFF) or decimal in the range 0 to 4294967295"""
	if decompile:
		return '0x' + hex(action[5])[2:].upper()
	base,s = 10,0
	if data.startswith('0x'):
		base,s = 16,2
	elif data.startswith('h'):
		base,s = 16,1
	try:
		i = int(data[s:], base)
		if -1 < i < 4294967296:
			action[5] = i
	except:
		raise PyMSError('Parameter',"'%s' is an invalid MemoryLocEnd (value must be hexadecimal or decimal and in the range 0 to 4294967295)" % data)

def new_location(trg, decompile, action, strings, properties, data=None):
	"""Location"""
	if decompile:
		if action[0] == 64:
			return 'Anywhere'
		return 'Location %s' % (action[0]-1)
	if data == 'Anywhere':
		action[0] = 66
		return
	l = None
	try:
		if data.startswith('Location '):
			l = int(data.split(' ',1)[1])
		else:
			l = int(data)
	except:
		pass
	if l != None and 0 <= l < 255:
		action[0] = l + 1
		return
	raise PyMSError('Parameter',"'%s' is an invalid Location (value must be in the range 0 to 254, or the keyword Anywhere)" % data)

def new_x1(trg, decompile, action, strings, properties, data=None):
	"""NewX1          - The x-coordinate of the top left corner of a location; a number in the range 0 to 4294967295"""
	if decompile:
		return action[1]
	try:
		n = int(data)
		if -1 < n < 4294967296:
			action[1] = n
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid NewX1 (value must be in the range 0 to 4294967295)" % data)

def new_y1(trg, decompile, action, strings, properties, data=None):
	"""NewY1          - The y-coordinate of the top left corner of a location; a number in the range 0 to 4294967295"""
	if decompile:
		return action[3]
	try:
		n = int(data)
		if -1 < n < 4294967296:
			action[3] = n
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid NewY1 (value must be in the range 0 to 4294967295)" % data)

def new_x2(trg, decompile, action, strings, properties, data=None):
	"""NewX2          - The x-coordinate of the bottom right corner of a location; a number in the range 0 to 4294967295"""
	if decompile:
		return action[4]
	try:
		n = int(data)
		if -1 < n < 4294967296:
			action[4] = n
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid NewX2 (value must be in the range 0 to 4294967295)" % data)

def new_y2(trg, decompile, action, strings, properties, data=None):
	"""NewY2          - The y-coordinate of the bottom right corner of a location; a number in the range 0 to 4294967295"""
	if decompile:
		return action[5]
	try:
		n = int(data)
		if -1 < n < 4294967296:
			action[5] = n
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid NewY2 (value must be in the range 0 to 4294967295)" % data)

def new_flags(trg, decompile, action, strings, properties, data=None):
	"""LocationFlags  - The flags to set on a location (6 flags: High Air, Medium Air, Low Air, High Elevation, Medium Elevation, Low Elevation)"""
	if decompile:
		return flags(action[6] ^ 63,6)
	try:
		action[6] = flags(data,6) ^ 63
		return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid LocationFlags (value must be 6 zero's or one's representing the flags)" % data)

def new_properties(trg, decompile, action, strings, properties, data=None):
	"""LocationProps  - The properties to set on a location (5 flags: X1, Y1, X2, Y2, Flags)"""
	if decompile:
		return flags(action[8],5)
	try:
		action[8] = flags(data,5)
		return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid LocationProps (value must be 5 zero's or one's representing the properties to set)" % data)

def new_properties2(trg, decompile, action, strings, properties, data=None):
	"""LocationProps"""
	if decompile:
		return flags(action[5],5)
	try:
		action[5] = flags(data,5)
		return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid LocationProps (value must be 5 zero's or one's representing the properties to set)" % data)

def new_player(trg, decompile, action, strings, properties, data=None): # Same?
	"""Player"""
	if decompile:
		if action[4] < 27:
			return player_ids[action[4]]
		return action[4]
	if data in player_ids:
		action[4] = player_ids.index(data)
		return
	try:
		p = int(data)
		if -1 < p < 256:
			action[4] = p
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid Player (value must be in the range 0 to 255, or on of the keywords: Current Player, Foes, Allies, Neutral Players, All Players, Force 1, Force 2, Force 3, Force 4, Unused 1, Unused 2, Unused 3, Unused 4, Non Allied Victory Players)" % data)

def new_unit(trg, decompile, action, strings, properties, data=None): # Same?
	"""Unit"""
	if decompile:
		if action[6] < 228:
			s = trg.stat_txt.strings[action[6]].split('\x00')
			if s[1] != '*':
				return TBL.decompile_string('\x00'.join(s[:2]), include='(,)')
			else:
				return TBL.decompile_string(s[0], include='(,)')
		return action[6]
	try:
		i = int(data)
		if -1 < i < 65536:
			action[6] = i
			return
	except:
		pass
	for i,name in enumerate(trg.stat_txt.strings[:228]):
		n = name.split('\x00')
		if TBL.compile_string(data) == n[0] or (n[1] != '*' and TBL.compile_string(data) == '\x00'.join(n[:2])):
			action[6] = i
			return
	raise PyMSError('Parameter',"'%s' is an invalid Unit (value must be in the range 0 to 65535, or a full unit name)" % data)

def new_unitend(trg, decompile, action, strings, properties, data=None):
	"""UnitEnd        - A unit ID from 0 to 227 (and extended unit ID's 233 to 65535), a full unit name (in the TBL, its the part before the first <0>)"""
	if decompile:
		if action[0] < 228:
			s = trg.stat_txt.strings[action[0]].split('\x00')
			if s[1] != '*':
				return TBL.decompile_string('\x00'.join(s[:2]), include='(,)')
			else:
				return TBL.decompile_string(s[0], include='(,)')
		return action[0]
	try:
		i = int(data)
		if -1 < i < 65536:
			action[0] = i
			return
	except:
		pass
	for i,name in enumerate(trg.stat_txt.strings[:228]):
		n = name.split('\x00')
		if TBL.compile_string(data) == n[0] or (n[1] != '*' and TBL.compile_string(data) == '\x00'.join(n[:2])):
			action[0] = i
			return
	raise PyMSError('Parameter',"'%s' is an invalid Unit (value must be in the range 0 to 277 and extended units 233 to 65535, or a full unit name)" % data)

def new_playerend(trg, decompile, action, strings, properties, data=None):
	"""PlayerEnd      - A number in the range 0 to 255 (with or without the keyword Player before it), or any keyword from this list: Current Player, Foes, Allies, Neutral Players, All Players, Force 1, Force 2, Force 3, Force 4, Unused 1, Unused 2, Unused 3, Unused 4, Non Allied Victory Players"""
	if decompile:
		if action[5] < 27:
			return player_ids[action[5]]
		return action[5]
	if data in player_ids:
		action[5] = player_ids.index(data)
		return
	try:
		p = int(data)
		if -1 < p < 256:
			action[5] = p
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid Player (value must be in the range 0 to 255, or on of the keywords: Current Player, Foes, Allies, Neutral Players, All Players, Force 1, Force 2, Force 3, Force 4, Unused 1, Unused 2, Unused 3, Unused 4, Non Allied Victory Players)" % data)

def new_math(trg, decompile, action, strings, properties, data=None):
	"""Math           - One of the keywords: Set To, Add, Subtract, Multiply, Divide"""
	if decompile:
		if action[8] == 7:
			return 'Set To'
		elif action[8] == 8:
			return 'Add'
		elif action[8] == 9:
			return 'Subtract'
		elif action[8] == 12:
			return 'Multiply'
		elif action[8] == 13:
			return 'Divide'
		raise
	if data in ['Set To', 'Add', 'Subtract', 'Multiply', 'Divide']:
		if data == 'Set To':
			action[8] = 7
		elif data == 'Add':
			action[8] = 8
		else:
			action[8] = 9
		return
	raise PyMSError('Parameter',"'%s' is an invalid Math operator (value must be one of the keywords: Set To, Add, Subtract, Multiply, Divide)" % data)

def new_stringid(trg, decompile, action, strings, properties, data=None):
	"""StatTxtString  - An ID of a string in stat_txt.tbl."""
	if decompile:
		return action[1]-1
	try:
		i = int(data)
		if -1 < i < len(trg.stat_txt.strings):
			action[1] = i + 1
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid StringID (value must be in the range 0 to %s)" % (data,len(trg.stat_txt.strings)-1))

def new_centered(trg, decompile, action, strings, properties, data=None):
	"""Centered       - One of the keywords: Centered, Uncentered"""
	if decompile:
		return ['Uncentered','Centered'][action[8]]
	try:
		action[8] = ['Uncentered','Centered'].index(data)
		return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid Centered value (value must be one of the keywords: Centered, Uncentered)" % data)

def new_speed(trg, decompile, action, strings, properties, data=None):
	"""GameSpeed      - The speed of the game (value must be one of the keywords: Slowest, Slower, Slow, Normal, Fast, Faster, Fastest)"""
	if decompile:
		return ['Slowest','Slower','Slow','Normal','Fast','Faster','Fastest'][action[0]]
	try:
		action[0] = ['Slowest','Slower','Slow','Normal','Fast','Faster','Fastest'].index(data)
		return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid Speed (value must be one of the keywords: Slowest, Slower, Slow, Normal, Fast, Faster, Fastest)" % data)

def new_multiplier(trg, decompile, action, strings, properties, data=None):
	"""Multiplayer    - One of the values 2, 4, 8, 16, 32 (with or without an x attached to the front)."""
	if decompile:
		return 'x%s' % action[1]
	try:
		if data.startswith('x'):
			action[1] = int(data[1:])
		else:
			action[1] = int(data)
		return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid Multiplier (value must be 2, 4, 8, 16, 32 and can be proceded by a x)" % data)

def new_racevalue(trg, decompile, action, strings, properties, data=None):
	"""SupplyType     - The supply type to edit (value must be one of the keywords: Zerg Available, Zerg Used, Zerg Max, Terran Available, Terran Used, Terran Max, Protoss Available, Protoss Used, Protoss Max)"""
	l = ['Zerg Available','Zerg Used','Zerg Max','Terran Available','Terran Used','Terran Max','Protoss Available','Protoss Used','Protoss Max']
	if decompile:
		return l[action[6]]
	try:
		action[6] = l.index(data)
		return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid SupplyType (value must be one of the keywords: Zerg Available, Zerg Used, Zerg Max, Terran Available, Terran Used, Terran Max, Protoss Available, Protoss Used, Protoss Max)" % data)

def new_unittype(trg, decompile, action, strings, properties, data=None):# Same?
	"""TUnit"""
	if decompile:
		if -1 < action[6] < 228:
			s = trg.stat_txt.strings[action[6]].split('\x00')
			if s[1] != '*':
				return TBL.decompile_string('\x00'.join(s[:2]), include='(,)')
			else:
				return TBL.decompile_string(s[0], include='(,)')
		if action[6] < 233:
			return unit_types[action[6] - 228]
		return action[6]
	if data in unit_types:
		action[6] = unit_types.index(data) + 228
		action[9] ^= 16
		return
	try:
		i = int(data)
		if -1 < i < 65536:
			action[6] = i
			return
	except:
		pass
	for i,name in enumerate(trg.stat_txt.strings[:228]):
		n = name.split('\x00')
		if TBL.compile_string(data) == n[0] or (n[1] != '*' and TBL.compile_string(data) == '\x00'.join(n[:2])):
			action[6] = i
			return
	raise PyMSError('Parameter',"'%s' is an invalid TUnit value must be in the range 0 to 227 (and extended units 233 to 65535), a full unit name, or a type from the list: None, Any Unit, Men, Buildings, Factories)" % data)

def new_unittypeend(trg, decompile, action, strings, properties, data=None):
	"""TUnitEnd       - A unit ID from 0 to 227 (and extended units 233 to 65535), a full unit name (in the TBL, its the part before the first <0>), or a type from the list: None, Any Unit, Men, Buildings, Factories"""
	if decompile:
		if -1 < action[3] < 228:
			s = trg.stat_txt.strings[action[3]].split('\x00')
			if s[1] != '*':
				return TBL.decompile_string('\x00'.join(s[:2]), include='(,)')
			else:
				return TBL.decompile_string(s[0], include='(,)')
		if action[6] < 233:
			return unit_types[action[3] - 228]
		return action[3]
	if data in unit_types:
		action[3] = unit_types.index(data) + 228
		action[9] ^= 16
		return
	try:
		i = int(data)
		if -1 < i < 65536:
			action[3] = i
			return
	except:
		pass
	for i,name in enumerate(trg.stat_txt.strings[:228]):
		n = name.split('\x00')
		if TBL.compile_string(data) == n[0] or (n[1] != '*' and TBL.compile_string(data) == '\x00'.join(n[:2])):
			action[6] = i
			return
	raise PyMSError('Parameter',"'%s' is an invalid TUnit value must be in the range 0 to 227 (and extended units 233 to 65535), a full unit name, or a type from the list: None, Any Unit, Men, Buildings, Factories)" % data)

def new_orderid(trg, decompile, action, strings, properties, data=None):
	"""OrderID        - The ID of the order to give the unit (A value in the range 0 to 188)"""
	if decompile:
		return action[8]
	try:
		n = int(data)
		if -1 < n < 188:
			action[8] = n
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid OrderID (value must be in the range 0 to 188)" % data)

def new_locationend(trg, decompile, action, strings, properties, data=None):
	"""EndLocation    - A number in the range 0 to 254 (with or without the keyword Location before it), or the keyword Anywhere (Anywhere is Location 63)"""
	if decompile:
		if action[5] == 66:
			return 'Anywhere'
		return 'Location %s' % (action[5]-1)
	if data == 'Anywhere':
		action[5] = 66
		return
	l = None
	try:
		if data.startswith('Location '):
			l = int(data.split(' ',1)[1])
		else:
			l = int(data)
	except:
		pass
	if l != None and 0 <= l < 255:
		action[5] = l + 1
		return
	raise PyMSError('Parameter',"'%s' is an invalid EndLocation (value must be in the range 0 to 254, or the keyword Anywhere, which is Location 63)" % data)

def new_x(trg, decompile, action, strings, properties, data=None):
	"""NewX           - The x-coordinate of the target; a number in the range 0 to 4294967295"""
	if decompile:
		return action[1]
	try:
		n = int(data)
		if -1 < n < 4294967296:
			action[1] = n
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid NewX (value must be in the range 0 to 4294967295)" % data)

def new_y(trg, decompile, action, strings, properties, data=None):
	"""NewY           - The y-coordinate of the target; a number in the range 0 to 4294967295"""
	if decompile:
		return action[3]
	try:
		n = int(data)
		if -1 < n < 4294967296:
			action[3] = n
			return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid NewY (value must be in the range 0 to 4294967295)" % data)

def new_vision(trg, decompile, action, strings, properties, data=None):
	"""Vision         - One of the keywords: Turn On, Turn Off, Toggle"""
	if decompile:
		if action[8] == 4:
			return 'Turn Off'
		elif action[8] == 5:
			return 'Turn On'
		elif action[8] == 6:
			return 'Toggle'
	try:
		action[8] = ['Turn Off','Turn On', 'Toggle'].index(data) + 4
		return
	except:
		pass
	raise PyMSError('Parameter',"'%s' is an invalid Vision value (value must be one of the keywords: Turn Off, Turn On, Toggle)" % data)
#
class TRG:
	conditions = [
		'NoCondition',
		'CountdownTimer',
		'Command',
		'Bring',
		'Accumulate',
		'Kill',
		'CommandTheMost',
		'CommandsTheMostAt',
		'MostKills',
		'HighestScore',
		'MostResources',
		'Switch',
		'ElapsedTime',
		None, #Used to signify Mission Briefing. Unused in .TRG files.
		'Opponents',
		'Deaths',
		'CommandTheLeast',
		'CommandTheLeastAt',
		'LeastKills',
		'LowestScore',
		'LeastResources',
		'Score',
		'Always',
		'Never',

		'RawCond', # Not actually a condition
	]
	condition_parameters = [
		None,
		[condition_comparison, condition_number],
		[condition_player, condition_comparison, condition_number, condition_tunit],
		[condition_player, condition_comparison, condition_number, condition_tunit, condition_location],
		[condition_player, condition_comparison, condition_number, condition_restype],
		[condition_player, condition_comparison, condition_number, condition_tunit],
		[condition_tunit],
		[condition_tunit, condition_location],
		[condition_tunit],
		[condition_score],
		[condition_restype],
		[condition_switch, condition_set],
		[condition_comparison, condition_number],
		None,
		[condition_player, condition_comparison, condition_number],
		[condition_player, condition_tunit, condition_comparison, condition_number],
		[condition_tunit],
		[condition_tunit, condition_location],
		[condition_tunit],
		[condition_score],
		[condition_restype],
		[condition_player, condition_comparison, condition_number, condition_score],
		None,
		None,

		[lambda s,f,d,c,p=n: condition_raw(s,f,d,c,p) for n in range(8)]
	]
	actions = [
		'NoAction',
		'Victory',
		'Defeat',
		'PreserveTrigger',
		'Wait',
		'PauseGame',
		'UnpauseGame',
		'Transmission',
		'PlayWAV',
		'DisplayTextMessage',
		'CenterView',#10
		'CreateUnitWithProperties',
		'SetMissionObjectives',
		'SetSwitch',
		'SetCountdownTimer',
		'RunAIScript',
		'RunAIScriptAtLocation',
		'LeaderBoardControl',
		'LeaderBoardControlAtLocation',
		'LeaderBoardResources',
		'LeaderBoardKills',#20
		'LeaderBoardPoints',
		'KillUnit',
		'KillUnitsAtLocation',
		'RemoveUnit',
		'RemoveUnitAtLocation',
		'SetResources',
		'SetScore',
		'MinimapPing',
		'TalkingPortrait',
		'MuteUnitSpeech',#30
		'UnmuteUnitSpeech',
		'LeaderboardComputerPlayers',
		'LeaderboardGoalControl',
		'LeaderboardGoalControlAtLocation',
		'LeaderboardGoalResources',
		'LeaderboardGoalKills',
		'LeaderboardGoalPoints',
		'MoveLocation',
		'MoveUnit',
		'LeaderboardGreed',#40
		'SetNextScenario',
		'SetDoodadState',
		'SetInvincibility',
		'CreateUnit',
		'SetDeaths',
		'Order',
		'Comment',
		'GiveUnitstoPlayer',
		'ModifyUnitHitPoints',
		'ModifyUnitEnergy',#50
		'ModifyUnitShieldPoints',
		'ModifyUnitResourceAmount',
		'ModifyUnitHangerCount',
		'PauseTimer',
		'UnpauseTimer',
		'Draw',
		'SetAllianceStatus',
		'DisableDebugMode',
		'EnableDebugMode',#59,

		'RawAct', # Not actually a condition
	]
	action_parameters = [
		None,
		None,
		None,
		None,
		[action_time],
		None,
		None,
		[action_string, action_wav, action_time, action_unit, action_location, action_modifier, action_time],
		[action_wav, action_time],
		[action_string, action_display],
		[action_location],
		[action_player, action_number, action_unit, action_location, action_property],
		[action_string],
		[action_switch, action_switchaction],
		[action_modifier, action_time],
		[action_aiscript],
		[action_aiscript_loc, action_location],
		[action_dstring, action_tunit],
		[action_dstring, action_tunit, action_location],
		[action_dstring, action_restype],
		[action_dstring, action_tunit],
		[action_dstring, action_score],
		[action_player, action_tunit],
		[action_player, action_qnumber, action_tunit, action_location],
		[action_player, action_tunit],
		[action_player, action_qnumber, action_tunit, action_location],
		[action_player, action_modifier, action_number, action_restype],
		[action_player, action_modifier, action_number, action_score],
		[action_location],
		[action_unit, action_time],
		None,
		None,
		[action_state],
		[action_dstring, action_number, action_tunit],
		[action_dstring, action_number, action_tunit, action_location],
		[action_dstring, action_number, action_tunit, action_restype],
		[action_dstring, action_number, action_tunit],
		[action_dstring, action_number, action_score],
		[action_player, action_tunit, action_location, action_destlocation],
		[action_player, action_qnumber, action_tunit, action_location, action_destlocation],
		[action_number],
		[action_string],
		[action_player, action_tunit, action_location, action_state],
		[action_player, action_tunit, action_location, action_state],
		[action_player, action_number, action_unit, action_location],
		[action_player, action_tunit, action_modifier, action_number],
		[action_player, action_tunit, action_location, action_order, action_destlocation],
		[action_string],
		[action_player, action_destplayer, action_qnumber, action_tunit, action_location],
		[action_player, action_qnumber, action_tunit, action_location, action_percentage],
		[action_player, action_qnumber, action_tunit, action_location, action_percentage],
		[action_player, action_qnumber, action_tunit, action_location, action_percentage],
		[action_player, action_qnumber, action_location, action_number],
		[action_player, action_qnumber, action_tunit, action_location, action_number],
		None,
		None,
		None,
		[action_player, action_allystatus],
		None,
		None,

		[lambda s,f,d,a,l,e,p=n: action_raw(s,f,d,a,l,e,p) for n in range(10)]
	]

  # New Trigger Actions
  # case 12: // SetUnitTargetToUnit 
  # // Location = Location ID 
  # // Text     = Target Owner 
  # // Time     = Target Unit 
  # // Player   = Owner 
  # // Dest     = Target Location 
  # // Type     = Unit

  # case 13: // SetUnitTargetToLocation 
  # // Location = Location ID 
  # // Player   = Owner
  # // Dest     = Target Location
  # // Type     = Unit

  # case 14: // SetUnitTarget 
  # // Location = Location ID 
  # // Text     = Target X 
  # // Time     = Target Y
  # // Player   = Owner
  # // Type     = Unit

  # case 15: // SetUnitHP 
  # // Location = Location ID 
  # // Player   = Owner 
  # // Dest     = Amount
  # // Type     = Unit Type
  # // Modifier = Set, Add, Subtract

  # case 16: // SetUnitShields 
  # // Location = Location ID 
  # // Player   = Owner 
  # // Dest     = Amount
  # // Type     = Unit Type
  # // Modifier = Set, Add, Subtract
	new_conditions = []
	new_condition_parameters = []
	new_actions = [
		None, # Indexed by 1
		'SetMemoryLocation',
		'SetDuoMemoryLocation',
		'SetLocationTo',
		'SetLocationFromDeath',
		'DCMath',
		'DisplayStatTxtString',
		None, #(Reserved)
		None, #(Reserved)
		'SetGameSpeed',
		'SetSupplyValue',
		'SendUnitOrder',
		'SetUnitTargetToUnit',
		'SetUnitTargetToLocation',
		'SetUnitTargetToCoords',
		'SetUnitHP',
		'SetUnitShields',
		'SetPlayerVision',
	]
	new_action_parameters = [
		None, # Indexed by 1
		# New Trigger Actions
		[new_memory,new_modifier,new_value],
		[new_memory,new_modifier,new_memoryend],
		[new_location,new_x1,new_y1,new_x2,new_y2,new_flags,new_properties],
		[new_location,new_modifier,new_unit,new_player,new_properties2],
		[new_unit,new_player,new_math,new_unitend,new_playerend],
		[new_stringid],#,new_centered],
		None,
		None,
		[new_speed,new_multiplier],
		[new_player,new_value,new_modifier,new_racevalue],
		[new_location,new_unittype,new_player,new_orderid],
		[new_location,new_unittype,new_player,new_locationend,new_unittypeend,new_playerend],
		[new_location,new_unittype,new_player,new_locationend],
		[new_location,new_unittype,new_player,new_x,new_y],
		[new_location,new_unittype,new_player,new_modifier,new_value],
		[new_location,new_unittype,new_player,new_modifier,new_value],
		[new_player,new_vision,new_playerend],
	]
	longlabel = 17

	def __init__(self, stat_txt=None, aiscript=None):
		if isinstance(stat_txt, TBL.TBL):
			self.stat_txt = stat_txt
		else:
			if stat_txt == None:
				stat_txt = os.path.join(BASE_DIR,'Libs', 'MPQ', 'rez', 'stat_txt.tbl')
			self.stat_txt = TBL.TBL()
			self.stat_txt.load_file(stat_txt)
		if isinstance(aiscript, AIBIN.AIBIN):
			ais = aiscript
		else:
			if aiscript == None:
				aiscript = os.path.join(BASE_DIR,'Libs', 'MPQ', 'scripts', 'aiscript.bin')
			ais = AIBIN.AIBIN(stat_txt=stat_txt)
			ais.load_file(aiscript)
		self.triggers = []
		self.strings = {}
		self.properties = {}
		# aiscript - ai, ailoc
		# bwscript - ai, ailoc
		self.ais = [[odict(),odict()],[odict(),odict()]]
		self.ais_rev = [[odict(),odict()],[odict(),odict()]]
		# self.ais = [[{},{}],[{},{}]]
		# self.ais_rev = [[{},{}],[{},{}]]
		for name,data in ais.ais.iteritems():
			string = TBL.decompile_string(self.stat_txt.strings[data[1]].split('\x00',1)[0])
			self.ais[not not data[2] & 4][data[2] & 1][name] = string
			self.ais_rev[not not data[2] & 4][data[2] & 1][string] = name
		self.dynamic_conditions = {}
		self.dynamic_actions = {}

		for r in REGISTER:
			r(self)

	def load_file(self, file, TRIG=False):
		try:
			if isstr(file):
				f = open(file,'rb')
				data = f.read()
				f.close()
			else:
				data = file.read()
		except:
			raise PyMSError('Load',"Could not load TRG '%s'" % file)
		try:
			offset = 0
			if not TRIG:
				if data[:8] != 'qw\x986\x18\x00\x00\x00':
					raise PyMSError('Load',"'%s' is not a TRG file (no TRG header). It could possibly be a .got TRG file, try using the -t option when decompiling" % file)
				offset = 8
			triggers = []
			strings = {}
			properties = {}
			findnext = []
			while offset < len(data):
				if not findnext:
					conditions = []
					for c in range(16):
						condition = struct.unpack('<3LH4B', data[offset:offset+18])
						if c and not condition[5]:
							break
						## New Trigger Actions
						# if condition[7] == 23 and condtion[2] != 0:
							# if self.new_condition_parameters[condition[2]]:
								# for parameter in self.new_condition_parameters[condition[2]]:
									# parameter(self, True, condition, {}, {})
						## Dynamic Trigger Actions
						# elif condition[5] == 22 and condition[2] != 0:
							# if self.dynamic_conditions[condition[2]][1]:
								# for parameter in self.dynamic_conditions[condition[2]][1]:
									# parameter(self, True, condition, {}, {})
						# else:
							# if self.condition_parameters[condition[5]]:
								# for parameter in self.condition_parameters[condition[5]]:
									# parameter(self, True, condition)
						conditions.append(list(condition))
						offset += 20
					offset += 20 * (16 - len(conditions))
					actions = []
					for a in range(64):
						action = struct.unpack('<6LH3B', data[offset:offset+29])
						if a and not action[7]:
							break
						## New Trigger Actions
						# if action[7] == 58 and action[2] != 0:
							# if self.new_action_parameters[action[2]]:
								# for parameter in self.new_action_parameters[action[2]]:
									# parameter(self, True, action, {}, {})
						## Dynamic Trigger Actions
						# elif action[7] == 59 and action[2] != 0:
							# if self.dynamic_actions[action[2]][1]:
								# for parameter in self.dynamic_actions[action[2]][1]:
									# parameter(self, True, action, {}, {})
						# else:
							# if not TRIG:
								# if action[1]:
									# findnext.append([True,action[1]])
								# if action[7] == 11 and action[9] & 8:
									# findnext.append([False,action[5]])
							# if self.action_parameters[action[7]]:
								# for parameter in self.action_parameters[action[7]]:
									# parameter(self, True, action, {}, {})
						if not TRIG:
							if action[1]:
								findnext.append([True,action[1]])
							if action[7] == 11 and action[9] & 8:
								findnext.append([False,action[5]])
						actions.append(list(action))
						offset += 32
					offset += 32 * (64 - len(actions))
					if not conditions == [[0,0,0,0,0,0,0,0]] or not actions == [[0,0,0,0,0,0,0,0,0,0]]:
						triggers.append([list(struct.unpack('<4x28B', data[offset:offset+32])),conditions,actions])
					offset += 32
				else:
					if findnext[0][0]:
						strings[findnext[0][1]] = data[offset:offset+2048].split('\x00',1)[0]
						if len(strings[findnext[0][1]]) < 2048:
							strings[findnext[0][1]] += '\x00'
						offset += 2048
					else:
						properties[findnext[0][1]] = list(struct.unpack('<HH4BLHH', data[offset:offset+16]))
						offset += 20
					del findnext[0]
			# d = open('trgdebug.txt','w')
			# for t in triggers:
				# d.write(str(t) + '\n')
			# d.close()
			self.triggers = triggers
			self.strings = strings
			self.properties = properties
		except PyMSError:
			raise
		except:
			raise PyMSError('Load',"Unsupported TRG file '%s', could possibly be corrupt" % file)

	def interpret(self, file): 
		if isstr(file):
			try:
				f = open(file,'r')
				data = f.readlines()
				f.close()
			except:
				raise PyMSError('Interpreter',"Could not load file '%s'" % file)
		else:
			data = file.readlines()
			try:
				file = file.file
			except:
				pass
		rev_dynamic_conditions = {}
		for i,c in self.dynamic_conditions.iteritems():
			rev_dynamic_conditions[c[0]] = i
		rev_dynamic_actions = {}
		for i,a in self.dynamic_actions.iteritems():
			rev_dynamic_actions[a[0]] = i
		loaded = []
		if isstr(file):
			loaded.append(file)
		warnings = []
		triggers = []
		strings = {}
		properties = {}
		constants = {}
		conditions = {}
		actions = {}
		def param_constant(o):
			if o.group(1) in constants:
				return constants[o.group(1)]
			return o.group(0)
		# 0  = Nothing, 1 = String, 2 = Property
		# 3  = Trigger, 4 = Conditions, 5 = End Conditions, 6 = Actions
		# 7  = Constant, 8 = Conditions Function, 9 = Actions Function
		# 10 = End Actions, 11 = End Actions Function, 12 = End Conditions Function
		def include(ddata):
			id = 0
			state = 0
			for n,l in enumerate(ddata):
				if l:
					line = l.strip().split('#',1)[0]
					if line:
						#print '%s : %s' % (state,line)
						if state == 1:
							if l.endswith('\n'):
								l = l[:-1]
							strings[id] += TBL.compile_string(l).split('\x00')[0]
							if len(strings[id]) > 2047:
								raise PyMSError('Interpreter',"String '%s' is too long (max length is 2048 characters)" % id,n,line)
							if re.match('.*<0+>.*', l):
								state = 0
								strings[id] += '\x00'
							else:
								strings[id] += '\n'
							continue
						elif state == 2:
							match = re.match('\\A(.+)\\((.+)\\)\\s*\\Z', line)
							if match:
								cmd = match.group(1)
								dat = match.group(2)
								if cmd == 'ValidProperties':
									if properties[id][0] != None:
										raise PyMSError('Interpreter',"Property '%s' has more then one ValidProperties setting" % id,n,line)
									properties[id][0] = 0
									if dat:
										params = re.split('\\s*,\\s*', dat)
										for param in params:
											if not param in unit_properties:
												raise PyMSError('Interpreter',"Property '%s' has an invalid ValidProperties value: '%s'" % (id,param),n,line)
											properties[id][0] ^= 2 ** unit_properties.index(param)
								elif cmd == 'ValidUnitData':
									if properties[id][1] != None:
										raise PyMSError('Interpreter',"Property '%s' has more then one ValidUnitData setting" % id,n,line)
									properties[id][1] = 0
									if dat:
										params = re.split('\\s*,\\s*', dat)
										for param in params:
											if not param in unit_data:
												raise PyMSError('Interpreter',"Property '%s' has an invalid ValidUnitData value: '%s'" % (id,param),n,line)
											properties[id][1] ^= 2 ** unit_data.index(param)
									for n in range(6):
										if not properties[id][1] & (2 ** n):
											properties[id][2 + n] = 0
								elif cmd == 'Properties':
									if properties[id][0] == None:
										raise PyMSError('Interpreter',"Property '%s' is trying to set the Properties before declaring the ValidProperties" % id,n,line)
									if properties[id][8] != None:
										raise PyMSError('Interpreter',"Property '%s' has more then one Properties setting" % id,n,line)
									properties[id][8] = 0
									if dat:
										params = re.split('\\s*,\\s*', dat)
										for param in params:
											if not param in unit_properties:
												raise PyMSError('Interpreter',"Property '%s' has an invalid Properties value: '%s'" % (id,param),n,line)
											properties[id][8] ^= 2 ** unit_properties.index(param)
								elif cmd in unit_data:
									if properties[id][1] == None:
										raise PyMSError('Interpreter',"Property '%s' is trying to set some unit data before declaring the ValidUnitData" % id,n,line)
									if properties[id][unit_data.index(cmd) + 2] != None:
										raise PyMSError('Interpreter',"Property '%s' has more then on %s setting" % (id,cmd),n,line)
									if cmd in ['Owner', 'Resources', 'AmountInHanger', 'Unknown']:
										try:
											d = int(dat)
										except:
											raise PyMSError('Interpreter',"Property '%s' has an invalid %s value: '%s'" % (id,cmd,dat),n,line)
										if cmd == 'Resources' and (-1 > p or 4294967295 < p):
											raise PyMSError('Interpreter',"Property '%s' has an invalid Resources value: '%s' (Must be a value between 0 and 4294967295)" % (id,p),n,line)
										elif cmd == 'AmountInHanger' and (-1 > p or 10 < p):
											raise PyMSError('Interpreter',"Property '%s' has an invalid AmountInHanger value: '%s' (Must be a value between 0 and 10)" % (id,p),n,line)
									elif cmd in ['Health','Shields','Energy']:
										try:
											if dat.endswith('%'):
												d = int(dat[:-1])
											else:
												d = int(dat)
										except:
											raise PyMSError('Interpreter',"Property '%s' has an invalid %s value: '%s'" % (id,cmd,dat),n,line)
										if -1 > d or 100 < d:
											raise PyMSError('Interpreter',"Property '%s' has an invalid %s value: '%s' (Must be a value between 0 and 100)" % (id,cmd,p),n,line)
									properties[id][unit_data.index(cmd) + 2] = d
								else:
									raise PyMSError('Interpreter',"Property '%s' has an unknown line format" % id,n,line)
								if not None in properties[id]:
									state = 0
							else:
								raise PyMSError('Interpreter',"Property '%s' has an unknown line format" % id,n,line)
							continue
						elif state == 3:
							if line != 'Conditions:':
								raise PyMSError('Interpreter',"Unexpected line, expected 'Conditions:'",n,line)
							state = 4
							continue
						elif state in [4,8]:
							if state == 4 and line == 'Actions:':
								state = 6
								continue
							cont = True
							for r in ['\\AString (\\d+):\\s*\\Z','\\AProperty (\\d+):\\s*\\Z','\\ATrigger(.+):\\s*\\Z','\\AConstant ([^\s]+):\\s*\\Z','\\AConditions ([^\s]+):\\s*\\Z','\\AActions ([^\s]+):\\s*\\Z']:
								match = re.match(r, line)
								if match:
									if state != 8:
										raise PyMSError('Interpreter',"Unexpected line, expected a condition or 'Actions:'",n,line)
									cont = False
									break
							if cont:
								match = re.match('\\A(-)?(.+)\\((.+)?\\)\\s*\\Z', line)
								if match:
									condition = [0]*8
									if match.group(1):
										condition[7] ^= 2
									cmd = match.group(2)
									if cmd in conditions:
										if state == 8:
											raise PyMSError('Interpreter',"You can not access a Condition Function inside another Condition Function",n,line)
										if len(triggers[-1][1]) + len(conditions[cmd]) > 16:
											raise PyMSError('Interpreter',"The Condition Function '%s' makes the trigger have over 16 conditions" % cmd,n,line)
										triggers[-1][1].extend(conditions[cmd])
									else:
										dat = []
										if match.group(3):
											dat = re.split('\\s*,\\s*', re.sub('\\{([^}\s]+)\\}', param_constant, match.group(3)))
										if not cmd in self.conditions and not cmd in self.new_conditions and not cmd in rev_dynamic_conditions:
											raise PyMSError('Interpreter',"'%s' is an invalid condition" % cmd,n,line)
										if cmd in self.conditions:
											condition[5] = self.conditions.index(cmd)
											params = self.condition_parameters[condition[5]]
										elif cmd in self.new_conditions:
											condition[5] = 23
											params = self.new_condition_parameters[self.new_conditions.index(cmd)]
										else:
											condition[5] = 22
											params = self.dynamic_conditions[rev_dynamic_conditions[cmd]][1]
										if params and len(dat) != len(params):
											raise PyMSError('Interpreter',"Incorrect parameter amount for condition '%s' (expected %s, got %s)" % (cmd,len(params),len(dat)),n,line)
										elif not params and dat:
											raise PyMSError('Interpreter',"The condition '%s' takes no paramaters, but got %s" % (cmd,len(dat)),n,line)
										elif params and dat:
											for d,param in zip(dat,params):
												try:
													param(self, False, condition, d)
												except PyMSError, e:
													e.line = n + 1
													e.code = line
													raise
										if cmd in self.new_conditions:
											condition[2] = self.new_conditions.index(cmd)
										elif cmd in rev_dynamic_actions:
											condition[2] = rev_dynamic_conditions[cmd]
										if state == 8:
											conditions[id].append(condition)
										else:
											triggers[-1][1].append(condition)
									if state == 9 and len(conditions[id]) == 16:
										state = 12
									elif state != 9 and len(triggers[-1][1]) == 16:
										state = 5
								else:
									raise PyMSError('Interpreter',"Unexpected line, expected a condition",n,line)
								continue
						elif state == 5:
							if line != 'Actions:':
								raise PyMSError('Interpreter',"Too many conditions in trigger (max is 16), expected 'Actions:'",n,line)
							state = 6
							continue
						elif state == 12:
							cont = True
							for r in ['\\AString (\\d+):\\s*\\Z','\\AProperty (\\d+):\\s*\\Z','\\ATrigger(.+):\\s*\\Z','\\AConstant ([^\s]+):\\s*\\Z','\\AConditions ([^\s]+):\\s*\\Z','\\AActions ([^\s]+):\\s*\\Z']:
								match = re.match(r, line)
								if match:
									cont = False
									break
							if cont:
								raise PyMSError('Interpreter',"Too many conditions in Conditions Function (max is 16)",n,line)
						elif state in [6,9,10,11]:
							cont = True
							for r in ['\\AString (\\d+):\\s*\\Z','\\AProperty (\\d+):\\s*\\Z','\\ATrigger(.+):\\s*\\Z','\\AConstant ([^\s]+):\\s*\\Z','\\AConditions ([^\s]+):\\s*\\Z','\\AActions ([^\s]+):\\s*\\Z']:
								match = re.match(r, line)
								if match:
									cont = False
									break
							if cont:
								match = re.match('\\A(-)?(.+)\\((.+)?\\)\\s*\\Z', line)
								if match:
									if state == 10:
										raise PyMSError('Interpreter',"Too many actions in trigger (max is 64)",n,line)
									elif state == 11:
										raise PyMSError('Interpreter',"Too many actions in Action Function (max is 64)",n,line)
									action = [0]*10
									if match.group(1):
										action[9] ^= 2
									cmd = match.group(2)
									if cmd in actions:
										if state == 9:
											raise PyMSError('Interpreter',"You can not access an Action Function inside another Action Function",n,line)
										if len(triggers[-1][2]) + len(actions[cmd]) > 64:
											raise PyMSError('Interpreter',"The Action Function '%s' makes the trigger have more then 64 actions" % cmd,n,line)
										triggers[-1][2].extend(actions[cmd])
									else:
										dat = []
										if match.group(3):
											dat = re.split('\\s*,\\s*', re.sub('\\{([^}\s]+)\\}', param_constant, match.group(3)))
										if not cmd in self.actions and not cmd in self.new_actions and not cmd in rev_dynamic_actions:
											raise PyMSError('Interpreter',"'%s' is an invalid action" % cmd,n,line)
										if cmd in self.actions:
											action[7] = self.actions.index(cmd)
											params = self.action_parameters[action[7]]
										elif cmd in self.new_actions:
											action[7] = 58
											params = self.new_action_parameters[self.new_actions.index(cmd)]
										else:
											action[7] = 59
											params = self.dynamic_actions[rev_dynamic_actions[cmd]][1]
										if params and len(dat) != len(params):
											raise PyMSError('Interpreter',"Incorrect parameter amount for action '%s' (expected %s, got %s)" % (cmd,len(params),len(dat)),n,line)
										if not params and dat:
											raise PyMSError('Interpreter',"The action '%s' takes no paramaters, but got %s" % (cmd,len(dat)),n,line)
										elif params and dat:
											for d,param in zip(dat,params):
												try:
													param(self, False, action, strings, properties, d)
												except PyMSError, e:
													e.line = n + 1
													e.code = line
													raise
										if cmd in self.new_actions:
											action[2] = self.new_actions.index(cmd)
										elif cmd in rev_dynamic_actions:
											action[2] = rev_dynamic_actions[cmd]
										if state == 9:
											actions[id].append(action)
										else:
											triggers[-1][2].append(action)
									if state == 9 and len(actions[id]) == 64:
										state = 11
									elif state != 9 and len(triggers[-1][2]) == 64:
										state = 10
								else:
									raise PyMSError('Interpreter',"Unexpected line, expected an action",n,line)
								continue
						elif state == 7:
							if l.endswith('\n'):
								l = l[:-1]
							constants[id] = l
							state = 0
							continue
						match = re.match('\\Ainclude\\s*(.+)\\Z', line)
						if match:
							try:
								inc = os.path.join(os.path.dirname(file),match.group(1))
							except:
								inc = os.path.abspath(match.group(1))
							if inc in loaded:
								continue
							try:
								d = open(inc,'r')
								dd = d.readlines()
								d.close()
							except:
								raise PyMSError('Include',"The include '%s' was not found" % inc, warnings=warnings)
							loaded.append(inc)
							include(dd)
							continue
						match = re.match('\\AString (\\d+):\\s*\\Z', line)
						if match:
							try:
								id = int(match.group(1))
							except:
								raise PyMSError('Interpreter',"Invalid string number '%s'" % match.group(1),n,line)
							if id in strings:
								raise PyMSError('Interpreter',"There is already a string with id number '%s'" % id,n,line)
							strings[id] = ''
							state = 1
							continue
						match = re.match('\\AProperty (\\d+):\\s*\\Z', line)
						if match:
							try:
								id = int(match.group(1))
							except:
								raise PyMSError('Interpreter',"Invalid property number '%s'" % match.group(1),n,line)
							if id in properties:
								raise PyMSError('Interpreter',"There is already a property with id number '%s'" % id,n,line)
							properties[id] = [None]*9
							state = 2
							continue
						match = re.match('\\ATrigger\\((.+)\\):\\s*\\Z', line)
						if match:
							triggers.append([[0]*28,[],[]])
							params = re.split('\\s*,\\s*', match.group(1))
							for param in params:
								if not param in player_ids:
									raise PyMSError('Interpreter',"Invalid player id '%s'" % param,n,line)
								triggers[-1][0][player_ids.index(param)] = 1
							state = 3
							continue
						match = re.match('\\AConstant ([^\s]+):\\s*\\Z', line)
						if match:
							id = match.group(1)
							state = 7
							continue
						match = re.match('\\AConditions ([^\s]+):\\s*\\Z', line)
						if match:
							id = match.group(1)
							if id in self.conditions:
								raise PyMSError('Interpreter',"'%s' is already a condition name" % id,n,line)
							elif id in conditions:
								raise PyMSError('Interpreter',"'%s' is already a Condition Function name" % id,n,line)
							conditions[id] = []
							state = 8
							continue
						match = re.match('\\AActions ([^\s]+):\\s*\\Z', line)
						if match:
							id = match.group(1)
							if id in self.actions:
								raise PyMSError('Interpreter',"'%s' is already an action name" % id,n,line)
							elif id in self.actions:
								raise PyMSError('Interpreter',"'%s' is already an Action Function name" % id,n,line)
							actions[id] = []
							state = 9
							continue
						raise PyMSError('Interpreting','Invalid syntax, unknown line format',n,line)
		include(data)
		self.triggers = triggers
		self.strings = strings
		self.properties = properties

	def reference(self, file):
		file.write('#----------------------------------------------------\n# Parameter Types:\n')
		done = []
		for p in self.condition_parameters + self.action_parameters:
			if p:
				for t in p:
					if t:
						n = t.__doc__.split(' ',1)[0]
						if not n in done:
							file.write('#    %s\n' % t.__doc__)
							done.append(n)
		file.write('#\n# Conditions:\n')
		for c,ps in zip(self.conditions,self.condition_parameters):
			if c:
				file.write('#    %s(' % c)
				if ps:
					comma = False
					for p in ps:
						if comma:
							file.write(', ')
						else:
							comma = True
						file.write(p.__doc__.split(' ',1)[0])
				file.write(')\n')
		file.write('#\n# Actions:\n')
		for c,ps in zip(self.actions,self.action_parameters):
			file.write('#    %s(' % c)
			if ps:
				comma = False
				for p in ps:
					if comma:
						file.write(', ')
					else:
						comma = True
					file.write(p.__doc__.split(' ',1)[0])
			file.write(')\n')
		if self.ais[0][0] or self.ais[1][0]:
			file.write('#\n# AIScripts (Without Location):\n')
			for name,string in self.ais[0][0].iteritems():
				file.write('#    %s    |    %s\n' % (name, string))
			if self.ais[1][0]:
				file.write('#        -- BroodWar Only --\n')
				for name,string in self.ais[1][0].iteritems():
					file.write('#    %s    |    %s\n' % (name, string))
		if self.ais[0][1] or self.ais[1][1]:
			file.write('#\n# AIScripts (Requires a Location):\n')
			for name,string in self.ais[0][1].iteritems():
				file.write('#    %s    |    %s\n' % (name, string))
			if self.ais[1][1]:
				file.write('#        -- BroodWar Only --\n')
				for name,string in self.ais[1][1].iteritems():
					file.write('#    %s    |    %s\n' % (name, string))
		file.write('#----------------------------------------------------\n\n')

	def decompile(self, file, ref=False):
		if isstr(file):
			try:
				f = open(file, 'w')
			except:
				raise PyMSError('Decompile',"Could not load file '%s'" % file)
		else:
			f = file
		if ref:
			self.reference(f)
		for n,string in self.strings.iteritems():
			f.write('String %s:\n%s\n\n' % (n, TBL.decompile_string(string, '\x0A')))
		for n,property in self.properties.iteritems():
			f.write('Property %s:\n\tValidProperties(' % n)
			comma = False
			for n in range(16):
				if property[0] & (2 ** n):
					if comma:
						f.write(', ')
					else:
						comma = True
					f.write(unit_properties[n])
			f.write(')\n\tValidUnitData(')
			unitdata = ')\n'
			comma = False
			for n in range(7):
				if property[1] & (2 ** n):
					if comma:
						f.write(', ')
					else:
						comma = True
					f.write(unit_data[n])
					value = ''
					if n < 6:
						value = str(property[n + 2])
					if n in [1,2,3]:
						value += '%'
					unitdata += '\t%s(%s)\n' % (unit_data[n], value)
			f.write(unitdata + '\tProperties(')
			comma = False
			for n in range(16):
				if property[8] & (2 ** n):
					if comma:
						f.write(', ')
					else:
						comma = True
					f.write(unit_properties[n])
			f.write(')\n\n')
		for trigger in self.triggers:
			f.write('Trigger(')
			comma = False
			for n,player in enumerate(trigger[0]):
				if player:
					if comma:
						f.write(', ')
					else:
						comma = True
					f.write(player_ids[n])
			f.write('):\n\tConditions:\n')
			for condition in trigger[1]:
				enabled = ''
				if condition[7] & 2:
					enabled = '-'
				if condition[5] == 58 and condition[2] != 0:
					cmd,params = self.new_conditions[condition[2]],self.new_condition_parameters[condition[2]]
				elif condition[5] == 59 and condition[2] != 0:
					cmd,params = self.dynamic_conditions[condition[2]]
				else:
					cmd,params = self.conditions[condition[5]],self.condition_parameters[condition[5]]
				f.write('\t\t%s%s(' % (enabled, cmd))
				if params:
					comma = False
					for parameter in params:
						if comma:
							f.write(', ')
						else:
							comma = True
						f.write(str(parameter(self, True, condition)))
				f.write(')\n')
			f.write('\tActions:\n')
			for action in trigger[2]:
				enabled = ''
				if action[9] & 2:
					enabled = '-'
				if action[7] == 58 and action[2] != 0:
					cmd,params = self.new_actions[action[2]],self.new_action_parameters[action[2]]
				elif action[7] == 59 and action[2] != 0:
					cmd,params = self.dynamic_actions[action[2]]
				else:
					cmd,params = self.actions[action[7]],self.action_parameters[action[7]]
				f.write('\t\t%s%s(' % (enabled, cmd))
				if params:
					comma = False
					for parameter in params:
						if comma:
							f.write(', ')
						else:
							comma = True
						f.write(str(parameter(self, True, action, self.strings, self.properties)))
				f.write(')\n')
			f.write('\n')
		f.close()

	def compile(self, file, TRIG=False):
		try:
			f = open(file, 'wb')
		except:
			raise
		if not TRIG:
			f.write('qw\x986\x18\x00\x00\x00')
		props = []
		for trigger in self.triggers:
			writenext = []
			for condition in trigger[1]:
				f.write(struct.pack('<3LH4Bxx', *condition))
			f.write('\x00' * 20 * (16 - len(trigger[1])))
			for action in trigger[2]:
				if not action[7] in [58,59]:
					if not TRIG:
						if action[1]:
							writenext.append([True,action[1]])
						if action[7] == 11 and action[5] not in props:
							props.append(action[5])
							action[9] ^= 8
							writenext.append([False,action[5]])
					elif (action[1] or action[7] == 11) and not action[9] & 2:
						action[9] ^= 2
				f.write(struct.pack('<6LH3B3x', *action))
			f.write('\x00' * 32 * (64 - len(trigger[2])))
			f.write(struct.pack('4x28B', *trigger[0]))
			for type,id in writenext:
				if type:
					f.write(self.strings[id] + '\x00' * (2048 - len(self.strings[id])))
				else:
					f.write(struct.pack('<HH4BLHH4x', *self.properties[id]))
		f.close()

for params in TRG.condition_parameters + TRG.action_parameters + TRG.new_action_parameters:
	if params:
		for p in params:
			if p.__doc__:
				d = p.__doc__.split('-',1)
				if not d[0].rstrip() in TYPE_HELP:
					TYPE_HELP[d[0].rstrip()] = d[1].lstrip()
#t = TRG()
#t.load_file('AG.trg')
#print t.triggers
#print t.strings
#print t.properties
#t.decompile('AG.txt')
#print condition_tunit(True, [0,0,0,37])
#print '-----'
#t.interpret('test.txt')
#t.compile('test.trg')
#t.load_file('test.trg')
#print t.triggers
#print t.strings
#print t.properties