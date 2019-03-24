#!/usr/bin/python3

import os, sys, time, re
from argparse import ArgumentParser
from collections import Counter, defaultdict
from os.path import basename
from math import modf

# Parsing the arguments
argParser = ArgumentParser("script.py3")
argParser.add_argument("-if", "--src", dest="inFilePath",
	help="Path to input (source) file", metavar="file.txt")
argParser.add_argument("-of", "--dst", dest="outFilePath",
	help="Path to output (resulting) file", metavar="file.txt")
argParser.add_argument("-ef", "--excl", nargs="?", dest="exclFilePath",
	help="Path to file with excluded records (for \"re_import\" mode)", metavar="file.txt")
argParser.add_argument("-im", "--mrg", dest="mergeFilePath",
	help="Path to input (for merging) file", metavar="file.txt")
argParser.add_argument("-m", "--mod", dest="workMode",
	help="Work mode selector", metavar="mode_name")
argParser.add_argument("-n", "--num", type=int, nargs="?", dest="topNum",
	help="Quantity for generating top-N reports (for \"top_rep\" mode)", metavar="num_of_records")
argParser.add_argument("-g", "--gran", type=int, nargs="?", dest="granLevel",
	help="Granularity level for domains (allowed maximum number of subdomains) (for \"top_rep\" mode)", metavar="gran_level")
argParser.add_argument("-d", "--dom", nargs="?", dest="domainType",
	help="Domain type (for \"re_import\" mode (your domain))", metavar="domain_type")
argParser.add_argument("-abc", "--abc", action="store_true", dest="abcSort",
	help="Sort values alphabetically")
scriptArgs = argParser.parse_args()

# File pathes definition
inFilePath    = scriptArgs.inFilePath
mergeFilePath = scriptArgs.mergeFilePath
outFilePath   = scriptArgs.outFilePath
exclFilePath  = scriptArgs.exclFilePath

# Reserving some other global variables
inFile  = None
outFile = None	
startTime = 0
endTime   = 0
inLinesCount = 0

# Mode variables and modificators/options
abcSort    = scriptArgs.abcSort
workMode   = scriptArgs.workMode
topNum     = scriptArgs.topNum
domainType = scriptArgs.domainType
granLevel  = scriptArgs.granLevel

# Function for input string cleaning from carriage returns and whitespaces
def cleanInputString(inStr):
	if len(inStr) != 0:
		outStr = inStr.strip("\r")
		outStr = outStr.strip("\n")	
		outStr = outStr.strip()
		return outStr

# Function for counting lines in file
def countLines(filePath):
	if checkFilePath(filePath):
		try:
			fileLinesCount = 0	
			with open(filePath, "r", encoding="utf8") as file:
				for fileLine in file:
					fileLinesCount += 1
			file.close()
			return fileLinesCount
		except:
			print("Failed to open a \"%s\" file!" % filePath)
			sys.exit()

# Function for counting lines in input file
def countLinesMem(fileContent):
	if fileContent != None:
		return len(fileContent)

# Function for checking that specified file path is correct
def checkFilePath(filePath, verbose = False):
	if not filePath or len(filePath) == 0 or filePath == None:
		if verbose:		
			print("File path is incorrect!")
		return False
	else:
		return True

# Function for checking file existance
def checkFileExists(filePath, checkPath = False, verbose = False):
	filePathOK = True	
	if checkPath:
		filePathOK = checkFilePath(filePath)
	if filePathOK:
		if not os.path.isfile(inFilePath):
			if verbose:		
				print("File \"%s\" does not exist!" % filePath)
			return False
		else:
			return True
	else:
		if verbose:
			print("File path is incorrect!")
		return False

# Function for loading data from file to memory
def loadFileContentToMem(filePath, addEndLine = False, noProgress = True):
	if not checkFileExists(filePath, True):
		print("File path is incorrect or file does not exist!")
		sys.exit()
	else:
		try:
			print("\nOpening a file \"%s\" for importing..." % filePath)
			if not noProgress:			
				linesCount = countLines(filePath)
				curLineNumber = 1
			fileContent = []
			eol = ""
			if addEndLine:
				eol = "\n"
			with open(filePath, "r", encoding="utf8") as file:
				if noProgress:
					for line in file:
						fileContent.append(cleanInputString(line) + eol)
				else:
					for line in file:
						print(f"\tProgress: {curLineNumber/linesCount*100:.2f}%", end="\r")
						fileContent.append(cleanInputString(line) + eol)
						curLineNumber += 1
			print("\n", end="\r")
			return fileContent
		except:
			print("Failed to open a file for importing!")
			sys.exit()

