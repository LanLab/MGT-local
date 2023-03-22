import sys
import os
import django
import json
import importlib

def setupEnvPath(projectPath, projectName,settingpath):

	if "/" in settingpath:
		b = os.path.basename(settingpath)
		b = b.replace(".py","")
		settingpath = "Mgt."+b
	sys.path.append(projectPath)
	os.environ['DJANGO_SETTINGS_MODULE'] = settingpath
	django.setup()


def importAppClassModels(appName):
	try:
		appClass = __import__(appName + ".models")
		return appClass

	except:
		sys.exit("Error: application name: " + appName + " not in  specified project settings file.\n")

def importAlleleDirFromSettings(projectName, projectPath,settingpath):
	try:
		settingsObj = __import__(settingpath, globals(), locals(), ['ABS_SUBDIR_ALLELES'], 0)
		# print(settingsObj.DIR_ALLELES)

		# if not settingsObj.SUBDIR_ALLELES.startswith("/"):
		# 	settingsObj.SUBDIR_ALLELES = "/" + settingsObj.SUBDIR_ALLELES
		return (settingsObj.ABS_SUBDIR_ALLELES)
		# return (settingsObj.MEDIA_ROOT +  settingsObj.SUBDIR_ALLELES)

	except:
		sys.stderr.write("Error: unable to import settings file.\n")
		raise

def importRefDirFromSettings(projectName, projectPath,settingpath):
	try:
		settingsObj = __import__(settingpath, globals(), locals(), ['ABS_SUBDIR_REFERENCES'], 0)
		# print(settingsObj.DIR_ALLELES)

		return (projectPath +  settingsObj.ABS_SUBDIR_REFERENCES)

	except:
		sys.stderr.write("Error: unable to import settings file.\n")
		raise

def importTableName(projectPath, appName, tableName):
	try:
		sys.path.append(projectPath)
		imp = importlib.import_module(appName + ".models.autoGenAps")
		# print ()
		tableClass = getattr(imp, tableName)
		return tableClass
	except:
		sys.stderr.write("Error: unable to import table class.\n")
		raise

def importTableName_simple(projectPath, appName, tableName):
	try:
		sys.path.append(projectPath)
		imp = importlib.import_module(appName + ".models")
		# print ()
		tableClass = getattr(imp, tableName)
		return tableClass
	except:
		sys.stderr.write("Error: unable to import table class.\n")
		raise

def loadJsonFile(jsonFileFullPathName):

	jsonObj = None

	with open(jsonFileFullPathName, 'r') as fh_:
		jsonObj = json.load(fh_)

	if not jsonObj:
		sys.exit("Error: could not read json file, or file empty\n")

	return jsonObj
