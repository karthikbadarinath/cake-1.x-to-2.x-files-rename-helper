#!/usr/bin/python
import os
import platform
from os import listdir
from os.path import isfile, join

class NormalizeProject:
	projectPath    = ''
	convertionType = ''
	fullPath       = ''
	folders        = ''
	files          = ''
	folderCount    = 0
	fileCount      = 0
	slash          = '/'

	options = {
		'm'   : 'models',
		'v'   : 'views',
		'c'   : 'controllers',
		'all' : 'all',
	}

	postFix = {
		'behaviors'  : 'behavior',
		'components' : 'component',
		'helpers'    : 'helper',
	}

	def __init__(self):
		self.__start()
		print("Welcome to file renaming tool")

		cakePath         = input("Provide path to project: ")
		self.projectPath = cakePath

	def convert(self):
		convertType         = input("What do you want to rename [M, V, C, All]: ")
		self.convertionType = convertType.lower()

		return self

	def all(self):
		print("Converting %s" % self.options[self.convertionType])
		self.__delegateConvertion()
		print('Completed renaming %d files and %d folders' % (self.fileCount, self.folderCount))

	def __start(self):
		if platform.system() != 'Linux':
			self.slash = '\\'
			return os.system('cls')

		return os.system('clear')

	def __resolvePath(self):
		self.fullPath = self.projectPath + self.options[self.convertionType] + self.slash
		self.folders  = [f for f in listdir(self.fullPath) if not isfile(join(self.fullPath, f))]
		self.files    = [f for f in listdir(self.fullPath) if isfile(join(self.fullPath, f))]

		return self

	def __delegateConvertion(self):
		if self.convertionType == 'c':
			self.__resolvePath().__convertControllers()
		elif self.convertionType == 'm':
			self.__resolvePath().__convertModels()
		elif self.convertionType == 'v':
			self.__resolvePath().__convertViews()
		else:
			self.__convertAll()

	def __convertAll(self):
		self.convertionType = 'c'
		self.__resolvePath().__convertControllers()

		self.convertionType = 'm'
		self.__resolvePath().__convertModels()

		self.convertionType = 'v'
		self.__resolvePath().__convertViews()

	def __convertControllers(self):
		self.__run()

	def __convertModels(self):
		self.__run()

	def __convertViews(self):
		print ('Converting files inside "%s" folder' % (self.options[self.convertionType]))

		print ('Converting files inside "helpers" of "%s" folder' % (self.options[self.convertionType]))
		folderPath   = self.fullPath + 'helpers' + self.slash
		helperFolder = [f for f in listdir(folderPath) if isfile(join(folderPath, f))]
		for oldHelperName in helperFolder:
			self.fileCount += 1
			newHelperName  = self.__camelize(oldHelperName, 'helpers')
			os.rename((folderPath + oldHelperName), (folderPath + newHelperName))

		for oldFolderName in self.folders:
			self.folderCount += 1
			folderName       = self.__camelize(oldFolderName, oldFolderName)
			newFolderName    = folderName.replace('.php', '')
			os.rename((self.fullPath + oldFolderName), (self.fullPath + newFolderName))

	def __camelize(self, fileName, folderName = ''):
		splitedText = fileName.split('_')
		textFile = ''
		for name in splitedText:
			if name.endswith('.php'):
				name = name.replace('.php', '')
				try:
					name += ' ' +  self.postFix[folderName] # No way to handle undefined index :(
				except:
					name = name

			textFile += name.title() # title cases the letter after any special char, like ' ', '.' and so on

		return textFile.replace(' ', '') + '.php'

	def __run(self):
		print ('Converting files inside "%s" folder' % (self.options[self.convertionType]))
		for oldFileName in self.files:
			self.fileCount += 1
			newFileName = self.__camelize(oldFileName)
			os.rename((self.fullPath + oldFileName), (self.fullPath + newFileName))

		for folderName in self.folders:
			folderPath  = self.fullPath + folderName + self.slash
			folderFiles = [f for f in listdir(folderPath) if isfile(join(folderPath, f))]
			self.folderCount += 1
			print ('Converting files inside "%s" folder' % (folderName))
			for oldFileName in folderFiles:
				self.fileCount += 1
				newFileName    = self.__camelize(oldFileName, folderName)
				os.rename((folderPath + oldFileName), (folderPath + newFileName))

try:
	NormalizeProject().convert().all()
except (Exception, KeyboardInterrupt) as ex:
	print("\nExecution stopped due to exception. \nError: %s" % str(ex))
