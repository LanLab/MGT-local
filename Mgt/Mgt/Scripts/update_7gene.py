from time import sleep as sl
import argparse
import readAppSettAndConnToDb
import addToTableInOrgDb
import addIsolates
import getFromTableInOrgDb
import re
import sys


def parseargs():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--projectPath", help="Path to project folder",
                        default="/path/to/MGT/Mgt/Mgt")
    parser.add_argument("--projectName", help="Name of project",
                        default="Mgt")
    parser.add_argument("--appname", help="mgt application name",
                        default="Salmonella")

    args = parser.parse_args()
    return args


# def update7gene(User, appClass, fn_isolateInfo):
#     sl(10)

def importrootDirFromSettings(projectName):
	try:
		settingsObj = __import__(projectName + ".settings", globals(), locals(), ['ABS_MEDIA_ROOT'], 0)
		# print(settingsObj.DIR_ALLELES)

		return (settingsObj.ABS_MEDIA_ROOT)
		# return (settingsObj.MEDIA_ROOT +  settingsObj.SUBDIR_ALLELES)

	except:
		sys.stderr.write("Error: unable to import settings file.\n")
		raise

def main():

    args = parseargs()

    readAppSettAndConnToDb.setupEnvPath(args.projectPath, args.projectName,settingpath)

    appClass = readAppSettAndConnToDb.importAppClassModels(args.appname)

    isolateObj = appClass.models.Isolate.objects.filter(mgt=None)

    alleles_pref = importrootDirFromSettings(args.projectName)
    c = 0
    for i in isolateObj:
        print(i.identifier)
        if i.file_alleles:
            # print(i.file_alleles)
            allele_file = alleles_pref + str(i.file_alleles)
            # print(allele_file)
            alleles = open(allele_file,"r").read().splitlines()
            for line in alleles:
                if "7_gene_ST" in line:
                    st = line.split(":")[-1]
                    if st.isdigit() and not i.mgt1:
                        # pass
                        # print(i.identifier,st)
                        i.mgt1 = int(st)
                        i.save()
                        c+=1
                    # else:
                    #     print(i.identifier,st)
                    #     sl(0.1)
        # i.mgt = X
        # i.save()
    print(c)

if __name__ == '__main__':
    main()