# Function for flushing content from memory to file
def writeMemContentToFile(filePath, memContent, addEndLine = True, noProgress = True):
	if not checkFilePath(filePath):
		print("File path is incorrect!")
		sys.exit()
	elif memContent == None:
		print("Nothing to write to file!")
		sys.exit()		
	else:
		try:
			print("Writing content to file \"%s\"..." % filePath)
			eol = ""
			if addEndLine:
				eol = "\n"
			if not noProgress:
				linesCount = countLinesMem(memContent)
				curLineNumber = 1
			with open(filePath, "w+", encoding="utf8") as file:
				if noProgress:
					for line in memContent:
						file.write(line + eol)
				else:
					for line in memContent:
						print(f"\tProgress: {curLineNumber/linesCount*100:.2f}%", end="\r")
						file.write(line + eol)
						curLineNumber += 1
		except:
			print("Failed to write to output file!")
			sys.exit()
			
# Function for flushing content from memory to file
def flushMemContentToFile(filePath, memContent):
	if not checkFilePath(filePath):
		print("File path is incorrect!")
		sys.exit()
	elif memContent == None:
		print("Nothing to flush to file!")
		sys.exit()		
	else:
		try:
			print("Flushing to file \"%s\"..." % filePath)
			file = open(filePath, "w+", encoding="utf8")
			file.writelines(memContent)
			file.close()
		except:
			print("Failed to flush to output file!")
			sys.exit()

# Converting an execution time into human readable format
def convertTime(timeInSeconds):
	if not timeInSeconds == None:
		if timeInSeconds >= 0:
			frac, days = modf(timeInSeconds/86400)
			frac, hours = modf((frac*86400)/3600)
			frac, minutes = modf((frac*3600)/60)
			frac, seconds = modf((frac*60))
			return ("%d day(s) %d hour(s) %d min(s) and %d second(s)" % (days, hours, minutes, seconds))
	return ("N/A")

# Function for counting item repeats in list and returning report in list format
def countRepeats(inList, byValue = True):
	if inList != None:
		# Creating dictionary from list
		inDict = dict(Counter(inList))
		# Sorting dictionary content by meet frequency
		if byValue:
			inDictSorted = sorted(inDict.items(), key=lambda item: item[1], reverse=True)
		else:
			inDictSorted = sorted(inDict.items(), key=lambda item: item[0], reverse=True)
		del inDict
		# Generating output
		outList = []
		for key, value in inDictSorted:
			outList.append("%s <- %s time(s)" % (key, value))
		del inDictSorted
		return outList

# Merging two files in one with repeats validation
def mergeFiles(sortByAlphabet = False):
	if not checkFileExists(mergeFilePath, True):
		print("Input file path for file to merge is incorrect or file does not exist!")
		sys.exit()
	else:
		# Determinating the time of start	
		startTime = time.time()
		# Loading strings from source file into memory
		print("\nLoading strings from source file into memory...", end="\r")
		inFileContent = loadFileContentToMem(inFilePath)
		# Counting number of lines
		inLinesCount = countLinesMem(inFileContent)
		print("Source file contains %d lines." % inLinesCount)
		# Converting to dictionary
		inFileDict = dict(Counter(inFileContent))
		del inFileContent
		# Loading strings from merging file into memory
		print("\nLoading strings from merging file into memory...", end="\r")
		mergeFileContent = loadFileContentToMem(mergeFilePath)
		# Counting number of lines
		mergeLinesCount = countLinesMem(mergeFileContent)
		print("Merging file contains %d lines." % mergeLinesCount)
		## Converting to dictionary and cleaning-up merge strings
		print("\nCreating dictionaries...")
		mergeFileDict = dict(Counter(mergeFileContent))
		del mergeFileContent
		## Definition of variables
		mergeAddedLines = 0
		## Merging process
		print("Starting merging process...")
		mergeFileDictLength = len(mergeFileDict)
		mergeFileDictKeys = list(mergeFileDict)
		for key in mergeFileDict:
			print(f"\tProgress: {(mergeFileDictKeys.index(key)+1)/mergeFileDictLength*100:.2f}%", end="\r")
			if key in inFileDict:
				### Re-writing value of repeats
				if mergeFileDict[key] > inFileDict[key]:
					inFileDict[key] = mergeFileDict[key]
					mergeAddedLines += (mergeFileDict[key]-inFileDict[key])
			else:
				### Writing absent entry
				inFileDict[key] = mergeFileDict[key]
				mergeAddedLines += mergeFileDict[key]
		## Purging unused
		del mergeFileDict
		## Sorting dictionary
		print("\nGenerating list of lines...")
		if sortByAlphabet:
			inFileDictKeys = sorted(inFileDict)
		else:
			inFileDictKeys = inFileDict.keys()
		## Generating lines to write to file
		fileContent = []
		for key in inFileDictKeys:
			for i in range (0, inFileDict[key]):
				fileContent.append(key)
		## Purging unused
		del inFileDict
		del inFileDictKeys
		## Writing to file
		print("\nWriting data to result file...")
		writeMemContentToFile(outFilePath, fileContent)
		# Determinating the time of end
		endTime = time.time()
		# Statistic printing and exiting
		print("\n%d lines have been processed in %s." % ((inLinesCount+mergeLinesCount), convertTime(endTime-startTime)))
		print("%d lines are imported from source and %d lines are added from merging file." % (inLinesCount, mergeAddedLines))
		print("Result file contains %d lines." % (inLinesCount+mergeAddedLines))
