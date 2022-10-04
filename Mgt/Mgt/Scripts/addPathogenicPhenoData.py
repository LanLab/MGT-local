#!/usr/bin/python3 

import argparse 
import pathlib 
import sys
import re 
import readAppSettAndConnToDb

# To run e.g.  python3 addPathogenicPhenoData.py --ftpFile ../../../20220224-AMRFinderPlusData/PDG000000002.2400.metadata.tsv --projectPath ../ --projectName Mgt --settingPath sklocal --appName Salmonella 1> outfile 2> error 

########################## TOP_LVL 
def readAndAddData(fn_ftpData, projectPath, projectName, settingPath, appName): 


	# setting up the appClass
	readAppSettAndConnToDb.setupEnvPath(projectPath, projectName,settingPath)
	appClass = readAppSettAndConnToDb.importAppClassModels(appName)

	amrTableObj = readAppSettAndConnToDb.importTableName_simple(projectPath, appName, 'Amr')
	virulenceTableObj = readAppSettAndConnToDb.importTableName_simple(projectPath, appName, 'Virulence')
	stressTableObj = readAppSettAndConnToDb.importTableName_simple(projectPath, appName, 'Stress')
	
	dict_cols = {
		"AMR_genotypes": -1,
		"AMR_genotypes_core": -1, 
		"stress_genotypes": -1,
		"virulence_genotypes": -1, 
		"amrfinder_version": -1, 
		"refgene_db_version": -1,
		"Run": -1
	}
	

	with open(fn_ftpData, 'r') as fh: 
		isHeader = True

		for line in fh: 
			line = line.strip()
			arr = line.split("\t") 

			if isHeader == True: 
				extractHeader(arr, dict_cols)
				isHeader = False
				continue 
			

			print (arr[dict_cols['Run']])
			# Check if isolate exists
			isoObj = getIsolateObj(appClass, arr[dict_cols['Run']])
			
			if isoObj: 
				amr = []; 
				virulence = [] 
				stress = []

				extractGenes(amr, arr[dict_cols['AMR_genotypes']])
				extractGenes(amr, arr[dict_cols['AMR_genotypes_core']])
				extractGenes(virulence, arr[dict_cols['virulence_genotypes']])
				extractGenes(stress, arr[dict_cols['stress_genotypes']])

				# print (arr[dict_cols['amrfinder_version']] + '\t' + arr[dict_cols['refgene_db_version']] + '\t' + str(amr) + '\t' + str(stress) + '\t' + str(virulence))

				addGenesToDbIfNotPresent(amr, amrTableObj)
				addGenesToDbIfNotPresent(virulence, virulenceTableObj)
				addGenesToDbIfNotPresent(stress, stressTableObj)

				linkGenesToIso(amr, isoObj, amrTableObj, 'Amr')
				linkGenesToIso(virulence, isoObj, virulenceTableObj, 'Virulence')
				linkGenesToIso(stress, isoObj, stressTableObj, 'Stress')

				addVersionNumber(isoObj, arr[dict_cols['amrfinder_version']], arr[dict_cols['refgene_db_version']]) 


########################## AUX
def addVersionNumber(isoObj, amrfinder_version, refgene_db_version): 
	isoObj.amrfinder_version = amrfinder_version
	isoObj.refgenedb_version = refgene_db_version
	isoObj.save() 

def linkGenesToIso(amr, isoObj, amrTableObj, tableType): 
	for gene in amr: 
		pathoPhenoObj = getAPathoPhenoObj(amrTableObj, gene)
		
		# check if it does not exist for isolate

		if tableType == 'Amr': 
			if len(isoObj.amr.filter(gene=gene)) == 0: 
				isoObj.amr.add(pathoPhenoObj)

		elif tableType == 'Virulence': 
			if len(isoObj.virulence.filter(gene=gene)) == 0: 
				isoObj.virulence.add(pathoPhenoObj)	

		elif tableType == 'Stress': 
			if len(isoObj.stress.filter(gene=gene)) == 0: 
				isoObj.stress.add(pathoPhenoObj)

			
def getAPathoPhenoObj(tableObj, geneId):
	pathoPhenoObj = tableObj.objects.get(gene=geneId)

	return pathoPhenoObj


def getIsolateObj(orgAppClass, isolateId): 
	
	isoObj = None 

	try: 
		isoObj = orgAppClass.models.Isolate.objects.get(identifier=isolateId)
		sys.stderr.write("Note: " + isolateId + " is found\n")
	except: 
		sys.stderr.write("Note: " + isolateId + " not found\n")
		 

	return isoObj  

def addGenesToDbIfNotPresent(arr_genes, tableObj): 

	for gene in arr_genes: 
		pathoPhenoObjs = getPathoPhenoObjs(tableObj, gene)

		if len(pathoPhenoObjs) == 0: 
			# print("Add to database") 
			addPathoPhenoObj(tableObj, gene) 


def addPathoPhenoObj(tableObj, gene): 

	i = tableObj(gene=gene)

	try: 
		i.save() 
	except:
		sys.stderr.write("Error: unable to save " + gene + " " + type)
		raise 

def getPathoPhenoObjs(tableObj, gene):

	pathoPhenoObjs = tableObj.objects.filter(gene=gene)
	
	return pathoPhenoObjs 	


def extractGenes(arr_genes, val):
	if val != "NULL": 
		val = re.sub('\"', "", val)
		arr = val.split(",")

		

		for gene in arr: 
			if gene not in arr_genes: 
				arr_genes.append(gene)



def extractHeader(arrLine, dict_cols): 

	for idx, val in enumerate(arrLine): 
		if val in dict_cols: 
			dict_cols[val] = idx


	for (key, val) in dict_cols.items(): 
		if val == -1: 
			sys.exit("Error: a column in the header is missing\n"); 
	
	# print (dict_cols) 


########################## MAIN 
def main(): 
	parser = argparse.ArgumentParser()

	parser.add_argument('--ftpFile', type=pathlib.Path, help='ftpFile downloaded from NCBI', required=True)
	# parser.add_argument('--sum', dest='accumulate', action='store_const' const=sum, default=max, help='sum the integers (default: find the max)')


	parser.add_argument('--projectPath', type=str, help='projectPath (e.g. ../)', required=True)
	parser.add_argument('--projectName', type=str, help='projectName (e.g. Mgt)', required=True)
	parser.add_argument('--settingPath', type=str, help='settingPath (e.g. ../)', required=True)
	parser.add_argument('--appName', type=str, help='appName (e.g. Salmonella)', required=True)

	args = parser.parse_args()


	# print(args.ftpFile)

	readAndAddData(args.ftpFile, args.projectPath, args.projectName, args.settingPath, args.appName)

if __name__ == '__main__':
	main()