#!/usr/bin/env python3

'''####################################
#Version: 00.01
#Version Numbering: Major.Minor
#Reasons for imports
	os				: used for verifying and reading files
	sys			: used for exiting the system
	json			: used for reading the Info.json files
	hashlib		: used for creating hashes of files
	argparse	: used for parsing arguments
	shutil		: used for helpful file/folder manipulations
	datetime	: used for creating a helpful date/time
	enum		: used for the supported enum types
'''####################################

##Imports
import os
import sys
import json
import hashlib
import argparse
import shutil
from datetime import datetime as dt
from enum import Enum

'''####################################
#
'''####################################

'''####################################
#Hardcoded variables used throughout the file
	files				: files used throughout the script
	fldrs				: folders used throughout the script
	shebang		: a flag used to enable shebang on the checksum
	routers			: a variable used to hold the main methods to be called
	spellCheck	: the option for spellchecking the latex files
'''####################################
files, fldrs, shebang, routers, spellCheck = ('body.tex','Info.json'), ('Imgs','Source'), False,{}, True


'''####################################
#The main class containing enums for auto commentors
'''####################################
class supportedTypes(Enum):
	java = 0
	groovy = 1
	scala = 2
	css = 3
	js = 4
	cpp = 5
	xml = 15
	html = 16
	php = 17
	py = 40

	@classmethod
	def supported(cls, testType):
		return testType in [e.name for e in cls]

	def __str__(self):
		return self.name

	def getCmtStart(self):
		if (self.value < 15):  		#Style: /* */
			return "/**\n=====================================\n"
		elif (self.value == 40):	#Style: #
			return "##########################################\n"
		else:								#Style: <!-- -->
			return "<!-----------------------------------------\n"

	def getCmtEnd(self):
		if (self.value < 15):  		#Style: /* */
			return "\n=====================================\n*/"
		elif (self.value == 40):	#Style: #
			return "\n##########################################"
		else:								#Style: <!-- -->
			return "\n------------------------------------------>"

	def getCmt(self):
		if (self.value < 15):  		#Style: /* */
			return "*"
		elif (self.value == 40):	#Style: #
			return "#"

'''####################################
#The program that zips and adds auto comments into the sha files
'''####################################
class programHeader(object):
	author = ""
	date = ""
	name = ""
	ext = None
	file = None
	isDir = False

	def __init__(self):
		localInfo = Utils.loadLocalInfo()
		self.file = 'Source'
		self.author = str(localInfo['fname'])+" "+str(localInfo['lname'])
		self.ignore = localInfo['ignore']
		self.date = dt.now().strftime('%Y/%m-%B/%d')
		self.name=str(localInfo['alias'])+'_'+str(localInfo['asnName'])
		self.assignmentName = localInfo['asnName']

	def pair(self, name, value, end=False):
		String = "\t\"" + str(name) + "\": "
		if (isinstance(value, str)):
			String += "\"" + str(value) + "\""
		else:
			String += str(value)
		if (not end):
			String += ",\n"
		return String

	def __str__(self):
		mayne = {
			"Author": self.author,
			"Date": self.date
		}
		return self.organize(mayne)

	def organize(self, Dict, ext=None):
		rtrn = ""
		if (ext is not None):
			rtrn += ext.getCmtStart()
		rtrn += "{\n"
		for itr, key in enumerate(Dict):
			if itr == (len(Dict) - 1):
				rtrn += self.pair(key, Dict[key], True)
			else:
				rtrn += self.pair(key, Dict[key])
		rtrn += "\n}"
		if (ext is not None):
			rtrn += ext.getCmtEnd()
		return rtrn

	def __print__(self):
		print(self.ext.getCmtStart())
		print(self.toString())
		print(self.ext.getCmtEnd())

	def out(self):
		rtrn = ""
		rtrn += self.ext.getCmtStart()
		rtrn += str(self)
		rtrn += self.ext.getCmtEnd()
		return rtrn

	def writeOut(self):

		newPath, oldPath, finPath = os.path.dirname(
			os.path.abspath(self.file)), os.path.abspath(self.file), None

		readFiles, ktr, info, ver = [], 0, {
			"Author": self.author,
			"Date": str(dt.now().strftime('%Y/%m-%B/%d'))
		}, '00'
		while (os.path.exists(
				os.path.join(newPath, "Cut_" + str(ver)))):
			if (ktr >= 15):
				print('Reached a max of 16 Cuts')
				sys.exit()
			ktr += 1
			if (ktr < 10):
				ver = '0'+str(ktr)
			else:
				ver = ktr

		newPath = os.path.join(newPath, "Cut_" + str(ver))
		finPath = newPath
		fileShas, folderSha, ogPath = "",os.path.join(newPath,"sha512sums.txt"), newPath

		try:
			shutil.copytree(oldPath, newPath)
		except:
			shutil.copy(oldPath, newPath)

		for root, directorynames, filenames in os.walk(newPath):
			for oldFileName in filenames:
				curPath, absPath, oldFile = root, str(
					os.path.join(root, oldFileName)), os.path.join(
						root, oldFileName)

				localPathName = str(oldFile).replace(ogPath,'.')

				if (localPathName not in self.ignore and len(os.path.basename(oldFile).split('.')) == 2
						and supportedTypes.supported(
							os.path.basename(oldFile).split('.')[1])):
					bareOldFileName, bareOldFileExt = os.path.basename(
						oldFile).split('.')
					with open(oldFile, 'r+') as foil:
						contents, info[
							'FileName'] = foil.read(), bareOldFileName
						foil.seek(0)
						foil.write(
							str(
								self.organize(
									info, supportedTypes[bareOldFileExt]))
							+ '\n')
						foil.write(contents)
						foil.truncate()

				fileShas+=str(Utils.ShaFile(oldFile,ogPath))+"\n"

		with open(str(folderSha),'w') as file:
			file.write(fileShas)

		zipFile = self.name
		shutil.make_archive(zipFile, "zip", newPath)
		zipFile, shaFile = zipFile + '.zip', zipFile + '_sha512'

		Utils.createSha(zipFile, shaFile)

		shutil.rmtree(newPath, ignore_errors=True)
		os.makedirs(newPath)
		shutil.move(zipFile, newPath)
		shutil.move(shaFile, newPath)