### End of "mergeFiles" ###

# Processing an input file with RegEx and exporting matches to an output file
def reImport(writeExcluded = False, sortByAlphabet = False, domain = None):
	# Determinating the time of start	
	startTime = time.time()
	# Defining the RegExes
	### Info: https://regex101.com/r/U5Y0HA/46
	mainPattern = r"(^([A-Za-z0-9](?!.*([\-_\.]){2,}.*)[A-Za-z0-9\-_\.]{0,62}[A-Za-z0-9])([@]{1})(((?![^A-Za-z0-9])(?!.*(\-){2,}.*)[A-Za-z0-9\-]{0,62}[A-Za-z0-9])(([\.])((?![^A-Za-z0-9])(?!.*(\-){2,}.*)[A-Za-z0-9\-]{0,62}[A-Za-z0-9]))+)([:;\ ]{1})((?!\b(?:(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?){1})\b)(?!.{32,})(.{2,31})))"
	if domain != None:
		if len(domain) >= 2:
			domainStr = cleanInputString(domain)
			domainStr = domainStr.replace(".", "\.")
			customPattern = r"(^(.*)([@]{1})((([A-Za-z0-9_\.\-]+[\.]){0,1})(" + domainStr + "))([:]{1})(.*))"
			pattern = customPattern
		else:
			print("Wrong domain pattern is given!")
			sys.exit()			
	else:
		pattern = mainPattern
	# Loading strings from source file into memory
	print("\nLoading strings from source file into memory...", end="\r")
	inFileContent = loadFileContentToMem(inFilePath)
	# Counting number of lines
	inLinesCount = countLinesMem(inFileContent)
	print("Source file contains %d lines." % inLinesCount)
	# Definition of variables
	outFileContent = []
	if writeExcluded:
		exclFileContent = []
	curLineNumber = 0
	matchesCount = 0
	excludedCount = 0
	# Importing process
	print("Importing using regular expression...")
	for pair in inFileContent:
		curLineNumber += 1
		print(f"\tProgress: {(curLineNumber/inLinesCount)*100:.2f}%", end="\r")
		regRes = re.findall(pattern, pair)
		if len(regRes) != 0:
			## Counting included elements
			matchesCount += 1
			## Replace the delimiter to standart colon symbol (:)
			outFileContent.append(re.sub(r"[:; ]", ":", regRes[0][0], 1))
		else:
			## Counting excluded elements
			excludedCount += 1
			if writeExcluded:
				if len(pair) != 0:
					exclFileContent.append(pair)
	# Purging unused
	del inFileContent
	# Sorting by alphabet
	print("\nGenerating list of lines...")
	if sortByAlphabet:
		outFileContent = sorted(outFileContent)
		if writeExcluded:
			exclFileContent = sorted(exclFileContent)
	# Writing included data to file
	print("\nWriting included data to file...")
	writeMemContentToFile(outFilePath, outFileContent)
	# Purging unused
	del outFileContent
	# Writing excluded data to file
	if writeExcluded:
		print("\nWriting excluded data to file...")
		writeMemContentToFile(exclFilePath, exclFileContent)
	# Purging unused
	if writeExcluded:
		del exclFileContent
	# Determinating the time of end
	endTime = time.time()
	# Statistic printing and exiting
	print("\nFound %d matches in %d lines, %d lines are excluded." % (matchesCount, inLinesCount, excludedCount))
	if writeExcluded:
		print("Excluded lines are written to \"%s\" file." % exclFilePath)
	print("Processing finished in %s." % (convertTime(endTime-startTime)))
