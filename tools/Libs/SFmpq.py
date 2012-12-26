from ctypes import *
import os,sys

cwd = os.getcwd()
if hasattr(sys, 'frozen'):
	SFmpq_DIR = os.path.join(os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding())),'Libs')
else:
	SFmpq_DIR = os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))
if SFmpq_DIR:
	os.chdir(SFmpq_DIR)
try:
	_SFmpq = windll.SFmpq
	FOLDER = False
except:
	FOLDER = True
    
os.chdir(cwd)

class SFile:
	def __init__(self, text='', file='<Internal SFile>'):
		self.text = text
		self.file = file

	def write(self, text):
		self.text += text

	def read(self):
		return self.text

	def close(self):
		pass

	def __str__(self):
		return self.file

MPQ_ERROR_MPQ_INVALID =      0x85200065
MPQ_ERROR_FILE_NOT_FOUND =   0x85200066
MPQ_ERROR_DISK_FULL =        0x85200068 #Physical write file to MPQ failed
MPQ_ERROR_HASH_TABLE_FULL =  0x85200069
MPQ_ERROR_ALREADY_EXISTS =   0x8520006A
MPQ_ERROR_BAD_OPEN_MODE =    0x8520006C #When MOAU_READ_ONLY is used without MOAU_OPEN_EXISTING

MPQ_ERROR_COMPACT_ERROR =    0x85300001

# MpqOpenArchiveForUpdate flags
MOAU_CREATE_NEW =          0x00 #If archive does not exist, it will be created. If it exists, the function will fail
MOAU_CREATE_ALWAYS =       0x08 #Will always create a new archive
MOAU_OPEN_EXISTING =       0x04 #If archive exists, it will be opened. If it does not exist, the function will fail
MOAU_OPEN_ALWAYS =         0x20 #If archive exists, it will be opened. If it does not exist, it will be created
MOAU_READ_ONLY =           0x10 #Must be used with MOAU_OPEN_EXISTING. Archive will be opened without write access
MOAU_MAINTAIN_ATTRIBUTES = 0x02 #Will be used in a future version to create the (attributes) file
MOAU_MAINTAIN_LISTFILE =   0x01 #Creates and maintains a list of files in archive when they are added, replaced, or deleted

# MpqOpenArchiveForUpdateEx constants
DEFAULT_BLOCK_SIZE = 3 # 512 << number = block size
USE_DEFAULT_BLOCK_SIZE = 0xFFFFFFFF # Use default block size that is defined internally

# MpqAddFileToArchive flags
MAFA_EXISTS =           0x80000000 #This flag will be added if not present
MAFA_UNKNOWN40000000 =  0x40000000 #Unknown flag
MAFA_MODCRYPTKEY =      0x00020000 #Used with MAFA_ENCRYPT. Uses an encryption key based on file position and size
MAFA_ENCRYPT =          0x00010000 #Encrypts the file. The file is still accessible when using this, so the use of this has depreciated
MAFA_COMPRESS =         0x00000200 #File is to be compressed when added. This is used for most of the compression methods
MAFA_COMPRESS2 =        0x00000100 #File is compressed with standard compression only (was used in Diablo 1)
MAFA_REPLACE_EXISTING = 0x00000001 #If file already exists, it will be replaced

# MpqAddFileToArchiveEx compression flags
MAFA_COMPRESS_STANDARD = 0x08 #Standard PKWare DCL compression
MAFA_COMPRESS_DEFLATE =  0x02 #ZLib's deflate compression
MAFA_COMPRESS_WAVE =     0x81 #Standard wave compression
MAFA_COMPRESS_WAVE2 =    0x41 #Unused wave compression

# Flags for individual compression types used for wave compression
MAFA_COMPRESS_WAVECOMP1 = 0x80 #Main compressor for standard wave compression
MAFA_COMPRESS_WAVECOMP2 = 0x40 #Main compressor for unused wave compression
MAFA_COMPRESS_WAVECOMP3 = 0x01 #Secondary compressor for wave compression

# ZLib deflate compression level constants (used with MpqAddFileToArchiveEx and MpqAddFileFromBufferEx)
Z_NO_COMPRESSION =         0
Z_BEST_SPEED =             1
Z_BEST_COMPRESSION =       9
Z_DEFAULT_COMPRESSION =    -1 #Default level is 6 with current ZLib version

# MpqAddWaveToArchive quality flags
MAWA_QUALITY_HIGH =    1 #Higher compression, lower quality
MAWA_QUALITY_MEDIUM =  0 #Medium compression, medium quality
MAWA_QUALITY_LOW =     2 #Lower compression, higher quality