'''####################################
#A utility class that contains the rest of the main common files
'''####################################
class Utils(object):
	def createSha(inFile, shaFile):
		sha = None
		with open(inFile, 'rb') as new:
			contents = new.read()
			sha = hashlib.sha512(contents).hexdigest()
		with open(shaFile, 'w') as shaFile:
			if (shebang):
				shaFile.write("#!/bin/bash" + "\n")
				shaFile.write(
					"echo \"" + str(sha) + "  " + inFile + "\"|sha512sum -c -")
			else:
				shaFile.write(str(sha) + "  " + inFile)

	def ShaFile(inFile,absPath):
		sha = None
		with open(inFile, 'rb') as new:
			contents = new.read()
			sha = hashlib.sha512(contents).hexdigest()

		return str(sha) + "  " + str(inFile).replace(absPath,'.')

	def make(switch):
		global files
		global fldrs
		localInfo = Utils.loadLocalInfo(switch)
		path = localInfo['assignmentTemplate']
		##Check the files for spelling first
		if spellCheck:
			for fil in files:
				if (fil != 'Info.json'):
					os.system('aspell -t -c --lang=en --dont-tex-check-comments '+str(fil))

		##Copying the sources into the assignment template
		for fil in files:
			os.system('cp '+str(fil)+' '+str(path))
		for fldr in fldrs:
			os.system('cp -r '+str(fldr)+' '+str(path))

		##Calling a build for the assignment
		os.system('make -C '+str(path))

		##Else set the name
		reportName = "Report"
		if 'asnName' in localInfo and localInfo['asnName'] != " ":
			reportName = str(localInfo['alias'])+"_"+str(localInfo['asnName'])

		##Setting a extra indicator if the report is not ready yet
		if localInfo['makeType'] != "conference":
			reportName += "_"+str(localInfo['makeType'])

		finPath = os.curdir
		if (switch == 'make'):
			finPath = os.path.join(finPath,'Source')

		##Moving the Created PDF to the called dir
		pdf,reportName=os.path.join(path,'Report.pdf'), str(reportName)+'.pdf'

		os.system('mv '+str(pdf)+' '+str(os.path.join(finPath,reportName)))

		##Cleaning the assignment template
		os.system('make clean -C '+str(path))

	def cut(switch):
		header = programHeader()
		header.writeOut()

	def prettyJson(ojb):
		return json.dumps(ojb,default=lambda o: o.__dict__,sort_keys=True,indent=3)

	def gen(switch):
		genInfo = json.load(open(localInfoPath,'r'))
		##Generating the Files and Folders used for the generation
		for fldr in fldrs:
			os.system('mkdir '+str(fldr))
		for file in files:
			os.system('touch '+str(file))
		with open('Info.json','w') as file:
			file.write(Utils.prettyJson(genInfo))

	#Setting the arguments to be handled by the parser
	def arguments(parser,curChoices):
		parser.add_argument("info", type=str, nargs='?', help='The location of the original info file')
		parser.add_argument("switch", choices=curChoices, nargs='?', default='ignore', help='Use the q flag to show detailed help')
		parser.add_argument("-i", type=str, nargs='?', help="File to be ignored.")
		parser.add_argument("-q", action='store_true', help='Shows the information for the flags')
		return parser

	def ignore(ignoreFile):
		localInfo = Utils.loadLocalInfo()

		fullPath = os.path.abspath(ignoreFile).split('Source')[-1]

		localInfo['ignore'] += ['.'+str(fullPath)]

		with open('Info.json','w') as file:
			file.write(Utils.prettyJson(localInfo))
		return

	def routing(switch):
		return routers.get(switch, Utils.make)

	def routingInfo():
		for val in routers:
			print('\t'+str(val)+': '+str(routers[val]['def'])+'\n')
		return

	def cleanFolders(switch):
		def remove_empty_dirs(path):
			for root, dirnames, filenames in os.walk(path, topdown=False):
				for dirname in dirnames:
					if (dirname != '__pycache__'):
						try:
							os.rmdir(os.path.realpath(os.path.join(root, dirname)))
						except OSError:
							pass

	def makeType(x):
		return {
			'draft':'draft',
			'make':'conference',
			'note':'technote'
		}.get(x,'draft')

	def loadLocalInfo(switch="ignore"):
		curPath = os.path.join(os.curdir,'Info.json')
		if (not os.path.isfile(curPath)):
			print('Local Info File Not Found')
			print(curPath)
			sys.exit()

		localInfo = json.load(open(curPath,'r'))

		if (switch != "ignore"):
			localInfo['makeType'] = Utils.makeType(switch)

		localInfo['date'] = dt.now().strftime('%Y/%m-%B/%d')

		return localInfo

	def start():
		curChoices=list(routers.keys())
		args, ignoreFile = Utils.arguments(argparse.ArgumentParser(),curChoices).parse_args(), None
		if (args.q):
			Utils.routingInfo()
			sys.exit()

		if (args.switch == 'ignore'):
			if (args.i is None):
				print("Please A File To Be Ignored")
				sys.exit()
			else:
				Utils.ignore(args.i)
				sys.exit()
		elif (args.switch == 'gen'):
			if (args.info is None or not os.path.exists(args.info) or len(args.info.split('.')) != 2 or args.info.split('.')[-1] != 'json' ):
				print('You need a valid info file for gen.')
				sys.exit()
			else:
				global localInfoPath
				localInfoPath = args.info

		Utils.routing(args.switch)["func"](args.switch)

'''####################################
#The dictionary containing the working functions and their respective definitions
'''####################################
routers = {
	'gen': {
		"func":Utils.gen,
		"def":"Flag to generate sources, Source, Imgs, body.tex, Info.json."
	},
	'draft': {
		"func":Utils.make,
		"def":"Flag to generate the Draft."
	},
	'make':  {
		"func":Utils.make,
		"def":"Flag to generate the Report into Source."
	},
	'note':  {
		"func":Utils.make,
		"def":"Flag to generate the Technote Report."
	},
	'cut': {
		"func":Utils.cut,
		"def":"Flag to make a cut of the Source Folder."
	},
	'clean': {
		"func":Utils.cleanFolders,
		"def":"The flag to recursively delete empty folders."
	},
	'ignore': {
		"func":Utils.ignore,
		"def":"The flag to be ignored on the cut commenting."
	}
}

'''####################################
#The main runner of this file, intended to be ran from 
'''####################################
if __name__ == '__main__':
	Utils.start()