### End of "reImport" ###

# Generating Top-N reports
def genTopReport(numOfRecords = 10, granLvl = 4):
	# Determinating the time of start	
	startTime = time.time()
	# Loading strings from source file into memory
	print("\nLoading strings from source file into memory...", end="\r")
	inFileContent = loadFileContentToMem(inFilePath)
	# Counting number of lines
	inLinesCount = countLinesMem(inFileContent)
	print("Source file contains %d lines." % inLinesCount)
	# Splitting pairs on components
	print("\nSplitting pairs on components:")
	curLineNumber = 0
	mailAddressList = []
	domainsList = []
	passwordsList = []
	passwordsLenList = []
	for pair in inFileContent:
		curLineNumber += 1
		print(f"\tProgress: {(curLineNumber/inLinesCount)*100:.2f}%", end="\r")
		splittedPair = re.split(r"([:])", pair, 1)
		## Mail addresses processing
		if len(splittedPair) == 3:
			### Adding into mail addresses list
			mailAddressList.append(splittedPair[0])
		## Passwords processing
		if len(splittedPair) == 3:
			password = splittedPair[2]
			### Passwords frequency based on password length
			passwordsLenList.append(len(password))
			### Adding into passwords list
			passwordsList.append(password)
		## Domains processing
		domainSplit = re.split(r"([@])", splittedPair[0], 1)
		if len(domainSplit) == 3:
			domain = re.split(r"([@])", splittedPair[0], 1)[2]
			dotsCount = domain.count(".")
			if dotsCount > granLvl:
				deltaDots = dotsCount - granLvl
				domain = re.split(r"([.])", domain, (deltaDots))[2*deltaDots]
			domainsList.append(domain)
	# Full pair processing
	fullPairsList = countRepeats(inFileContent)
	# Purging unused
	del inFileContent
	# Getting lists with data
	mailAddressList = countRepeats(mailAddressList)
	domainsList = countRepeats(domainsList)
	passwordsList = countRepeats(passwordsList)
	passwordsLenList = countRepeats(passwordsLenList, False)
	# Generating lines to write to file
	print("\nGenerating lines to write to file:")
	outFileContent = []
	fullPairsRecCount = len(fullPairsList)
	fullPairsRecCount = numOfRecords if numOfRecords < fullPairsRecCount else fullPairsRecCount
	mailAddressRecCount = len(mailAddressList)
	mailAddressRecCount = numOfRecords if numOfRecords < mailAddressRecCount else mailAddressRecCount
	domainsRecCount = len(domainsList)
	domainsRecCount = numOfRecords if numOfRecords < domainsRecCount else domainsRecCount
	passwordsRecCount = len(passwordsList)
	passwordsRecCount = numOfRecords if numOfRecords < passwordsRecCount else passwordsRecCount
	passwordsLenListCount = len(passwordsLenList)
	curLineNumber = 0
	recordsCount = (fullPairsRecCount + mailAddressRecCount + domainsRecCount + passwordsRecCount + passwordsLenListCount)
	## Header
	outFileContent.append("Top-%d report for \"%s\" file (contains %d lines).\n" % (numOfRecords, basename(inFilePath), inLinesCount))
	## Full Pairs
	outFileContent.append("# Top-%d of full-pairs, selected %d records:" % (numOfRecords, fullPairsRecCount))
	for i in range(fullPairsRecCount):
		curLineNumber += 1
		print(f"\tProgress: {(curLineNumber/recordsCount)*100:.2f}%", end="\r")
		outFileContent.append("\t%s" % fullPairsList[i])
	### Purging unused
	del fullPairsList
	## Adding some gap
	outFileContent.append("")
	## Mail Addresses
	outFileContent.append("# Top-%d of mail addresses, selected %d records:" % (numOfRecords, mailAddressRecCount))
	for i in range(mailAddressRecCount):
		curLineNumber += 1
		print(f"\tProgress: {(curLineNumber/recordsCount)*100:.2f}%", end="\r")
		outFileContent.append("\t%s" % mailAddressList[i])
	### Purging unused
	del mailAddressList
	## Adding some gap
	outFileContent.append("")
	## Domains
	outFileContent.append("# Top-%d of domains (max subdomain level is %d), selected %d records:" % (numOfRecords, granLvl, domainsRecCount))
	for i in range(domainsRecCount):
		curLineNumber += 1
		print(f"\tProgress: {(curLineNumber/recordsCount)*100:.2f}%", end="\r")
		outFileContent.append("\t%s" % domainsList[i])
	### Purging unused
	del domainsList
	## Adding some gap
	outFileContent.append("")
	## Passwords
	outFileContent.append("# Top-%d of passwords, selected %d records:" % (numOfRecords, passwordsRecCount))
	for i in range(passwordsRecCount):
		curLineNumber += 1
		print(f"\tProgress: {(curLineNumber/recordsCount)*100:.2f}%", end="\r")
		outFileContent.append("\t%s" % passwordsList[i])
	### Purging unused
	del passwordsList
	## Adding some gap
	outFileContent.append("")
	## Passwords distribution by length
	outFileContent.append("# Passwords distribution by length (LENGTH:AMOUNT):")
	for i in range(passwordsLenListCount):
		curLineNumber += 1
		print(f"\tProgress: {(curLineNumber/recordsCount)*100:.2f}%", end="\r")
		outFileContent.append("\t%s" % passwordsLenList[i])
	### Purging unused
	del passwordsLenList
	# Writing to file
	print("\n\nWriting data to result file...")
	writeMemContentToFile(outFilePath, outFileContent)
	# Determinating the time of end
	endTime = time.time()
	# Statistic printing and exiting
	print("\n%d lines have been processed in %s." % (inLinesCount, convertTime(endTime-startTime)))
