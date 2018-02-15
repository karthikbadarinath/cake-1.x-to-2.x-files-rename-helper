#!/usr/bin/python
import os
import platform
import re
import fileinput
from os import listdir
from os.path import isfile, join

class ReplaceVariables:
	cakePath       = ''
	cakeRoot       = ''
	cakeSubfolders = ''
	files           = ''
	folderCount     = 0
	fileCount       = 0
	slash           = '/'

	cakeFolders = {
		'v'   : 'View',
		'c'   : 'Controller',
	}

	replaceStrings = {
		'$this->data'    : '$this->request->data',
		'$this->params'  : '$this->request->params',
		'$this->webroot' : '$this->request->webroot',
		'$this->action'  : '$this->request->action',
	}

	def __init__(self):
		self.__start()
		print("Welcome to request variables renaming tool")

		self.cakeRoot = input("Root path to CakePHP 2.x project: ")

	def convert(self):
		print("Converting all")
		self.__delegateConversion()
		print('Completed renaming %d files and %d folders' % (self.fileCount, self.folderCount))

	def __start(self):
		if platform.system() != 'Linux':
			self.slash = '\\'
			return os.system('cls')

		return os.system('clear')

	def __resolvePath(self, conversionType):
		self.cakePath       = self.cakeRoot + "app" + self.slash + self.cakeFolders[conversionType] + self.slash
		self.cakeSubfolders = [f for f in listdir(self.cakePath) if not isfile(join(self.cakePath, f))]
		self.files           = [f for f in listdir(self.cakePath) if isfile(join(self.cakePath, f))]

		return self

	def __delegateConversion(self):
		# Controller
		self.__resolvePath('c').__convertControllers()

		# View
		self.__resolvePath('v').__convertViews()

	def searchAndReplace(self, filename, search, replace):
		with fileinput.FileInput(filename, inplace=True) as file:
			for line in file:
				print(re.sub(r'(%s\b(?!\())' % re.escape(search), replace, line), end = '')

	def replacer(self, files, folder):
		for fileName in files:
			self.fileCount += 1
			fileWithPath = folder + fileName
			for search, replace in self.replaceStrings.items():
				self.searchAndReplace(fileWithPath, str(search), replace)

	def __convertControllers(self):
		self.replacer(self.files, self.cakePath)

		# subFolder files
		self.__convertSubFolders(self.cakeSubfolders, self.cakePath)

	def __convertViews(self):
		print ('Converting files inside "%s" folder' % (self.cakeFolders['v']))

		self.replacer(self.files, self.cakePath)
		# subFolder files
		self.__convertSubFolders(self.cakeSubfolders, self.cakePath)

	def __convertSubFolders(self, subFolders, folderPath):
		for subFolder in subFolders:
			self.folderCount += 1
			subFolderPath = folderPath + subFolder + self.slash
			subfiles = [f for f in listdir(subFolderPath) if isfile(join(subFolderPath, f))]
			print ('Converting files inside "%s" folder' % (subFolder))
			self.replacer(subfiles, (folderPath + subFolder + self.slash))

			anySubFolders = [f for f in listdir(subFolderPath) if not isfile(join(subFolderPath, f))]
			if anySubFolders:
				self.__convertSubFolders(anySubFolders, subFolderPath)

try:
	ReplaceVariables().convert()
except (Exception, KeyboardInterrupt) as ex:
	print("\nExecution stopped due to exception. \nError: %s" % str(ex))
