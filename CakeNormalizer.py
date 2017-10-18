#!/usr/bin/python
import os
import platform
import shutil
from os import listdir
from os.path import isfile, join

class NormalizeProject:
	cake1Path       = ''
	cake1Root       = ''
	cake1Subfolders = ''
	cake2Path       = ''
	cake2Root       = ''
	files           = ''
	folderCount     = 0
	fileCount       = 0
	slash           = '/'

	cake1Folders = {
		'm'   : 'models',
		'v'   : 'views',
		'c'   : 'controllers',
	}

	cake2Folders = {
		'm'   : 'Model',
		'v'   : 'View',
		'c'   : 'Controller',
	}

	def __init__(self):
		self.__start()
		print("Welcome to file renaming tool")

		self.cake1Root = input("Root path to CakePHP 1.x project: ")
		self.cake2Root = input("Root path to CakePHP 2.x project: ")

	def all(self):
		print("Converting all")
		self.__delegateConversion()
		print('Completed renaming %d files and %d folders' % (self.fileCount, self.folderCount))

	def __start(self):
		if platform.system() != 'Linux':
			self.slash = '\\'
			return os.system('cls')

		return os.system('clear')

	def __resolvePath(self, conversionType):
		self.cake1Path       = self.cake1Root + self.cake1Folders[conversionType] + self.slash
		self.cake2Path       = self.cake2Root + "app" + self.slash + self.cake2Folders[conversionType] + self.slash
		self.cake1Subfolders = [f for f in listdir(self.cake1Path) if not isfile(join(self.cake1Path, f))]
		self.files           = [f for f in listdir(self.cake1Path) if isfile(join(self.cake1Path, f))]

		return self

	def __delegateConversion(self):
		# Controller
		self.__resolvePath('c').__convertControllers()

		# Lib
		self.__move('libs', 'Lib', True)

		# Model
		self.__resolvePath('m').__convertModels()

		# Test
		self.__move('tests', 'Test', True)

		# View
		self.__resolvePath('v').__convertViews()

	def __convertControllers(self):
		self.__run('c')

	def __convertModels(self):
		self.__run('m', self.__prepender("namespace Saleswarp\Model;\n\n"))

	def __prepender(self, prependage):
		def prepend(file):
			f = open(file, "r")
			contents = f.readlines()
			f.close()

			contents.insert(1, prependage)

			f = open(file, "w")
			contents = "".join(contents)
			f.write(contents)
			f.close()

		return prepend

	def __move(self, cake1Folder, cake2Folder, ensureRemoval):
		self.folderCount += 1
		print ('Moving "%s" folder' % cake1Folder)

		cake1Path = self.cake1Root + cake1Folder + self.slash
		cake2Path = self.cake2Root + "app" + self.slash + cake2Folder + self.slash
		if ensureRemoval == True:
			try:
				shutil.rmtree(cake2Path)
			except:
				pass

		shutil.copytree(cake1Path, cake2Path)

	def __run(self, conversionType, func = None):
		print ('Converting files inside "%s" folder' % (self.cake1Folders[conversionType]))
		self.__copyFiles(self.files, self.cake1Path, self.cake2Path, True, '', func)

		for folderName in self.cake1Subfolders:
			cake1FolderPath  = self.cake1Path + folderName + self.slash
			properFolderName = self.__singularize(self.__camelizeFolder(folderName))
			cake2FolderPath  = self.__ensureDir(self.cake2Path + properFolderName + self.slash)
			folderFiles      = [f for f in listdir(cake1FolderPath) if isfile(join(cake1FolderPath, f))]
			self.folderCount += 1
			print ('Converting files inside "%s" folder' % (folderName))
			self.__copyFiles(folderFiles, cake1FolderPath, cake2FolderPath, True, properFolderName)

	def __copyFiles(self, files, cake1Folder, cake2Folder, camelize, appendage, function = None):
		for oldFileName in files:
			self.fileCount += 1
			if camelize:
				newFileName = self.__camelizeFile(oldFileName, appendage)
			else:
				newFileName = oldFileName
			newFile = cake2Folder + newFileName
			shutil.copy2((cake1Folder + oldFileName), newFile)
			if function is not None:
				function(newFile)

	def __convertViews(self):
		print ('Converting files inside "%s" folder' % (self.cake1Folders['v']))

		print ('Converting files inside "helpers" of "%s" folder' % (self.cake1Folders['v']))
		cake1FolderPath = self.cake1Path + 'helpers' + self.slash
		cake2FolderPath = self.__ensureDir(self.cake2Path + 'Helper' + self.slash)
		helperFiles     = [f for f in listdir(cake1FolderPath) if isfile(join(cake1FolderPath, f))]
		self.__copyFiles(helperFiles, cake1FolderPath, cake2FolderPath, True, 'helpers')

		for oldFolderName in self.cake1Subfolders:
			if oldFolderName == "helpers": # was already handled above, specially
				continue

			self.folderCount += 1
			newFolderName    = self.__camelizeFolder(oldFolderName)
			try:
				shutil.copytree((self.cake1Path + oldFolderName), (self.cake2Path + newFolderName))
			except:
				files = [f for f in listdir(self.cake1Path + oldFolderName) if isfile(join(self.cake1Path + oldFolderName, f))]
				self.__copyFiles(files, self.cake1Path + oldFolderName + self.slash, self.cake2Path + newFolderName + self.slash, False, '')

	def __camelizeFile(self, fileName, folderName = ''):
		if fileName.endswith('.php'):
			ext = '.php'
		elif fileName.endswith('.ctp'):
			ext = '.ctp'

		splitedText = fileName.replace(ext, '').split('_')
		textFile = ''
		for name in splitedText:
			textFile += name.title() # title cases the letter after any special char, like ' ', '.' and so on

		try:
			textFile += ' ' + self.__singularize(folderName) # No way to handle undefined index :(
		except:
			pass

		return textFile.replace(' ', '') + ext

	def __singularize(self, str):
		if str[-1:] == 's':
			str = str[:-1]
		return str

	def __camelizeFolder(self, folderName):
		splitedText = folderName.split('_')
		textFolder = ''
		for name in splitedText:
			textFolder += name.title() # title cases the letter after any special char, like ' ', '.' and so on

		return textFolder.replace(' ', '')

	def __ensureDir(self, dirName):
		try:
			os.mkdir(dirName)
		except:
			pass

		return dirName


try:
	NormalizeProject().all()
except (Exception, KeyboardInterrupt) as ex:
	print("\nExecution stopped due to exception. \nError: %s" % str(ex))
