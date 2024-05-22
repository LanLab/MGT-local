from time import sleep as sl
import argparse
import glob
import sys
from Bio import SeqIO



def main():
    infolder = sys.argv[1]
    outzeros = infolder + "/zero_neg_reason_locus_stats.txt" # one row per locus, one column per reason plus one column for no of negs, counts of reasons per locus
    strainstats = open(infolder + "/zero_neg_reason_strain_stats.txt","w")# outsummary = infolder + "/neg_zero_summary.txt"


    neg_counts = {}
    allzerocounts = {}
    locus_counts = {}
    locus_neg = {}
    reasonls = ["unscorable_too_much_missing","no_blast_hits","unscorable_too_long","large_overlap","mixed_orientation","failed_filter"]

    strainstats.write("Strain\t0_{}\tAll_zeros\tNegatives\n".format("\t0_".join(reasonls)))

    locus_ls = []
    isolates = 0
    alleles = glob.glob(infolder+"/*/*alleles.fasta")
    for file in alleles:
        reason_counts = {}
        isolates +=1
        if isolates%100 == 0:
            print(isolates)
        inf = SeqIO.parse(file,"fasta")
        strain = file.split("/")[-1].replace("_alleles.fasta","")
        neg_counts[strain] = []
        allzerocounts[strain] = []
        for i in reasonls:
            reason_counts[i] = 0

        for allele in inf:
            no = allele.id.split(":")[-1]
            locus = allele.id.split(":")[0]
            if locus not in locus_ls:
                locus_ls.append(locus)


            if no[0] == "0":
                allzerocounts[strain].append(allele.id)
                reason = no[2:]
                reason_counts[reason] += 1
                if locus not in locus_counts:
                    locus_counts[locus] = {reason:1}
                else:
                    if reason not in locus_counts[locus]:
                        locus_counts[locus][reason] = 1
                    else:
                        locus_counts[locus][reason] += 1
            if "N" in allele.seq or ":0" in allele.id:
                neg_counts[strain].append(allele.id)
            if "N" in allele.seq:
                if locus not in locus_neg:
                    locus_neg[locus] = 1
                else:
                    locus_neg[locus] += 1
        reasons_summary = [str(reason_counts[x]) for x in reasonls]
        strainstats.write("{}\t{}\t{}\t{}\n".format(strain,"\t".join(reasons_summary),str(len(allzerocounts[strain])),str(len(neg_counts[strain]))))

    strainstats.close()

    outf = open(outzeros,"w")
    outf.write(str(isolates)+" strains analysed with results\n")
    outf.write("Locus\t0_"+"\t0_".join(reasonls) + "\tAll_zeros\tNumber_negatives\n")

    # print(reasonls)
    # print(isolates)

    # for reason,counts in reason_counts.items():
    #     print(reason,counts)
    for locus in sorted(locus_ls):
        outf.write(locus)
        allzero = 0
        for c in reasonls:
            if locus in locus_counts:
                if c in locus_counts[locus]:
                    outf.write("\t"+str(locus_counts[locus][c]))
                    allzero += locus_counts[locus][c]
                else:
                    outf.write("\t0")
            else:
                outf.write("\t0")
        outf.write("\t" + str(allzero))
        if locus in locus_neg:
            outf.write("\t"+str(locus_neg[locus]))
        else:
            outf.write("\t0")
        outf.write("\n")
    outf.close()



if __name__ == '__main__':
    main()