# SFileGetFileInfo flags
SFILE_INFO_BLOCK_SIZE =      0x01 #Block size in MPQ
SFILE_INFO_HASH_TABLE_SIZE = 0x02 #Hash table size in MPQ
SFILE_INFO_NUM_FILES =       0x03 #Number of files in MPQ
SFILE_INFO_TYPE =            0x04 #Is MPQHANDLE a file or an MPQ?
SFILE_INFO_SIZE =            0x05 #Size of MPQ or uncompressed file
SFILE_INFO_COMPRESSED_SIZE = 0x06 #Size of compressed file
SFILE_INFO_FLAGS =           0x07 #File flags (compressed, etc.), file attributes if a file not in an archive
SFILE_INFO_PARENT =          0x08 #Handle of MPQ that file is in
SFILE_INFO_POSITION =        0x09 #Position of file pointer in files
SFILE_INFO_LOCALEID =        0x0A #Locale ID of file in MPQ
SFILE_INFO_PRIORITY =        0x0B #Priority of open MPQ
SFILE_INFO_HASH_INDEX =      0x0C #Hash table index of file in MPQ
SFILE_INFO_BLOCK_INDEX =     0x0D #Block table index of file in MPQ

# Return values of SFileGetFileInfo when SFILE_INFO_TYPE flag is used
SFILE_TYPE_MPQ =  0x01
SFILE_TYPE_FILE = 0x02

# SFileListFiles flags
SFILE_LIST_MEMORY_LIST =  0x01 # Specifies that lpFilelists is a file list from memory, rather than being a list of file lists
SFILE_LIST_ONLY_KNOWN =   0x02 # Only list files that the function finds a name for
SFILE_LIST_ONLY_UNKNOWN = 0x04 # Only list files that the function does not find a name for

# SFileOpenArchive flags
SFILE_OPEN_HARD_DISK_FILE = 0x0000 #Open archive without regard to the drive type it resides on
SFILE_OPEN_CD_ROM_FILE =    0x0001 #Open the archive only if it is on a CD-ROM
SFILE_OPEN_ALLOW_WRITE =    0x8000 #Open file with write access

# SFileOpenFileEx search scopes
SFILE_SEARCH_CURRENT_ONLY = 0x00 #Used with SFileOpenFileEx; only the archive with the handle specified will be searched for the file
SFILE_SEARCH_ALL_OPEN =     0x01 #SFileOpenFileEx will look through all open archives for the file. This flag also allows files outside the archive to be used

class SFMPQVERSION(Structure):
	_fields_ = [
		('Major',c_int),
		('Minor',c_int),
		('Revision',c_int),
		('Subrevision',c_int)
	]

class FILELISTENTRY(Structure):
	_fields_ = [
		('fileExists',c_int),
		('locale',c_int),
		('compressedSize',c_int),
		('fullSize',c_int),
		('flags',c_int),
		('fileName',c_char * 260)
	]

	def __getitem__(self, k):
		if self.fullSize:
			p = self.compressedSize / float(self.fullSize)
		else:
			p = 0
		return [self.fileExists,self.locale,self.compressedSize,p,self.fullSize,self.flags,self.fileName][k]

	def __str__(self):
		if self.fullSize:
			p = self.compressedSize / float(self.fullSize)
		else:
			p = 0
		return str([self.fileExists,self.locale,self.compressedSize,p,self.fullSize,self.flags,self.fileName])

class MPQHEADER(Structure):
	_fields_ = [
		('mpqId',c_int),
		('headerSize',c_int),
		('mpqSize',c_int),
		('unused',c_short),
		('blockSize',c_short),
		('hashTableOffset',c_int),
		('blockTableOffset',c_int),
		('hashTableSize',c_int),
		('blockTableSize',c_int),
	]

class BLOCKTABLEENTRY(Structure):
	_fields_ = [
		('fileOffset',c_int),
		('compressedSize',c_int),
		('fullSize',c_int),
		('flags',c_int),
	]

class HASHTABLEENTRY(Structure):
	_fields_ = [
		('nameHashA',c_int),
		('nameHashB',c_int),
		('locale',c_int),
		('blockTableIndex',c_int),
	]

class MPQFILE(Structure):
	pass

class MPQARCHIVE(Structure):
	pass

