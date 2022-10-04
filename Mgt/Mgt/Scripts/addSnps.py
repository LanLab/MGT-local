import sys
import readAppSettAndConnToDb
import re
import addToTableInOrgDb
import getFromTableInOrgDb


###### COL_NUMBERS

Col_alleleName = 0
Col_snps = 1


#################################### TOP_LVL

def addSnpMutsToDb(projectPath, projectName, orgAppName, fn_snpMuts,settingpath):

	# setting up the appClass
	readAppSettAndConnToDb.setupEnvPath(projectPath, projectName,settingpath)
	organismAppClass = readAppSettAndConnToDb.importAppClassModels(orgAppName)

	# running add snps
	readSnpFileAndDo(organismAppClass, fn_snpMuts)

#################################### AUX.

def readSnpFileAndDo(orgAppClass, fn_snpMuts):
	dict_snpObjs = dict()

	with open(fn_snpMuts, 'r') as fh_:
		for line in fh_:

			line = line.strip()

			arr = line.split("\t")

			if len(arr) > 1:
				[locusId, alleleId] = arr[Col_alleleName].split(":")

				arr_snps = re.split("[\s]*,[\s]*", arr[Col_snps])

			#	print (locusId + "\t" + alleleId) # + "\t" + arr[Col_snps])
			#	print (arr_snps)

				getAlleleAndAddSnpsTo_(orgAppClass, dict_snpObjs, locusId, alleleId, arr_snps)


def getAlleleAndAddSnpsTo_(orgAppClass, dict_snpObjs, locusId, alleleId, arr_snps):

	for snp in arr_snps:
		if snp not in dict_snpObjs:
			# isSnpInDb()
			# print("Add snpObj to db; and then to dict_snpObjs")

			(snpPos, original_aa, altered_aa) = extractSnpInfo(snp)


			# print (snpPos + "\t" + original_aa + "\t" + altered_aa)

			snpObj = getFromTableInOrgDb.getSnp(orgAppClass, snpPos, original_aa, altered_aa)

			if not snpObj:
				# add snp to db.; and then add it to dict_
				snpObj = addToTableInOrgDb.addSnp(orgAppClass, snpPos, original_aa, altered_aa)

			dict_snpObjs[snp] = snpObj

		try:
			addSnpToAllele(orgAppClass, dict_snpObjs[snp], locusId, alleleId)
		except Exception as e:
			print("SNP failed to add")
			print(e)

##################### ALLELE_FNS

def addSnpToAllele(orgAppClass, snpObj, locusId, alleleId):

	try:
		if orgAppClass.models.Allele.objects.filter(locus=locusId, identifier=alleleId).get().snps.filter(id=snpObj.id).exists():
			print ("Not added to db - already present " + str(snpObj.id) + " " + snpObj.original_aa + " " + snpObj.altered_aa + " in " + locusId + " " + alleleId)
			return

		alleleObj = getFromTableInOrgDb.getAllele(orgAppClass, locusId, alleleId)

		addToTableInOrgDb.addSnpToAllele(orgAppClass, snpObj, alleleObj)

	except:
		sys.stderr.write("Error: with " + locusId + " " + alleleId + " " + str(snpObj.position) + "\n")
		raise

##################### SNP_FNS

def extractSnpInfo(snpStr):
	snpStr = re.sub("^[a-zA-Z]+\.", "", snpStr)

	# addToTableInOrgDb.addSnp()
	# snp = snpStr[:-3]
	# mut = snpStr[-3:]
	# print (snpStr + " " +  snp + " " + mut)

	return (snpStr[:-3], snpStr[len(snpStr)-3], snpStr[len(snpStr)-1])
#################################### MAIN

def main():
	usage = "python3 script.py <projectPath> <projectName> <organismAppName> <snpMuts_files> <settingpath>"

	if len(sys.argv) != 6:
		sys.exit("Error: incorrect number of inputs\n" + usage + '\n\n')

	addSnpMutsToDb(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

if __name__ == '__main__':
	main()
