#!/usr/bin/python
import os
import platform
import re
import shutil
import fileinput
from os import listdir
from os.path import isfile, join
import sys, traceback

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
	cake1PluginName = ''
	cake2PluginName = ''
	appFolder       = ''

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

	cake1AppFiles = {
		'm'   : 'app_model.php',
		'v'   : 'app_helper.php',
		'c'   : 'app_controller.php',
	}

	plugins = [
		'alertify',
		'migrations',
		'mocks',
		'toolbelt',
		'zendesk',
	]

	def __init__(self):
		self.__start()
		print("Welcome to file renaming tool")

		self.cake1Root = input("Root path to CakePHP 1.x project: ")
		self.cake2Root = input("Root path to CakePHP 2.x project: ")
		self.appFolder = "app" + self.slash

	def all(self):
		print("Converting all")
		self.__delegateConversion()
		print("Converting plugins")
		self.__delegatepluginsConversion()
		print('Completed renaming %d files and %d folders' % (self.fileCount, self.folderCount))

	def __start(self):
		if platform.system() != 'Linux':
			self.slash = '\\'
			return os.system('cls')

		return os.system('clear')

	def __resolvePath(self, conversionType):
		self.cake1Path       = self.cake1Root + self.cake1Folders[conversionType] + self.slash
		self.cake2Path       = self.cake2Root + self.appFolder + self.cake2Folders[conversionType] + self.slash
		if os.path.exists(self.cake1Path):
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

	def __delegatepluginsConversion(self):
		for plugin in self.plugins:
			self.cake1PluginName = plugin
			self.cake2PluginName = self.__camelizeFolder(plugin)

			# Change root paths to plugin paths
			self.cake1Root = self.cake1Root + 'plugins' + self.slash + self.cake1PluginName + self.slash
			self.cake2Root = self.cake2Root + self.appFolder + 'Plugin' + self.slash + self.cake2PluginName + self.slash

			self.appFolder = '' # app Folder is already added into root path for plugins
			self.__delegateConversion()

			# Move remaining files and folders of plugin
			if os.path.exists(self.cake1Root):
				subFolders = [f for f in listdir(self.cake1Root) if not isfile(join(self.cake1Root, f))]
				subFiles   = [f for f in listdir(self.cake1Root) if isfile(join(self.cake1Root, f))]

				for folder in subFolders:
					if folder in ['models', 'views', 'controllers', 'libs', 'tests']:
						continue
					self.folderCount += 1
					self.__move(folder, folder, True)

				for file in subFiles:
					copyFile = True
					for appIndex in self.cake1AppFiles:
						pluginAppFile = self.cake1PluginName + '_' + self.cake1AppFiles[appIndex]
						if file == pluginAppFile:
							copyFile = False
							break

					if copyFile == True:
						self.fileCount += 1
						self.__copyFiles({file}, self.cake1Root, self.cake2Root, False, '')

			# Reverting Root path
			cake1PluginSuffixLength = len('plugins' + self.slash + self.cake1PluginName + self.slash)
			self.cake1Root          = self.cake1Root[0:-cake1PluginSuffixLength]
			cake2PluginSuffixLength = len(self.appFolder + 'Plugin' + self.slash + self.cake2PluginName + self.slash)
			self.cake2Root          = self.cake2Root[0:-cake2PluginSuffixLength]

	def namespacer(self, filename):
		prefix = self.cake2Root + self.appFolder

		if self.cake2PluginName == '':
			prefixLen = len(prefix)
		else:
			prefixLen = len(prefix) - len(self.cake2PluginName + self.slash)

		suffixLen = len(os.path.basename(filename))
		namespace = filename[prefixLen:-suffixLen-1].replace(self.slash, '\\')
		self.__prepender("namespace Saleswarp\\" + namespace + ";\n\n")(filename)

	def searchAndReplace(self, folder, filename, search, replace):
		if folder in filename:
			with fileinput.FileInput(filename, inplace=True) as file:
				for line in file:
					print(line.replace(search, replace), end = '')

	def __convertControllers(self):
		def controllerNamespacerAndComponentFixer(filename):
			componentFolder = self.cake2Root + self.appFolder + "Controller" + self.slash + "Component" + self.slash
			if componentFolder in filename:
				self.__prepender("\App::uses('Component', 'Controller');\n\n")(filename)
				with fileinput.FileInput(filename, inplace=True) as file:
					for line in file:
						print(line.replace('extends Object', 'extends \Component'), end = '')

			self.namespacer(filename)

		self.__run('c', controllerNamespacerAndComponentFixer)

	def __convertModels(self):
		def namespaceAssociations(filename):
			with fileinput.FileInput(filename, inplace=True) as file:
				for line in file:
					print(re.sub(r"('className' *\=\> *)'([A-Za-z]+)',", r"\1\2::class,", line), end = '')

		def fixModels(filename):
			self.namespacer(filename)
			behaviorFolder = self.cake2Root + self.appFolder + "Model" + self.slash + "Behavior" + self.slash
			self.searchAndReplace(behaviorFolder, filename, 'extends ModelBehavior', 'extends \ModelBehavior')
			namespaceAssociations(filename)

		self.__run('m', fixModels)

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

		cake1Path = self.cake1Root + cake1Folder + self.slash
		cake2Path = self.cake2Root + self.appFolder + cake2Folder + self.slash

		if os.path.exists(cake1Path):
			self.folderCount += 1
			print ('Moving "%s" folder' % cake1Folder)

			if ensureRemoval == True:
				try:
					shutil.rmtree(cake2Path)
				except:
					pass

			shutil.copytree(cake1Path, cake2Path)

	def __run(self, conversionType, func = None):
		if not os.path.exists(self.cake1Path):
			return
		print ('Converting files inside "%s" folder' % (self.cake1Folders[conversionType]))
		self.__copyFiles(self.files, self.cake1Path, self.cake2Path, True, '', func)

		# Move app classes
		appFileName = self.cake1AppFiles[conversionType]
		if self.cake1PluginName is not '':
			appFileName = self.cake1PluginName + '_' + appFileName

		if os.path.exists(self.cake1Root + appFileName):
			self.__copyFiles({appFileName}, self.cake1Root, self.cake2Path, True, '')
			self.namespacer(self.cake2Path + self.__camelizeFile(appFileName))

		for folderName in self.cake1Subfolders:
			cake1FolderPath  = self.cake1Path + folderName + self.slash
			properFolderName = self.__singularize(self.__camelizeFolder(folderName))
			cake2FolderPath  = self.__ensureDir(self.cake2Path + properFolderName + self.slash)
			folderFiles      = [f for f in listdir(cake1FolderPath) if isfile(join(cake1FolderPath, f))]
			self.folderCount += 1
			print ('Converting files inside "%s" folder' % (folderName))
			self.__copyFiles(folderFiles, cake1FolderPath, cake2FolderPath, True, properFolderName, func)

	def __copyFiles(self, files, cake1Folder, cake2Folder, camelize, appendage, function = None):
		if not os.path.exists(cake2Folder):
			os.makedirs(cake2Folder)

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
		if not os.path.exists(self.cake1Path):
			return
		print ('Converting files inside "%s" folder' % (self.cake1Folders['v']))

		print ('Converting files inside "helpers" of "%s" folder' % (self.cake1Folders['v']))
		cake1FolderPath = self.cake1Path + 'helpers' + self.slash
		if os.path.exists(cake1FolderPath):
			cake2FolderPath = self.__ensureDir(self.cake2Path + 'Helper' + self.slash)
			helperFiles     = [f for f in listdir(cake1FolderPath) if isfile(join(cake1FolderPath, f))]
			self.__copyFiles(helperFiles, cake1FolderPath, cake2FolderPath, True, 'helpers')

			for helperFile in helperFiles:
				self.namespacer(cake2FolderPath + self.__camelizeFile(helperFile, 'helpers'))

		# Move app_helper
		appFileName = self.cake1AppFiles['v']
		if self.cake1PluginName != '':
			appFileName = self.cake1PluginName + '_' + self.cake1AppFiles['v']

		if os.path.exists(self.cake1Root + appFileName):
			self.__copyFiles({appFileName}, self.cake1Root, cake2FolderPath, True, '')
			self.namespacer(cake2FolderPath + self.__camelizeFile(appFileName))

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
			textFile += ' ' + self.__singularize(folderName.title()) # No way to handle undefined index :(
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
	exc_type, exc_value, exc_traceback = sys.exc_info()
	traceback.print_tb(exc_traceback, limit=10, file=sys.stdout)