MPQFILE._fields_ = [
	('nextFile',POINTER(MPQFILE)),
	('prevFile',POINTER(MPQFILE)),
	('fileName',c_char * 260),
	('file',c_int),
	('parentArc',POINTER(MPQARCHIVE)),
	('blockEntry',POINTER(BLOCKTABLEENTRY)),
	('cryptKey',c_int),
	('filePointer',c_int),
	('unknown',c_int),
	('blockCount',c_int),
	('blockOffsets',POINTER(c_int)),
	('readStarted',c_int),
	('streaming',c_byte),
	('lastReadBlock',POINTER(c_byte)),
	('bytesRead',c_int),
	('bufferSize',c_int),
	('refCount',c_int),
	('hashEntry',POINTER(HASHTABLEENTRY)),
	('fileName',c_char_p),
]
MPQARCHIVE._fields_ = [
	('nextArc',POINTER(MPQARCHIVE)),
	('prevArc',POINTER(MPQARCHIVE)),
	('fileName',c_char * 260),
	('hFile',c_int),
	('flags',c_int),
	('priority',c_int),
	('lastReadFile',POINTER(MPQFILE)),
	('bufferSize',c_int),
	('mpqStart',c_int),
	('mpqEnd',c_int),
	('mpqHeader',POINTER(MPQHEADER)),
	('blockTable',POINTER(BLOCKTABLEENTRY)),
	('hashTable',POINTER(HASHTABLEENTRY)),
	('readOffset',c_int),
	('refCount',c_int),
	('sfMpqHeader',MPQHEADER),
	('sfFlags',c_int),
	('sfFileName',c_char_p),
	('sfExtraFlags',c_int),
]

def MpqInitialize():
	if not FOLDER:
		_SFmpq.MpqGetVersionString.restype = c_char_p
		_SFmpq.MpqGetVersion.restype = c_float
		_SFmpq.SFMpqGetVersionString.restype = c_char_p
		_SFmpq.SFMpqGetVersionString2.argtypes = [c_char_p,c_int]
		_SFmpq.SFMpqGetVersion.restype = SFMPQVERSION
		
		_SFmpq.SFileOpenArchive.argtypes = [c_char_p,c_int,c_int,c_void_p]
		_SFmpq.SFileCloseArchive.argtypes = [c_int]
		#_SFmpq.SFileOpenFileAsArchive.argtypes = [c_int,c_char_p,c_int,c_int,c_void_p]
		_SFmpq.SFileGetArchiveName.argtypes = [c_int,c_char_p,c_int]
		_SFmpq.SFileOpenFile.argtypes = [c_char_p,c_void_p]
		_SFmpq.SFileOpenFileEx.argtypes = [c_int,c_char_p,c_int,c_void_p]
		_SFmpq.SFileCloseFile.argtypes = [c_int]
		_SFmpq.SFileGetFileSize.argtypes = [c_int,c_void_p]
		_SFmpq.SFileGetFileArchive.argtypes = [c_int,c_void_p]
		_SFmpq.SFileGetFileName.argtypes = [c_int,c_char_p,c_int]
		_SFmpq.SFileSetFilePointer.argtypes = [c_int,c_int,c_void_p,c_int]
		_SFmpq.SFileReadFile.argtypes = [c_int,c_void_p,c_int,c_void_p,c_void_p]
		_SFmpq.SFileSetLocale.argtypes = [c_int]

		_SFmpq.SFileGetFileInfo.argtypes = [c_int,c_int]
		_SFmpq.SFileListFiles.argtypes = [c_int,c_char_p,c_void_p,c_int]
		# _SFmpq..argtypes = []
		# _SFmpq..argtypes = []
		# _SFmpq..argtypes = []
		# _SFmpq..argtypes = []
		# _SFmpq..argtypes = []
		# _SFmpq..argtypes = []
		_SFmpq.SFileSetArchivePriority.argtypes = [c_int,c_int]
		_SFmpq.MpqOpenArchiveForUpdate.argtypes = [c_char_p,c_int,c_int]
		_SFmpq.MpqCloseUpdatedArchive.argtypes = [c_int,c_int]
		_SFmpq.MpqAddFileToArchive.argtypes = [c_int,c_char_p,c_char_p,c_int]
		_SFmpq.MpqAddWaveToArchive.argtypes = [c_int,c_char_p,c_char_p,c_int,c_int]
		_SFmpq.MpqRenameFile.argtypes = [c_int,c_char_p,c_char_p]
		_SFmpq.MpqDeleteFile.argtypes = [c_int,c_char_p,c_char_p]
		_SFmpq.MpqCompactArchive.argtypes = [c_int]

		_SFmpq.MpqOpenArchiveForUpdateEx.argtypes = [c_char_p,c_int,c_int,c_int]
		_SFmpq.MpqAddFileToArchiveEx.argtypes = [c_int,c_char_p,c_char_p,c_int,c_int,c_int]
		_SFmpq.MpqAddFileFromBuffer.argtypes = [c_int,c_void_p,c_int,c_char_p,c_int]
		_SFmpq.MpqRenameAndSetFileLocale.argtypes = [c_int,c_char_p,c_char_p,c_int,c_int]
		_SFmpq.MpqDeleteFileWithLocale.argtypes = [c_int,c_char_p,c_int]
		_SFmpq.MpqSetFileLocale.argtypes = [c_int,c_char_p,c_int,c_int]

