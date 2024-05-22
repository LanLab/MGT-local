import math
from time import sleep as sl
import pandas as pd
import numpy as np
import argparse
import datetime
import sys

def count_values_in_range(series):
    newseries = series.replace("nan",None)
    n = newseries.nunique(dropna=True)
    return n

def parseargs():
    debug = False
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,description='A script for identifying candidate loci for MGT levels using isolate allele profiles and clade assignments.')

    if not debug:

        parser.add_argument("-c", "--clade_def", help="tab delimited file with each isolate as a row and one or more columns defining clades. Isolate names should match those in allele_profile.",required=True)
        parser.add_argument("-a", "--allele_profile",
                            help="tab delimited file with locus as a column and each isolate as a row. Can handle 0 alleles and negative alleles from MGT processing. Isolate names should match those in clade_def.",required=True)
        parser.add_argument("-o", "--outprefix", help="output path prefix for both output files",required=True)
        parser.add_argument("--ignore_loci", help="file with one locus per line. Loci to be ignored if they have already been used or are undesirable", default="None")
        parser.add_argument("--sens_cutoff", help="minimum sensitivity of a locus when describing clade of interest", default=0.3,type=float)
        parser.add_argument("--spec_cutoff", help="minimum specificity of a locus when describing clade of interest",
                            default=0.8, type=float)
        parser.add_argument("--clade_sets", help="name of one or more columns (comma separated) defining clades of interest in --clade_def input",
                            type=str, default = 'all')
        parser.add_argument("--target_clades", help="name of one or more particular clades (comma separated) listed in --cladeset column. set as all to process all clades in set",
                            type=str, default = 'all')
        parser.add_argument("--cladeidcol", help="the column name in --clade_def for the strain identifier",
                            type=str, default="Strain")
        parser.add_argument("--apidcol", help="the column name in --allele_profile for the strain identifier",
                            type=str, default="Strain")
        parser.add_argument("--showneg",
                            help="do not replace negative alleles with positive in output allele profiles",
                            action='store_true')
    args = parser.parse_args()

    return args

def undst(x):
    if isinstance(x,float):
        # x = str(x)
        if math.isnan(x):
            return "0"
        else:
            #print(x)
            #sl(1)
            return str(int(math.floor(x)))
    elif isinstance(x,int):
        return str(x)
    else:
        if x.startswith("-"):
            return x.split("_")[0][1:]
        else:
            return x

