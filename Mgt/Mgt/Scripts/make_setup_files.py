import os
import shutil
import sys
from time import sleep as sl
from Bio import SeqIO,Seq, SeqRecord
from os import path
from shutil import copyfile,copy
import argparse
from glob import glob
import importlib.util

"""
TODO
1 - make ref info file - refFileInfo.json - DONE
2 - make loci in ref pos file - lociLocationsInRef.txt - DONE
3 - make scheme info - schemesInfo.txt - DONE
4 - tables_ccs.txt - DONE
5 - tables_aps.txt - DONE
6 - $ref_files"/ref_$appname_alleles - DONE
7 - $ref_files"/snpMuts.txt - DONE
8 - $ref_files"schemeToApMapping.txt" $ref_files"AllelicProfiles/"  - DONE
9 - $ref_files"ccInfo.txt"  $ref_files"ClonalComplexes/"  - DONE
10 - $ref_files"isolate_info.tab
                Col_username = 0
                Col_projectName = 1
                Col_privStatus = 2
                Col_isolateId = 3


                Col_date = 6 # file isolate_metadata_.txt
                Col_year = 7
                Col_month = 8
                Col_postcode = 9 # file isolate_info.txt
                Col_state = 10 # file isolate_info.txt
                Col_country = 11 # file isolate_info.txt
                Col_continent = 12 # file isolate_info.txt
                Col_source = 13 # file isolate_metadata_.txt
                Col_type = 14 # file isolate_metadata_.txt
                Col_host = 15 # file isolate_metadata_.txt
                Col_hostDisease = 16 # file isolate_metadata_.txt

                Col_mgt1 = 18
                Col_serovar = 19
11 - $ref_files"hgt_annotations.tab"
12 - views head
    from django.db import models
    from .defModels import *
    from .autoGenAps import *
    from .autoGenCcs import *

"""





def parseargs():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-r","--refgenome", help="File path to reference genome fasta file")
    parser.add_argument("-a", "--appname", help="Application name (normally uppercase first letter (i.e. Salmonella)",default="Blankdb")
    parser.add_argument("-d", "--dbname", help="postgres database name (normally lowercase first letter (i.e. salmonella)",default="blankdb")
    parser.add_argument("-s", "--species",
                        help="Full species name (put in double quotes) i.e. Vibrio cholerae",default="Salmonella enterica")
    parser.add_argument("-t", "--temp",
                        help="setup files temporary folder", default= "tmp")
    # parser.add_argument("--keeptemp", help="keep database setup files", action='store_true')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--allelesfile",
                        help="file of allele sequences if locus positions not known. Cannot be used with --allele_locations")
    group.add_argument("--allele_locations",
                        help="allele location in ref fileCannot be used with --allelesfile")
    parser.add_argument("--allref", help="location of species specific alleles folder which is used to store 'reference allele' collections used as inputs for reads_to_alleles.py")
    parser.add_argument("--schemeno",help="number of MGT levels in scheme",default=9,type=int)
    parser.add_argument("--schemeaccessions", help="folder containing one file per scheme each file contains loci for that scheme one locus per line", required=True)
    parser.add_argument("--mgt1is7gene",
                        help="MGT1 is traditional MLST called by separate mlst program",
                        action='store_true')
    parser.add_argument("--odcls",
                        help="comma separated list of cluster cutoffs or range or both i.e 1,2,5 or 1-8 or 1,2,5-10",
                        default="1,2,5,10")
    parser.add_argument("--settings",help="settings prefix (settings file in MGT/Mgt/Mgt/Mgt)")





    args = parser.parse_args()
    return args

def get_distances_frm_args(args):
    diststring = args.odcls
    dists = diststring.split(",")
    distances = []
    for i in dists:
        if "-" in i:
            n = i.split("-")
            nlist = list(range(int(n[0]),int(n[1])+1))
            # distance cutoffs seems to be non inclusive i.e. cutoff of 3 means max distance is 2
            # therefore need to add 1 to all values
        else:
            nlist = [int(i)]
        distances += nlist
    return distances

def maketmp(args):
    if not path.exists(args.temp):
        os.makedirs(args.temp)
    else:
        shutil.rmtree(args.temp)
        os.makedirs(args.temp)
    snp = open(args.temp+"/snpMuts.txt","w")
    snp.close()