def SFInvalidHandle(h):
	return h in [None,0,-1]

def MpqGetVersionString():
	return _SFmpq.MpqGetVersionString()

def MpqGetVersion():
	return _SFmpq.MpqGetVersion()

def SFMpqGetVersionString():
	return _SFmpq.SFMpqGetVersionString()

def SFMpqGetVersion():
	return _SFmpq.SFMpqGetVersion()

def SFileOpenArchive(path, priority=0, flags=SFILE_OPEN_HARD_DISK_FILE):
	h = c_int()
	if _SFmpq.SFileOpenArchive(path, priority, flags, byref(h)):
		return h.value

def SFileCloseArchive(mpq):
	return _SFmpq.SFileCloseArchive(mpq)

def SFileOpenFileEx(mpq, path, search=SFILE_SEARCH_CURRENT_ONLY):
	f = c_int()
	if _SFmpq.SFileOpenFileEx(mpq, path, search, byref(f)):
		return f.value

def SFileCloseFile(file):
	return _SFmpq.SFileCloseFile(file)

def SFileGetFileSize(file, high=False):
	s = c_int()
	l = _SFmpq.SFileGetFileSize(file, byref(s))
	if high:
		return (l,s.value)
	return l

def SFileReadFile(file, read=None):
	all = read == None
	if all:
		read = SFileGetFileSize(file)
		if read == -1:
			return
	d = create_string_buffer(read)
	r = c_int()
	o = c_int()
	if _SFmpq.SFileReadFile(file, d, read, byref(r), byref(o)):
		if all and r.value < read:
			t = r.value
			f = d.raw
			d = create_string_buffer(read-t)
			while t < read:
				if _SFmpq.SFileReadFile(file, d, read-t, byref(r), byref(o)):
					t += r.value
					f += d.raw
				else:
					break
			return (f,t)
		else:
			return (d.raw,r.value)

def SFileSetLocale(locale):
	return _SFmpq.SFileSetLocale(locale)

def SFileGetFileInfo(mpq, flags=SFILE_INFO_BLOCK_SIZE):
	return _SFmpq.SFileGetFileInfo(mpq, flags)

# listfiles is either a list of file lists or a file list itself depending on flags, either are seperated by newlines (\n \r or \r\n?)
def SFileListFiles(mpq, listfiles='', flags=0):
	n = SFileGetFileInfo(mpq, SFILE_INFO_HASH_TABLE_SIZE)
	if n < 1:
		return []
	f = (FILELISTENTRY * n)()
	_SFmpq.SFileListFiles(mpq, listfiles, f, flags)
	return filter(lambda e: e.fileExists,f)

def SFileSetArchivePriority(mpq, priority):
	return _SFmpq.SFileSetArchivePriority(mpq, priority)

def MpqOpenArchiveForUpdate(path, flags=MOAU_OPEN_ALWAYS, maxfiles=1024):
	return _SFmpq.MpqOpenArchiveForUpdate(path, flags, maxfiles)

def MpqCloseUpdatedArchive(handle, unknown=0):
	return _SFmpq.MpqCloseUpdatedArchive(handle, unknown)

def MpqAddFileToArchive(mpq, source, dest, flags=MAFA_REPLACE_EXISTING):
	return _SFmpq.MpqAddFileToArchive(mpq, source, dest, flags)

def MpqAddFileFromBuffer(mpq, buffer, file, flags=MAFA_REPLACE_EXISTING):
	return _SFmpq.MpqAddFileFromBuffer(mpq, buffer, len(buffer), file, flags)

def MpqCompactArchive(mpq):
	return _SFmpq.MpqCompactArchive(mpq)

def MpqOpenArchiveForUpdateEx(mpq, flags=MOAU_OPEN_ALWAYS, maxfiles=1024, blocksize=3):
	return _SFmpq.MpqOpenArchiveForUpdateEx(mpq, flags, maxfiles, blocksize)

def MpqAddFileToArchiveEx(mpq, source, dest, flags=MAFA_REPLACE_EXISTING, comptype=0, complevel=0):
	return _SFmpq.MpqAddFileToArchiveEx(mpq, source, dest, flags, comptype, complevel)

def MpqRenameAndSetFileLocale(mpq, oldname, newname, oldlocale, newlocale):
	return _SFmpq.MpqRenameAndSetFileLocale(mpq, oldname, newname, oldlocale, newlocale)

def MpqDeleteFileWithLocale(mpq, file, locale):
	return _SFmpq.MpqDeleteFileWithLocale(mpq, file, locale)

def MpqSetFileLocale(mpq, file, oldlocale, newlocale):
	print repr(mpq),repr(file),repr(oldlocale),repr(newlocale)
	return _SFmpq.MpqSetFileLocale(mpq, file, oldlocale, newlocale)