def main():

    # load arguments
    args = parseargs()

    # load clade definitions tab delimited file
    inmeta = pd.read_csv(args.clade_def,sep="\t",dtype=str)
    if args.cladeidcol not in list(inmeta.columns):
        sys.exit("please check that column name in --cladeidcol is in your clade_def input file headers")

    # check if one or more clade sets and return as list
    if "," in args.clade_sets:
        cladesets = args.clade_sets.split(",")
    elif args.clade_sets == "all":
        cladesets = list(inmeta.columns)
        cladesets = [x for x in cladesets if x != args.cladeidcol]
    else:
        cladesets = [args.clade_sets]

    
    sys.stdout.write("\nLoading inputs\n")

    # write header to output file including sens and spec cutoffs


    #  load loci to ignore
    if args.ignore_loci == "None":
        usedloci =[]
    else:
        usedloci = open(args.ignore_loci).read().splitlines()

        # load allele_profile tab delimited file
    inap = pd.read_csv(args.allele_profile,sep="\t",na_values=[0],dtype='object')
    if args.apidcol not in list(inap.columns):
        sys.exit("please check that column name in --apidcol is in your allele_profile input file headers")

    # merge clade definition and allele profile file
    merged = inap.merge(inmeta,left_on=args.apidcol,right_on=args.cladeidcol)

    sys.stdout.write("Checking input clade ids\n")

    # check if one or more target clades and return as list
    if "," in args.target_clades:
        targetclades = args.target_clades.split(",")
        possclades = []
        for cladecol in cladesets:
            possclades += list(merged[cladecol].dropna().unique())
        notincols = list(set(targetclades).difference(set(possclades)))
        if len(notincols) > 0:
            sys.exit(f"the following target clades are not specified in the --clade_set columns specified: {','.join(notincols)}")
    elif args.target_clades == "all":
        targetclades = []
        for cladecol in cladesets:
            targetclades += list(merged[cladecol].dropna().unique())
    else:
        targetclades = [args.target_clades]
        possclades = []
        for cladecol in cladesets:
            possclades += list(merged[cladecol].dropna().unique())
        notincols = list((set(targetclades)).difference(set(possclades)))
        if len(notincols) > 0:
            sys.exit(f"the following target clades are not specified in the --clade_set columns specified: {','.join(notincols)}")


    sys.stdout.write(f"Looking for candidate loci for target clade/s: {','.join(map(str, targetclades))}, from column/s: {','.join(map(str, cladesets))}.\n")

    #total isolates part of clade
    from collections import Counter
    cladelist = []
    for cladecol in cladesets:
        cladelist += list(merged[cladecol].dropna())
    cladeisolates = Counter(cladelist)

    sys.stdout.write("Searching for candidate loci: \n")

    # setup progress printing
    cols = list(inap.columns)
    tot = len(cols)-2
    c = 0
    plist = []

    # list for storing used loci to generate allele profile subset
    outputlist = []

    minorallele = {}
    outs = {}

    # iterate over loci in alelle profile column headers starting from 3rd column and skip if in usedloci file
    for locus in cols[2:]:
        if locus not in usedloci:
            # iterate over clade definition columns set in --clade_set
            for cladecol in cladesets:
                columnclades = merged[cladecol].dropna().unique()
                for clade in targetclades:
                    if clade in columnclades:
                        zeros = merged[locus].isna().sum()
                        newseries = merged[locus].replace("nan", None).dropna()
                        negs = newseries.str.contains('-', na=False).sum()
                        c1series = merged.loc[merged[cladecol]==clade,locus]
                        c1series = c1series.replace("nan",None).dropna()
                        c1series = c1series.map(undst)
                        ids,c1countls = np.unique(c1series, return_counts=True)
                        c1counts = dict(zip(ids, c1countls))
                        c1types = list(c1series.unique())
                        c1types = set(c1types)
                        nonc1series = merged.loc[merged[cladecol] != clade,locus]
                        nonc1series = nonc1series.replace("nan",None).dropna()
                        nonc1series = nonc1series.map(undst)
                        ids,nc1counts = np.unique(nonc1series, return_counts=True)

                        nonc1counts = dict(zip(ids, nc1counts))
                        cladenum = cladeisolates[clade]
                        for type in c1types:
                            if type not in ["nan",""]:
                                total_in_c1 = sum(c1countls)
                                total_for_type = c1counts[type]
                                tp = int(total_for_type)
                                if type in nonc1counts:
                                    fp = nonc1counts[type]
                                else:
                                    fp=0
                                fn = int(total_in_c1) - int(total_for_type)
                                tn = int(sum(nc1counts)) - fp

                                if (tp + fn) == 0:
                                    sens = 0
                                else:
                                    sens = float(tp) / (tp + fn)
                                if (fp + tn) == 0:
                                    spec = 0
                                else:
                                    spec = float(tn) / (fp + tn)
                                fpdetails = {}

                                if sens > args.sens_cutoff and spec > args.spec_cutoff:
                                    fndetails = {x: c1counts[x] for x in c1counts if x != type}
                                    largestnonc1 = max([int(nonc1counts[x]) for x in nonc1counts])
                                    minorallelecount = sum([nonc1counts[x] for x in nonc1counts if nonc1counts[x] != largestnonc1])
                                    if locus not in outputlist:
                                        outputlist.append(locus)
                                    # outstrlist = [clade,locus,str(type),cladenum,tp,fp,fn,tn,sens,spec,fpdetails,fndetails,minorallelecount,nonc1counts,zeros,negs]
                                    outstrlist = [clade,locus,str(type),cladenum,tp,fp,fn,tn,sens,spec,minorallelecount,zeros,negs]
                                    if clade not in outs:
                                        outs[clade] = {locus:[outstrlist]}
                                    else:
                                        if locus not in outs[clade]:
                                            outs[clade][locus] = [outstrlist]
                                        else:
                                            outs[clade][locus].append(outstrlist)

                                if sens < 1 and sens > 0:
                                    largest_for_loci_and_clade = max([c1counts[x] for x in c1counts])
                                    value = [i for i in c1counts if c1counts[i] == largest_for_loci_and_clade]
                                    largest_clade_id = value[0]
                                    sum_of_the_rest = sum([c1counts[x] for x in c1counts if x != largest_clade_id])
                                    if type != largest_clade_id:
                                        if locus not in minorallele:
                                            minorallele[locus] = {type:c1counts[type]}
                                        else:
                                            if type not in minorallele[locus]:
                                                minorallele[locus][type] = c1counts[type]
                                            else:
                                                minorallele[locus][type] += c1counts[type]
        c+=1
        cperc = math.floor((float(c)*100)/tot)
        if cperc not in plist:
            # print(cperc)
            sys.stdout.flush()
            # sys.stdout.write(str(cperc)+"%")
            print(str(cperc)+"%",end = '\r', file = sys.stdout)
            plist.append(cperc)
            
    sys.stdout.write("\nWriting candidate loci\n")
    outpath = args.outprefix + "_sens_{}perc_spec_{}perc.txt".format(int(args.sens_cutoff*100),int(args.spec_cutoff*100))
    outfile = open(outpath,"w")
    outfile.write("Clade\tLocus\tspecific_allele\tNum_in_clade\ttp\tfp\tfn\ttn\tsensitivity\tspecificity\tminor_allele_count\tproblematic_minor_allele_count\tlocuszeros\tlocusnegs\n")

    
    for clade in outs:
        for locus in outs[clade]:
            for outlist in outs[clade][locus]:
                outtype = int(outlist[2])
                if locus in minorallele:
                    minor_split = sum([minorallele[locus][x] for x in minorallele[locus] if x != outtype])
                else:
                    minor_split = 0
                outlist = outlist[:13] + [str(minor_split)] + outlist[13:]
                outlist = list(map(str,outlist))
                outfile.write("\t".join(outlist)+"\n")
                outfile.close()

    sys.stdout.write("\nWriting candidate loci allele profiles\n")

    inap = pd.read_csv(args.allele_profile,sep="\t",na_values=[0],low_memory=False)

    outdf = inap[[args.apidcol]+outputlist]

    outdf.columns = [args.apidcol] + outputlist

    if not args.showneg:
        outdf = outdf.applymap(undst)

    outpath2 = args.outprefix + "_sens_{}perc_spec_{}perc_ap.txt".format(int(args.sens_cutoff * 100),
                                                                     int(args.spec_cutoff * 100))
    outdf.to_csv(outpath2,sep="\t",header=True,index=False)



if __name__ == '__main__':
    main()