def make_refjson(args):
    chromno = len(list(SeqIO.to_dict(SeqIO.parse(args.refgenome,"fasta")).keys()))
    refpath = args.refgenome.replace(" ","\ ")
    outstring = f"""{{
            "identifier":"{args.dbname}",
            "organism":"{args.species}",
            "description": "",
            "chromosomes": [
                    {{
                            "number": {chromno},
                            "loc_and_filename": "{refpath}"
                    }}
            ]
    }}"""
    print("1 - made_refjson")
    outf = open(args.temp+"/refFileInfo.json","w")
    outf.write(outstring)
    outf.close()
    return outstring

def locations_from_genome(args):
    inref = SeqIO.to_dict(SeqIO.parse(args.refgenome, "fasta"))
    keyorder = sorted(list(*inref.keys()))
    genomechroms = [inref[x].seq for x in keyorder]

    inalleles = SeqIO.to_dict(SeqIO.parse(args.allelesfile, "fasta"))
    outf = open(
        args.temp + "/lociLocationsInRef.txt",
        "w")
    outrefalleles = args.temp + f"/{args.appname}_alleles/"
    if not path.exists(outrefalleles):
        os.makedirs(outrefalleles)
    c = 0
    chromno = 1
    locils = []
    for locus in inalleles:
        allele = inalleles[locus]
        for chrom in genomechroms:
            genomepos = chrom.find(allele.seq) + 1
            loc = locus.split(":")[0]
            locils.append(loc)
            # print(allele.id)
            if genomepos == 0:
                genomepos = chrom.find(allele.seq.reverse_complement()) + 1
                genomeend = genomepos + len(allele.seq) - 1
                outf.write(f"{loc}\t{genomepos}\t{genomeend}\t-\t{chromno}\n")
                c += 1
            else:
                genomeend = genomepos + len(allele.seq) - 1
                outf.write(f"{loc}\t{genomepos}\t{genomeend}\t+\t{chromno}\n")
                c += 1

            allelefile = outrefalleles+"/"+loc + ".fasta"
            SeqIO.write(allele,allelefile,"fasta")
            chromno+=1

    outf.close()

    outfolder = f"{args.allref}/{args.appname}/"
    outpath = f"{outfolder}/{args.appname}_intact_alleles.fasta"
    if not path.exists(outfolder):
        os.makedirs(outfolder)
    shutil.copy(args.allelesfile,outpath)


    return locils

def make_ref_allele_files(args,inp):
    outrefalleles = args.temp + f"/{args.appname}_alleles/"
    if not path.exists(outrefalleles):
        os.makedirs(outrefalleles)
    inref = SeqIO.to_dict(SeqIO.parse(args.refgenome, "fasta"))
    # print(inref)
    # print(args.refgenome)

    keyorder = sorted(list(inref.keys()))
    chromdict = {str(keyorder.index(x)+1):x for x in keyorder}
    print('keyorder: ', keyorder)
    print('chromdict: ', chromdict)
    allalleles = []
    for line in inp:
        col = line.split("\t")
        loc = col[0]
        st = int(col[1])
        en = int(col[2])
        orient = col[3]
        chrom = col[4]
        # print('chrom: ', type(chrom))
        if chrom not in chromdict.keys():
            # print(chrom, chromdict.keys())
            sys.exit(f"ERROR: Please ensure that the number of chromosomes specified in {args.allele_locations} is correct")
        else:
            # print('this is: ', chrom)
            chromid =  chromdict[chrom]
            if en <= len(inref[chromid].seq):
                alleleseq = inref[chromid].seq[st-1:en]
                if orient == "-":
                    alleleseq = alleleseq.reverse_complement()
                outallele = SeqRecord.SeqRecord(alleleseq,id=loc+":1",description="")
                SeqIO.write(outallele,outrefalleles+"/"+loc+".fasta","fasta")
                allalleles.append(outallele)
            else:
                print('en: ', en)
                print('inref: ', len(inref[chromid].seq))
                sys.exit(f"ERROR: please ensure that chromosome number in {args.allele_locations} corresponds to the alphabetical order of chromosome fasta headers")

    outfolder = f"{args.allref}/{args.appname}"
    outpath = f"{outfolder}_intact_alleles.fasta"
    print('outfolder:', outfolder)
    print('outpath: ', outpath)
    if not path.exists(outfolder):
        os.makedirs(outfolder)
    SeqIO.write(allalleles,outpath,"fasta")

def make_posinref(args):
    if args.allele_locations:
        copyfile(args.allele_locations,args.temp+"/lociLocationsInRef.txt")
        inp = open(args.allele_locations,"r").read().splitlines()
        locils = [x.split("\t")[0] for x in inp]
        make_ref_allele_files(args,inp)
    else:
        locils = locations_from_genome(args)

    print("2 - made refpos file and ref alleles")
    return locils