### End of "genTopReport" ###

# Filtering-out all duplicating addresses and exporting only unique
def getUniqueAddresses(sortByAlphabet = False):
	# Determinating the time of start	
	startTime = time.time()
	# Loading strings from source file into memory
	print("\nLoading strings from source file into memory...", end="\r")
	inFileContent = loadFileContentToMem(inFilePath)
	# Counting number of lines
	inLinesCount = countLinesMem(inFileContent)
	print("Source file contains %d lines." % inLinesCount)
	# Extracting email addresses from pairs list
	print("\nExtracting email addresses:")
	curLineNumber = 0
	mailAddressList = []
	for pair in inFileContent:
		curLineNumber += 1
		print(f"\tProgress: {(curLineNumber/inLinesCount)*100:.2f}%", end="\r")
		splittedPair = re.split(r"([:])", pair, 1)
		## Mail addresses processing
		if len(splittedPair) == 3:
			### Adding into mail addresses list
			mailAddressList.append(splittedPair[0].lower())
	# Purging unused
	del inFileContent
	# Getting unique email addresses as keys from dictionary
	print("\nGetting unique email addresses...")
	mailAddressList = list(dict(Counter(mailAddressList)))
	# Sorting by alphabet
	if sortByAlphabet:
		mailAddressList = sorted(mailAddressList)
	# Getting unique records count
	uniqueRecCount = countLinesMem(mailAddressList)
	# Writing data to file
	print("\nWriting result data to file...")
	writeMemContentToFile(outFilePath, mailAddressList)
	# Purging unused
	del mailAddressList
	# Determinating the time of end
	endTime = time.time()
	# Statistic printing and exiting
	print("\nFound %d unique email addresses in %d occurrences, %d addresses are duplicates." % (uniqueRecCount, inLinesCount, (inLinesCount-uniqueRecCount)))
	print("Processing finished in %s." % (convertTime(endTime-startTime)))
### End of "getUniqueAddresses" ###

# Function for mode checking and calling the appropriate mode function
def checkMode(workMode):
	if (workMode == None):
		print("Please select right work mode!\n" + "Allowed modes are:\n" +
		"1. \"mrg_files\" - Merging two files together (must be used with -im flag)\n" +
		"2. \"re_import\" - Processing an input file with RegEx and exporting matches to an output file\n" +
		"3. \"top_rep\" - Generating top-X report\n" +
		"4. \"uniq_addr\" - Getting unique email addresses")
		sys.exit()
	else:
		if workMode == "mrg_files":
			if mergeFilePath == None:
				print("Please specify a path to the file for merging with source file using \"-im\" flag!")
				sys.exit()
			else:
				mergeFiles(abcSort)
		elif workMode == "re_import":
			reImport(checkFilePath(exclFilePath), abcSort, domainType)
		elif workMode == "top_rep":
			numOfRecords = topNum if (topNum != None and topNum > 0) else 10
			granLvl = granLevel if (granLevel != None) else 0
			genTopReport(numOfRecords, granLvl)
		elif workMode == "uniq_addr":
			getUniqueAddresses(abcSort)
		else:
			print("Mode name is not correct!")
			sys.exit()

# Checking work mode and starting tasks
checkMode(workMode)

# Stop line. You've reached the end of this script. You're winner! :)
