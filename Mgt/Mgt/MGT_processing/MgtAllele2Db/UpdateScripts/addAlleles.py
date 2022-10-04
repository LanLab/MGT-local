import sys
import re
from Bio import SeqRecord, SeqIO
from MGT_processing.MgtAllele2Db.UpdateScripts import getFromTableInOrgDb, readAppSettAndConnToDb, addToTableInOrgDb
# from Static import *


################################# TOP_LVL

def addAlleles(projectPath, projectName, appName,dir_alleleSeqs, alleles_out_dict,settingtype):
    ## change dir_alleleSeqs to use alleles_dict_out

    # setting up the appClass
    readAppSettAndConnToDb.setupEnvPath(projectPath, projectName,settingtype)
    organismAppClass = readAppSettAndConnToDb.importAppClassModels(appName)

    # dir_seqsToSaveTo = readAppSettAndConnToDb.importAlleleDirFromSettings(projectName)
    # print(organismAppClass,dir_seqsToSaveTo)

    # for each file in the folder

    extractAndAddAlleles(organismAppClass, dir_alleleSeqs, projectPath, appName, alleles_out_dict)


def extractAndAddAlleles(organismAppClass, dir_alleleSeqs, projectPath, appName, alleles_out_dict):
    # fns = glob.glob(dir_alleleSeqs + "*")

    for locusId in alleles_out_dict:
        for allelels in alleles_out_dict[locusId]:
            alleleId = allelels[1]
            allele_seq = allelels[2]

            if not doesAlleleExistInDb(organismAppClass, locusId, alleleId):
                print(locusId,alleleId)
                seqRec = SeqRecord.SeqRecord(allele_seq,id=locusId+":"+alleleId,)
                print(dir_alleleSeqs)
                seqFileLoc = appendSeqToFile(appName, dir_alleleSeqs, locusId, seqRec)


                addAlleleToDb(organismAppClass, locusId, alleleId, len(seqRec.seq), False, seqFileLoc)

            else:
                print("Allele already in db, not added: " + locusId + " " + alleleId)

            # print(locusId, alleleId)


def allele_seq_unique(existing_alleles_file,newseq):
    exist = SeqIO.parse(existing_alleles_file,"fasta")

    for existseq in exist:
        if existseq.seq == newseq.seq:
            return False
    return True

def appendSeqToFile(appName, alleleSeqDirName, locusId, seqRec):
    fn_ = alleleSeqDirName + "/" + locusId + ".fasta"
    # print(fn_)
    # print(">{}\n{}\n".format(seqRec.id,str(seqRec.seq)))
    # print(fn_)

    if not allele_seq_unique(fn_,seqRec):
        print("New allele for {} is not unique!!\n{}\n{}".format(locusId,seqRec.id,str(seqRec.seq)))
        sys.exit()
    else:
        outf = open(fn_,"a+")
        outf.write(">{}\n{}\n".format(seqRec.id,str(seqRec.seq)))
        outf.close()

    #
    # print("Seq. appended to: " + fn_)

    return fn_


def addAlleleToDb(organismAppClass, locusId, alleleId, seqLen, hasSnp, fileLocation):
    locusObj = getFromTableInOrgDb.getLocus(organismAppClass, locusId)

    addToTableInOrgDb.addAllele(organismAppClass, alleleId, locusObj, seqLen, hasSnp, fileLocation)


def doesAlleleExistInDb(organismAppClass, locusId, alleleId):
    set_allele = organismAppClass.models.Allele.objects.filter(locus=locusId, identifier=alleleId)

    if len(set_allele) == 0:
        # sys.stderr.write("Locus: " + locusId + ", Alelle: " + alleleId + " not found in db." + '\n')
        return False

    return True


# except:
# 	sys.stderr.write("Locus: " + locusId + ", Alelle: " + alleleId + " not found in db." + '\n')


################################# MAIN


def addSlashIfNotThere(dir_):
    if not re.search(".*/$", dir_):
        dir_ = dir_ + "/"

    return dir_


def main():
    usage = "python3 scripty.py <projectPath> <projectName> <appName> <alleleSeqsFolder> <settingpath>"
    if len(sys.argv) != 6:
        sys.exit("Error: incorrect number of inputs\n" + usage + '\n\n')

    sys.argv[4] = addSlashIfNotThere(sys.argv[4])

    addAlleles(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])


if __name__ == '__main__':
    main()