def make_schemesInfo(args,locils):
    outf = open(args.temp+"/schemesInfo.txt","w")
    min = 0
    if args.mgt1is7gene:
        min=1


    schemefolder = args.temp + "/Schemes/"
    os.makedirs(schemefolder)
    missing = False
    misstring = ""
    usedloci = set()
    alllociset = set(locils)
    apfolder = args.temp + "/AllelicProfiles/"
    schemes = []
    for i in range(min,args.schemeno):
        print('range', range(min,args.schemeno))
        schemeno = i+1
        schemeaccfile = f'{args.schemeaccessions}/MGT{schemeno}_gene_accessions.txt'
        if not path.exists(schemeaccfile):
            sys.exit(f"scheme loci file {schemeaccfile} does not exist")
        outf.write("MGT{0}\t1\tMGT{0}_gene_accessions.txt\tMGT{0}\n".format(schemeno))
        copy(schemeaccfile, schemefolder)
        scheme = "MGT"+str(schemeno)
        schemes.append(scheme)
        schemeloci = set(open(schemeaccfile,"r").read().splitlines())
        schemelocitouse = list(sorted(list(schemeloci)))
        schemelocitouse = [x.replace("_","") for x in schemelocitouse]
        usedloci.union(schemeloci)

        intersect = list(schemeloci.intersection(alllociset))
        if len(intersect) != len(schemeloci):
            diff = list(schemeloci.difference(alllociset))
            diffstr = ",".join(diff)
            misstring += f"These {scheme} loci not in loci definitions: {diffstr}\n"
            missing = True

        if not path.exists(apfolder):
            os.makedirs(apfolder)
        outapfile = apfolder + f"{scheme}_gene_profiles.txt"
        outap = open(outapfile,"w")
        locus_str = "\t".join(schemelocitouse)
        allele_str = "\t".join(["1"]*len(schemelocitouse))
        outap.write(f"ST\tdST\t{locus_str}\n1\t0\t{allele_str}\n")
        outap.close()
    outf.close()

    notused = ",".join(list(alllociset.difference(usedloci)))
    if len(notused) > 0:
        misstring += f"These loci not used in any level but are in loci definitions: {notused}\n"

    if missing:
        sys.exit(misstring)


    print("3 - made schemeinfo")
    return schemes

def make_cc_inp_files(args,mgt,odc=False):
    ccfolder = args.temp+"/ClonalComplexes"
    if not path.exists(ccfolder):
        os.makedirs(ccfolder)
    if not odc:
        cc = open(ccfolder+f"/MGT{mgt}_cc.txt","w")
        cc.write(f"ST\tdst\toriginal_MGT{mgt}_CC\tcurrent_MGT{mgt}_CC\n1\t0\t1\t1\n")
        cc.close()
        ccmerge = open(ccfolder+f"/MGT{mgt}_cc_merges.txt","w")
        ccmerge.write("Original cc\tMerged with")
        ccmerge.close()
    else:
        cc = open(ccfolder+f"/MGT{mgt}{odc}_cc.txt","w")
        cc.write(f"ST\tdst\toriginal_MGT{mgt}{odc}_CC\tcurrent_MGT{mgt}{odc}_CC\n1\t0\t1\t1\n")
        cc.close()
        ccmerge = open(ccfolder+f"/MGT{mgt}{odc}_cc_merges.txt","w")
        ccmerge.write("Original cc\tMerged with")
        ccmerge.close()

def make_tables(args):
    odcdists = get_distances_frm_args(args)
    print(odcdists)
    outf = open(args.temp+"/tables_ccs.txt","w")
    outaptables = open(args.temp + "/tables_aps.txt", "w")
    outapmapping = open(args.temp + "/schemeToApMapping.txt", "w")
    outccInfo = open(args.temp+"/ccInfo.txt","w")

    minlevel = 1
    maxlevel = args.schemeno
    odc1 = False
    if args.mgt1is7gene:
        minlevel=2
    for i in range(minlevel,args.schemeno+1):
        if i == maxlevel and min(odcdists) == 1:
            outf.write(f"MGT{i}\t1,2\t{i},1\tMGT{i},ODC1\t1\n")
            outccInfo.write(f"MGT{i}\tMGT{i}_cc.txt	MGT{i}_cc_merges.txt	1_{i}\n")
            odc1=True
            make_cc_inp_files(args,i)
            outaptables.write(f"MGT{i}\t{i}\tMGT{i}\n")
            outapmapping.write(f"MGT{i}\tMGT{i}_gene_profiles.txt\n")
        else:
            outf.write(f"MGT{i}\t1\t{i}\tMGT{i}\t1\n")
            outccInfo.write(f"MGT{i}\tMGT{i}_cc.txt	MGT{i}_cc_merges.txt	1_{i}\n")
            make_cc_inp_files(args, i)
            outaptables.write(f"MGT{i}\t{i}\tMGT{i}\n")
            outapmapping.write(f"MGT{i}\tMGT{i}_gene_profiles.txt\n")

    odcdists = [x for x in odcdists if x != 1]
    c = 1
    if odc1:
        c+=1
    for i in odcdists:
        outf.write(f"MGT{maxlevel}\t2\t{c}\tODC{i}\t{i}\n")
        outccInfo.write(f"MGT{maxlevel}\tMGT{maxlevel}{i}_cc.txt	MGT{maxlevel}{i}_cc_merges.txt	2_{c}\n")
        c+=1
        make_cc_inp_files(args, maxlevel,odc=i)
    outf.close()
    outccInfo.close()
    outaptables.close()
    outapmapping.close()
    print("4 - made cc and ap tables and files")

def make_isolateandmgt(args,schemes):
    """
        Col_username = 0
        Col_projectName = 1
        Col_privStatus = 2
        Col_isolateId = 3


        Col_date = 6 # file isolate_metadata_.txt
        Col_year = 7
        Col_month = 8
        Col_postcode = 9 # file isolate_info.txt
        Col_state = 10 # file isolate_info.txt
        Col_country = 11 # file isolate_info.txt
        Col_continent = 12 # file isolate_info.txt
        Col_source = 13 # file isolate_metadata_.txt
        Col_type = 14 # file isolate_metadata_.txt
        Col_host = 15 # file isolate_metadata_.txt
        Col_hostDisease = 16 # file isolate_metadata_.txt

        Col_mgt1 = 18
        Col_serovar = 19
    """
    outhead = "Username\tProject\tprivacy_status\tIsolatename\t\t\tdate\tyear\tmonth\tpostcode\tstate\tcountry\tcontinent\tsource\ttype\thost\thostdisease\t\t7geneMLST\tserovar\n"
    outhead += "Ref\tRef\tPublic\tRef\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\n"
    outf = open(args.temp + "/isolate_info.tab", "w")
    outf.write(outhead)
    outf.close()


    outmgt = "Username\tProject\tIsolatename\tAssignmentStatus\t{}\n".format("\t".join(schemes))
    outmgt += "Ref\tRef\tRef\tA\t{}\n".format("\t".join(["1.0"]*len(schemes)))
    outf = open(args.temp + "/mgt_annotations.tab", "w")
    outf.write(outmgt)
    outf.close()
    print('isolate and mgts created')

def load_settings(args):
    if ".py" in args.settings:
        folder = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
        s = args.settings.split("/")[-1]
        settingsfile = folder + "/Mgt/Mgt/" + s
    else:
        folder = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
        settingsfile = folder +"/Mgt/Mgt/"+ args.settings + ".py"

    if not path.exists(settingsfile):
        sys.exit("settings file not found at: {}".format(settingsfile))
    spec = importlib.util.spec_from_file_location("settings", settingsfile)
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)

    return settings

def make_db_folders(settings,args):
    folderstocheck = [settings.ABS_SUBDIR_REFERENCES,
                      settings.ABS_SUBDIR_ALLELES,
                      settings.ABS_MEDIA_ROOT,
                      settings.FILES_FOR_DOWNLOAD,
                      settings.TMPFOLDER,
                      settings.TMPFOLDER+"/"+args.appname,
                      settings.TMPFOLDER+"/"+args.appname+"/tmp",
                      settings.TMPFOLDER+"/"+args.appname+"/outfiles",
                      settings.TMPFOLDER+"/"+args.appname+"/fastq_tmp"]
    for folder in folderstocheck:
        dirname = "/".join(folder.split("/")[:-1])
        if not os.path.exists(dirname):
            print("created folder: {}".format(dirname))
            os.mkdir(dirname)
        if not os.path.exists(folder):
            print("created folder: {}".format(folder))
            os.mkdir(folder)
def main():
    args = parseargs()
    settings=load_settings(args)
    maketmp(args)
    make_db_folders(settings,args)
    make_refjson(args)
    locils = make_posinref(args)
    schemes = make_schemesInfo(args,locils)
    make_tables(args)
    make_isolateandmgt(args,schemes)

if __name__ == "__main__":

    main()
