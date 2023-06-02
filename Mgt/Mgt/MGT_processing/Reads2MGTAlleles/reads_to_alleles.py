#!/usr/bin/env python3
from time import sleep as sl

import sys
from os import environ
from Bio import SeqIO
import os
from os.path import commonprefix
import shutil
import argparse
# import psutil
import subprocess
from csv import reader
import multiprocessing
from Bio.Blast.Applications import NcbiblastnCommandline
from Bio.Blast import NCBIXML
from os.path import basename
from os import remove
import re
import itertools
import datetime
from copy import deepcopy
import time
import dis

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

"""
Dependencies:

Python 3
conda install psutil
conda install biopython
conda install Kraken 
(will need to DL minikraken DB)
export KRAKEN_DEFAULT_DB='/srv/scratch/lanlab/kraken_dir/minikraken_20141208'
conda install assembly-stats
conda install blast
conda install mafft
conda install -c bioconda sistr_cmd
conda install -c bioconda mlst

shovill (include 15cov version)

shovill dependencies
    skesa
    megahit (not used)
    velvet (not used)
    spades (not used)
    Lighter
    FLASH
    SAMtools >= 1.3
    BWA MEM
    MASH >= 2.0
    seqtk
    pigz
    Pilon (Java)
    Trimmomatic (Java)
    
conda:
Java
kraken



"""




# TODO return wrong input status (check that it is intact/valid fastq file) to the database (update db to say input incorrect)
# TODO also write back to db for contamination or genome quality

######## MAIN ########


def main(args):
    """
    run two components of reads -> alleleles:
    1 reads -> genome (assembly pipeline)
    2 genome -> alleles

    :param args: command line input arguments in argparse object
    :return: output alleles file with 7gene MLST, allele calls and seq and uncallable loci
    """

    if args.intype == "reads":
        raw_assembly_out, strainid = run_assemblypipe(args)
    else:
        raw_assembly_out=args.input
        if not args.strainid:
            strainid = raw_assembly_out.split("/")[-1]
            args.strainid = re.sub('.(fasta|fna|fa)', '', strainid)

    query_genome, strainid, mgt1st, serotype = post_assembly_qc(args.strainid,raw_assembly_out,args)

    genome_to_alleles(query_genome, args.strainid, args, mgt1st, serotype)




######## ASSEMBLY PIPELINE (incl shovill + skesa) ########

"""
Takes raw reads (fastq or fastq.gz) and runs assembly pipeline:
 runs kraken and checks for match to input species string and that contamination is <10%
 runs shovill (with skesa as assembler) with modified 15 fold coverage minimum regardless of overall coverage
 runs assembly-stats to gather stats to compare to assembly quality limits in inputs
 runs SISTR to verify serovar of genome based on input serotype (salmonella only)
 runs mlst to get 7 gene MLST ST
 
"""


# TODO include read depth estimation (assume all reads map to ref) so need to count reads from input

def run_assemblypipe(args):
    """

    :param fq1:
    :param fq2:
    :return:
    """
    start_time = time.time()

    ## get inputs from args

    script_path = sys.path[0]

    reads = args.input.split(",")
    fq1 = reads[0]
    fq2 = reads[1]

    force = args.force

    ## check if reads are paired and save strain name derived from fastq files

    if len(reads) != 2:
        sys.exit("Two files must be provided one for forward and one for reverse reads (.gz is supported)")

    readpref = commonprefix(reads)

    if readpref == "":
        strain = fq1.split("/")[-1].split(".fastq")[0]
    else:
        strain = str(readpref.split("/")[-1][:-1])

    ## make tmp folder based on strain name - with check for overwrite

    now = datetime.datetime.now()
    timestamp = now.strftime("%H:%M:%S")

    print("[" + timestamp + "] MGT fastq to genome pipeline started for strain: " + strain)

    pref = args.outpath

    basename = pref + strain

    if os.path.exists(basename):
        if force:
            shutil.rmtree(basename)
            os.mkdir(basename)
        else:
            sys.exit("\nStrain with this name already has temp or output files. Use -f/--force flag to overwrite\n")
    else:
        os.mkdir(basename)

    krakenout1 = basename + "/" + strain + "_kraken_out"
    rename_skesa = basename + "/" + strain + "_contigs.fa"
    contam = basename + "/" + strain + "_failure_reason.txt"
    shovil_pref = basename + "/" + strain + "_shovill"
    skesa_assembly = shovil_pref + "/contigs.fa"

    ##### Run kraken #####

    run_kraken(args, fq1, fq2, krakenout1, strain, contam)

    ##### Run shovill #####

    run_shovill(args, fq1, fq2, script_path, shovil_pref, skesa_assembly, rename_skesa)

    elapsed_time = time.time() - start_time

    print("Assembly completed in: ", elapsed_time)

    return rename_skesa, strain


def post_assembly_qc(strain,raw_assembly_out,args):
    start_time = time.time()
    if not os.path.exists(raw_assembly_out):
        sys.exit("genome file is missing at {}".format(raw_assembly_out))

    basename = args.outpath + strain

    if args.intype == "genome":
        if os.path.exists(basename):
            if args.force:
                shutil.rmtree(basename)
                os.mkdir(basename)
            else:
                sys.exit("\nStrain with this name already has temp or output files at {}. Use -f/--force flag to overwrite\n".format(basename))
        else:
            os.mkdir(basename)

    contam = basename + "/" + strain + "_failure_reason.txt"

    assembly_fail = basename + "/" + strain + "_fail_assembly.fa"
    serovar_fail = basename + "/" + strain + "_fail_serovar.fa"
    skesa_pass = basename + "/" + strain + "_pass.fasta"
    sistr_out = basename + "/" + strain + "_sistr.csv"
    assembly_stats = basename + "/" + strain + "_assembly_stats.txt"

    ##### Run assembly-stats/assembly quality filters #####

    run_assembly_stats(raw_assembly_out, contam, assembly_fail, strain, assembly_stats)

    ##### Run SISTR serotyping #####
    serotype = ""
    if args.serotyping:
        serotype = run_sistr(args, raw_assembly_out, strain, sistr_out, contam, serovar_fail)
    else:
        serotype = args.species

    ##### Run 7 gene MLST program #####

    MGT1ST = run_mlst(raw_assembly_out)

    shutil.copy(raw_assembly_out, skesa_pass)  # if no sys.exit by this point then genome has passed filters

    elapsed_time = time.time() - start_time

    print("Assembly QC completed in: ", elapsed_time)

    return skesa_pass, strain, MGT1ST, serotype



def check_kraken(krakenout, target_species):
    """

    :param krakenout: output from kraken_report
    :param target_species: string to match with species line in krakenout
    :return: either Species name = contamination is >10%, False = no contamination (>10%)
    """
    contam = True
    krakenout = krakenout.decode('utf8')
    for line in krakenout.split("\n"):
        col = line.split("\t")
        if len(col) > 5:
            level = col[3]
            ident = col[5].replace(" ", "")
            perc_match = float(col[0].replace(" ", ""))
            if level == "S" and ident == target_species.replace(" ", "") and contam == True:
                contam = False
            elif level == "S" and ident != target_species.replace(" ",
                                                                  "") and perc_match > 10.0:  # scriptvariable - min kraken 10% for contaminany
                contam = col[5].replace("  ", "")
    return contam

def sistr_filter(sistr_out, serovars):
    """
    takes sistr output and checks against specified target serovar
    :param sistr_out: sistr output
    :param serovars: specified serovar to check for
    :return: either sistr_pass=True or False and serovar predicted
    """
    inp = sistr_out

    infile = open(inp, "r").read().splitlines()

    prediction = list(reader(infile))[1][-3]

    sistr_pass = False
    for sero in serovars:
        if prediction.lower() == sero.lower():
            sistr_pass = True
            return sistr_pass, prediction
        else:
            pred = prediction
    return sistr_pass, pred



def assem_filter(inp, args):
    """
    assembly stats filter
    :param inp: assembly stats
    :param args: input arguments argparse object from main()
    :return: True or (False + reasons for failure)
    """
    print(inp)
    inlis = inp.split("\n")

    inf1 = inlis[1].split(",")
    contigs = int(inf1[1].replace("n = ", ""))
    largest_cont = int(inf1[3].replace("largest = ", ""))
    length = int(inf1[0].replace("sum = ", ""))
    n50 = int(inlis[2].split(",")[0].replace("N50 = ", ""))

    contig_no_max = int(args.max_contig_no)
    largest_cont_min = int(args.min_largest_contig)
    length_min = int(args.genome_min)
    length_max = int(args.genome_max)
    n50_min = int(args.n50_min)

    faillis = []

    if contigs >= contig_no_max:
        faillis.append(">{} contigs ({})".format(str(contig_no_max), str(contigs)))
    if largest_cont <= largest_cont_min:
        faillis.append("largest contig < {}kb ({})".format(str(largest_cont_min / 1000), str(largest_cont)))
    if length < length_min or length > length_max:
        faillis.append("Genome outside of allowed range: {:.1f}-{:.1f}Mb ({:.1f})".format(float(length_min) / 1000000,
                                                                                          float(length_max) / 1000000,
                                                                                          float(length) / 1000000))
    if n50 <= n50_min:
        faillis.append("N50 less than {}bp ({})".format(n50_min, n50))

    if len(faillis) == 0:
        return True, faillis
    else:
        return False, faillis



def run_mlst(ingenome):
    ##### Run 7 gene MLST program #####

    mlst_cmd = "mlst {}".format(ingenome)

    proc2 = subprocess.Popen(mlst_cmd, shell=True, stdout=subprocess.PIPE)

    mlst_result = proc2.stdout.read()
    mlst_result = mlst_result.decode('utf8')

    MGT1ST = mlst_result.split("\t")[2]

    return MGT1ST



def run_kraken(args, fq1, fq2, krakenout1, strain, contam):
    ## set KRAKEN_DEFAULT_DB variable to kraken_db input variable
    krakendbcmd = ""
    if args.kraken_db != "":
        #environ["KRAKEN_DEFAULT_DB"] = args.kraken_db
        krakendbcmd=f" --db {args.kraken_db}"
    else:
        test = subprocess.Popen('echo $KRAKEN_DEFAULT_DB', shell=True, stdout=subprocess.PIPE)
        if test.communicate()[0] == b'\n':
            sys.exit(
                "A Kraken database location must either be defined using --kraken_db\n or set as an environmental valiable ( export $KRAKEN_DEFAULT_DB=/path/to/dbfolder )")

    #### Run kraken ####

    if check_zp(fq1):
        kraken_cmd = 'kraken{} --threads {} --fastq-input --gzip-compressed --output {} --paired {} {}'.format(
            krakendbcmd,
            str(args.threads),
            krakenout1,
            fq1, fq2)
    else:
        kraken_cmd = 'kraken{} --threads {} --fastq-input --output {} --paired {} {}'.format(krakendbcmd,str(args.threads),
                                                                                           krakenout1, fq1,
                                                                                           fq2)



    subprocess.Popen(kraken_cmd, shell=True).wait()

    kraken_report_cmd = f'kraken-report{krakendbcmd} {krakenout1}'

    proc = subprocess.Popen(kraken_report_cmd, stdout=subprocess.PIPE, shell=True)

    kraken_result = proc.stdout.read()

    krakenReport = open(krakenout1+"_report.txt","w")

    kraken_out = kraken_result.decode('utf8')

    krakenReport.write(kraken_out)

    krakenReport.close()

    os.remove(krakenout1)

    contamination = check_kraken(kraken_result, args.species)
    # takes kraken_report file and checks for presence of 'species string' and any contaminants above 10% of reads

    if contamination == True:
        outc = open(contam, "w")
        outmessage = "F: {}\tdoes not contain reads from the target species\n".format(strain)
        outc.write(outmessage)
        outc.write(kraken_out)
        outc.close()
        sys.exit(outmessage)
    elif contamination != False:
        outc = open(contam, "w")
        outmessage = "F: {}\tcontaminated with > 10% reads from\t{}\n".format(strain, contamination)
        outc.write(outmessage)
        outc.write(kraken_out)
        outc.close()
        sys.exit(outmessage)



def run_shovill(args, fq1, fq2, script_path, shovil_pref, skesa_assembly, rename_skesa):
    ##TODO work out shovill inclusion / dependencies

    shovill_cmd = script_path + "/shovill_cmd/bin/shovill_15cov -R1 {} -R2 {} --gsize {}M --outdir {} --cpus {} --ram {} --assembler skesa --force".format(
        fq1, fq2, args.refsize, shovil_pref, args.threads, args.memory)

    subprocess.Popen(shovill_cmd, shell=True).wait()

    shutil.copy(skesa_assembly, rename_skesa)



def run_assembly_stats(rename_skesa, contam, assembly_fail, strain, assembly_stats):
    """
    run assembly-stats and pass results to assem_filter() if fails for 1 or more reasons sys.exit with reasons for fail
    """

    assem_cmd = "assembly-stats {}".format(rename_skesa)

    procassem = subprocess.Popen(assem_cmd, shell=True, stdout=subprocess.PIPE)

    assem_result = procassem.stdout.read()
    assem_result = assem_result.decode('utf8')

    assembly_pass, fail_reasons = assem_filter(assem_result, args)

    assem_out = open(assembly_stats,"w")
    assem_out.write(assem_result)
    assem_out.close()

    if not assembly_pass:
        outc = open(contam, "w")
        shutil.copy(rename_skesa, assembly_fail)
        outmessage = "G: {} genome failed the following filters:\n{}\n\n".format(strain, "\n".join(fail_reasons))
        outc.write(outmessage)
        outc.write(assem_result)
        outc.close()
        sys.exit(outmessage)



def run_sistr(args, rename_skesa, strain, sistr_out, contam, serovar_fail):
    """
    run sistr and pass results to sistr_filter if not the correct serovar sys.exit out
    """

    sistr_cmd = "sistr -i {} {} -f csv -o {} -t {}".format(rename_skesa, strain, sistr_out, args.threads)

    subprocess.Popen(sistr_cmd, shell=True).wait()


    serotype_list1 = args.serotype.split(" or ")
    serotype_list = []
    for x in serotype_list1:
        serotype_list+= x.split(";")

    # possible for dynamic db selection later
    # serotype_d = dict(args.serotodb)
    #
    # serotype_list = list(serotype_d.keys())
    #
    # print(serotype_list)

    serovar_pass, prediction = sistr_filter(sistr_out, serotype_list)

    print(serovar_pass,prediction)


    if not serovar_pass:
        outc = open(contam, "w")
        outmessage = "S: {} has been predicted as\t{}\twhich is not currently supported in MGT\n".format(strain,
                                                                                                        prediction)
        outc.write(outmessage)
        outc.close()
        shutil.copy(rename_skesa, serovar_fail)
        sys.exit(outmessage)

    return prediction


######## ASSEMBLY TO ALLELES ########


def genome_to_alleles(query_genome, strain_name, args, mgt1st, serotype):
    """
    Takes assembly from assemblypipe and blasts against set of known alleles for all loci
    exact matches to existing alleles are called from perfect blast hits
    a locus that has no hits in the allele are called as 0

    :param query_genome: assembled genome path
    :param strain_name:
    :param args: args from main()
    :param mgt1st: 7 gene mlst included in allele file as a header

    :return: writes alleles,zero calls,7geneMLST to output file
    """
    start_time = time.time()

    print("Parsing inputs\n")

    ref_alleles_in = args.refalleles


    hsp_ident_thresh = float(args.hspident)  # scriptvariable blast identity to at least one other allele for each locus
    missing_limit = args.locusnlimit  # scriptvariable minimum allowable fraction of locus not lost (i.e. max 20% can be "N")
    wordsize = 18  # scriptvariable blast word size

    ####

    pref = args.outpath

    outdir = pref + strain_name

    outfile = outdir + "/" + strain_name + "_alleles.fasta"

    if args.tmpdir:
        tempdir = args.tmpdir + "/" + strain_name +"/"
    else:
        tempdir = outdir + "/tmp/"
    if os.path.exists(outdir):
        pass
    else:
        os.mkdir(outdir)

    if os.path.exists(tempdir):
        shutil.rmtree(tempdir)
        os.mkdir(tempdir)
    else:
        os.mkdir(tempdir)

    qgenomeseq = SeqIO.parse(query_genome, "fasta")

    qgenome = {x.id: str(x.seq) for x in qgenomeseq}  # query genome as dictionary of {fastq_header:seq}

    locus_allowed_size,seqs = get_allowed_locus_sizes(ref_alleles_in)

    locus_list = [x for x in locus_allowed_size.keys()]

    print("Running BLAST\n")

    # gets ref allele hits and blast hits against reference
    alleles_called_ref, ref_blast_hits, no_hits = ref_exact_blast(query_genome, ref_alleles_in, locus_allowed_size,
                                                                  tempdir,args)

    print(no_hits)
    exacthits = len(alleles_called_ref.keys())
    print("Exact matches found: {}\n".format(exacthits))
    print("Processing partial BLAST hits\n")

    partial_loci = list(locus_list)  # list of all loci

    for i in alleles_called_ref:
        partial_loci.remove(i)  # if locus has exact match to existing remove from list


    # get hsps that match to loci but are not intact for partial_loci list
    # also dict of loci and reasons for uncallable loci in query genome
    partial_hsps, uncallable, tophitlocus = get_partial_match_query_region(ref_blast_hits, partial_loci, qgenome, hsp_ident_thresh,seqs)

    print("Reconstructing fragmented loci\n")

    # Try to rebuild each locus that has partial hsps matching it
    # returns reconstructed loci (with Ns) where possible
    reconstructed, uncallable = generate_query_allele_seqs(partial_hsps, query_genome, missing_limit,
                                                           wordsize, tophitlocus, qgenome, hsp_ident_thresh, uncallable)

    alleles_called_ref,newcalls = check_reconstructed_for_exact_matches(reconstructed,seqs,alleles_called_ref)

    for i in newcalls:
        partial_loci.remove(i)  # if locus has exact match to existing remove from list

    exacthits = len(alleles_called_ref.keys())-exacthits
    print("Reconstructed exact matches found: {}\n".format(exacthits))

    print("Writing outputs\n")
    write_outalleles(outfile, reconstructed, alleles_called_ref, uncallable, locus_list, mgt1st, no_hits, serotype)

    elapsed_time = time.time() - start_time

    print("Allele calling completed in: {:2f}".format(elapsed_time))

    if os.path.exists(tempdir):
        shutil.rmtree(tempdir)

    now = datetime.datetime.now()
    timestamp = now.strftime("%H:%M:%S")


    print("[" + timestamp + "] MGT fastq to alleles pipeline complete for strain: " + strain_name)

def check_reconstructed_for_exact_matches(reconstructed,refseqs,alleles_called_ref):
    newcalls = []
    for locus in reconstructed:
        reconseq = reconstructed[locus]
        if "N" not in reconseq:
            for allele in refseqs[locus]:
                alleleseq = refseqs[locus][allele]
                if alleleseq == reconseq:
                    alleles_called_ref[locus] = allele.split(":")[-1]
                    newcalls.append(locus)
    return alleles_called_ref,newcalls

def ref_exact_blast(query_genome, ref_fasta, allele_sizes, tempdir,args):
    """
    runs blast and extracts exact hits to existing alleles
    data structure of parsed blast results:

    list of results (if multifasta input, one result per fasta seq)

    result attributes: >>>'alignments'<<<, 'application', 'blast_cutoff', 'database', 'database_length', 'database_letters', 'database_name', 'database_sequences', 'date', 'descriptions', 'dropoff_1st_pass', 'effective_database_length', 'effective_hsp_length', 'effective_query_length', 'effective_search_space', 'effective_search_space_used', 'expect', 'filter', 'frameshift', 'gap_penalties', 'gap_trigger', 'gap_x_dropoff', 'gap_x_dropoff_final', 'gapped', 'hsps_gapped', 'hsps_no_gap', 'hsps_prelim_gapped', 'hsps_prelim_gapped_attemped', 'ka_params', 'ka_params_gap', 'matrix', 'multiple_alignment', 'num_good_extends', 'num_hits', 'num_letters_in_database', 'num_seqs_better_e', 'num_sequences', 'num_sequences_in_database', 'posted_date', 'query', 'query_id', 'query_length', 'query_letters', 'reference', 'sc_match', 'sc_mismatch', 'threshold', 'version', 'window_size']
        alignment attributes: 'accession', 'hit_def', 'hit_id', >>>'hsps'<<<, 'length', 'title']
            hsp attributes: 'align_length', 'bits', 'expect', 'frame', 'gaps', 'identities', 'match', 'num_alignments', 'positives', 'query', 'query_end', 'query_start', 'sbjct', 'sbjct_end', 'sbjct_start', 'score', 'strand'

    :param query_genome: query genome fasta path
    :param ref_fasta: path to existing intact alleles file
    :param allele_sizes: dictionary of required allele sizes for each locus
    :param tempdir: directory path that is created to hold blast outputs/tmp files

    :return: dict of loci with exact hits, Bio.Blast.NCBIXML parsed blast results, list of loci with no blast hits in query genome
    """
    no_hits = list(allele_sizes.keys())
    # scriptvariable 15 blast word size
    # scriptvariable 1000000 culling limit
    # scriptvariable 90 blast identity limit

    bident = int(args.blastident)

    blast_hits = run_blast(query_genome, ref_fasta, 15, 1000000, bident, tempdir,args)
    exact_list = []
    exact_dict = {}
    for result in blast_hits:
        contig_hit = result.query.split(" ")[0]
        for alignment in result.alignments:
            allele_hit = alignment.hit_def.split(":")[0]  # get locus name
            if allele_hit in allele_sizes:
                if allele_hit in no_hits:
                    no_hits.remove(allele_hit)  # remove locus from list of no hits
                allele_no = alignment.hit_def.split(":")[1]  # retreive allele number from full allele name
                for hsp in alignment.hsps:
                    if int(hsp.identities) == int(hsp.align_length) and int(hsp.gaps) == 0 and int(hsp.align_length) in allele_sizes[allele_hit]:
                        #  if no gaps, matching bases = length of alignment & length is same as input dictionary add to exact
                        exact_list.append(allele_hit)
                        if allele_hit not in exact_dict:
                            exact_dict[allele_hit] = allele_no  # store exact hit in dict

    return exact_dict, blast_hits, no_hits



def run_blast(query_seq, locus_db, wordsize, culling, pident, tempdir,args):
    """

    :param query_seq: query sequence - can be multiple fasta seqs
    :param locus_db: blastdb path
    :param wordsize: blast word size
    :return: returns list of blast results
    """
    # scriptvariable max hsps 5
    # scriptvariable evalue 0.1

    cpus = multiprocessing.cpu_count()
    gene = basename(locus_db).replace(".fasta", "")
    tmp_out = tempdir + "/tmp_blast.xml"
    cline = NcbiblastnCommandline(
        query=query_seq,
        subject=locus_db,
        evalue=0.1,
        perc_identity=pident,
        # penalty=-5,
        # reward=4,
        # gapextend=5,
        # gapopen=4,
        # ungapped=True,
        out=tmp_out,
        outfmt=5,
        max_target_seqs=10000000,
        max_hsps=5,
        word_size=wordsize,
        num_threads=args.threads,
        task="blastn",
        culling_limit=culling)
    # best_hit_score_edge = 0.01,
    try:
        stdout, stderr = cline()
    except Exception as e:
        print(e)
        sys.exit()

    r_handle = open(tmp_out)

    blast_records = list(NCBIXML.parse(r_handle))

    remove(tmp_out)
    """
    blast_records structure: 
    list of results (if multifasta input, one result per fasta seq) 

    result attributes: >>>'alignments'<<<, 'application', 'blast_cutoff', 'database', 'database_length', 'database_letters', 'database_name', 'database_sequences', 'date', 'descriptions', 'dropoff_1st_pass', 'effective_database_length', 'effective_hsp_length', 'effective_query_length', 'effective_search_space', 'effective_search_space_used', 'expect', 'filter', 'frameshift', 'gap_penalties', 'gap_trigger', 'gap_x_dropoff', 'gap_x_dropoff_final', 'gapped', 'hsps_gapped', 'hsps_no_gap', 'hsps_prelim_gapped', 'hsps_prelim_gapped_attemped', 'ka_params', 'ka_params_gap', 'matrix', 'multiple_alignment', 'num_good_extends', 'num_hits', 'num_letters_in_database', 'num_seqs_better_e', 'num_sequences', 'num_sequences_in_database', 'posted_date', 'query', 'query_id', 'query_length', 'query_letters', 'reference', 'sc_match', 'sc_mismatch', 'threshold', 'version', 'window_size']
        alignment attributes: 'accession', 'hit_def', 'hit_id', >>>'hsps'<<<, 'length', 'title']
            hsp attributes: 'align_length', 'bits', 'expect', 'frame', 'gaps', 'identities', 'match', 'num_alignments', 'positives', 'query', 'query_end', 'query_start', 'sbjct', 'sbjct_end', 'sbjct_start', 'score', 'strand'
    """

    return blast_records



def get_partial_match_query_region(blast_results, partial_matches, qgenome, hsp_ident,seqs):
    """

    :param blast_results:
    :param partial_matches: loci without exact matches
    :param sizes: not used
    :param ref_alleles:
    :param qgenome:
    :param hsp_ident:
    :return:
    """

    '''

    :param blast_results: blast results
    :param partial_matches: loci without exact matches
    :return: partials dictionary {locus:list of tuples} tuple -> (hsp matching reference allele,query contig where match was found)
    Also writes fasta file of these hits for each locus to be used to blast all alleles of the locus
    '''

    partials = {}

    no_call_reason = {}

    #Combine below loop with finding best hit for each loci - store current best combined bitscore alignment in dict
    # and also store those hsps in partials - if higher score is found then replace in partials.

    top_allele_hits = {}

    ## need to store bit scores for all alignments for a given allele
    ## then go through combined scores for all alignments for those alleles
    ## then save HSPs for the best allele across 2 alignments
    ## this is to get best allele even if across 2 contigs in input

    tophitlocus = {}
    testlocus = "XXXXX"
    c=0

    AlignBitscore_dict = {}

    for result in blast_results:
        for alignment in result.alignments:
            alignment_locus = alignment.hit_def.rsplit(":")[0]

            if alignment_locus in partial_matches:# and alignment.hit_def == alignment_locus + ":1":

                currentAlignBitscore = 0
                hspls = []
                for hsp in alignment.hsps:
                    if hsp_filter_ok(hsp, 100, hsp_ident):

                        currentAlignBitscore += hsp.score
                        hspls.append((hsp, result.query, alignment.hit_def))

                if alignment_locus not in AlignBitscore_dict:
                    AlignBitscore_dict[alignment_locus] = {alignment.hit_def: [currentAlignBitscore,hspls]}
                else:
                    if alignment.hit_def not in AlignBitscore_dict[alignment_locus]:
                        AlignBitscore_dict[alignment_locus][alignment.hit_def] = [currentAlignBitscore,hspls]
                    else:
                        AlignBitscore_dict[alignment_locus][alignment.hit_def][0] += currentAlignBitscore
                        AlignBitscore_dict[alignment_locus][alignment.hit_def][1] += hspls


    for locus in AlignBitscore_dict:
        if locus not in top_allele_hits:
            top_allele_hits[locus] = 0

        for allele in AlignBitscore_dict[locus]:
            full_subjct = seqs[locus][allele]
            AlignBitscore = AlignBitscore_dict[locus][allele][0]
            hsps = AlignBitscore_dict[locus][allele][1]
            if AlignBitscore > top_allele_hits[locus]:
                if locus == testlocus:
                    print("new best")
                    print("\n",testlocus)
                    for hsptup in hsps:
                        hsp = hsptup[0]
                        print("len",hsp.align_length)
                        print("ident",hsp.identities)
                        print("gaps",hsp.gaps)
                        print("sbjct",hsp.sbjct)
                        print("query",hsp.query)
                        print("\n")
                        sl(0.1)
                top_allele_hits[locus] = AlignBitscore
                tophitlocus[locus] = full_subjct
                partials[locus] = []
                for hsptup in hsps:
                    if hsp_filter_ok(hsptup[0], 100, hsp_ident):
                        partials[locus].append(hsptup)

    rmlis = []

    partials2 = {}

    # deal with partial overlaps of 2 hsps
    for locus in partial_matches:
        hsplis = []
        c = 1
        ## if 2 or more hsps pass filter but overlap by more that 60% call as 0

        if locus not in tophitlocus:
            rmlis.append(locus)
            no_call_reason[locus] = "no_blast_hits"
            olcheck = "nohit"

        elif len(partials[locus]) > 1:

            olcheck = check_for_multiple_ol_partial_hsps(partials[locus], hsp_ident,locus)
            if locus == testlocus:
                print(olcheck)
                for i in partials[locus]:
                    hsp1 = i[0]
                    print("len", hsp1.align_length)
                    print("ident", hsp1.identities)
                    print("gaps", hsp1.gaps)
                    print("query_start", hsp1.query_start)
                    print("query_end", hsp1.query_end)
                    print("sbjct_start", hsp1.sbjct_start)
                    print("sbjct_end", hsp1.sbjct_end)

            if olcheck == "overlap":
                rmlis.append(locus)
                no_call_reason[locus] = "large_overlap"
            else:
                locuspartials = remove_hsps_entirely_within_others(partials[locus], 0, hsp_ident)
        else:
            locuspartials = partials[locus]
            olcheck = "no overlap"
        if olcheck == "no overlap":
            #TODONE sizechange dict of allele sizes for each locus then use top hit to give size instead of ref_alleles
            locuspartials2 = check_ends_for_snps(locuspartials, tophitlocus[locus], locus, qgenome)
            partials2[locus] = locuspartials

            if len(locuspartials2) == 0:
                rmlis.append(locus)
                no_call_reason[locus] = "possible_duplication"

    npartials = {}
    for locus in partials2:
        if locus not in rmlis:
            npartials[locus] = partials2[locus]

    if testlocus in no_call_reason:
        print("REASON",no_call_reason[testlocus])

    return npartials, no_call_reason,tophitlocus

def mask_high_snp_regions(locus, recon_locus, ref_locus, window_size, snp_limit):
    """
    compare new allele seq to "ref" allele to identify and mask(with Ns) regions with high snp density
    which can be caused by BLAST errors where indels are present in query seq

    :param locus: Not currently used (useful for debug)
    :param recon_locus: sequence to be checked
    :param ref_locus: sequence of 'ref' locus
    :param window_size: size of rolling window to check SNP frequency within
    :param snp_limit: limit of number of SNPs within that window

    :return: input sequence to be checked with regions with elevated SNP counts masked if necessary
    """

    if len(recon_locus) != len(ref_locus): #  comparison with reference will break if lengths not the same
        return recon_locus

    halfwindow = int(window_size / 2)
    mutpos = []
    outlocus = list(str(recon_locus)) #  Convert test sequence into list of letters
    for pos in range(len(recon_locus)):
        if recon_locus[pos] != ref_locus[pos] and recon_locus[pos] not in ["N", "-"] and ref_locus[pos] not in ["N","-"]:
            mutpos.append("X")#  if the same position doesn't match (i.e. a SNP) and that missmatch is not caused by an N or an indel
        else:
            mutpos.append("M")  # If ref and new seq are the same

    #  Get list of ranges allowing for window length over whole locus
    for x in range(halfwindow, len(ref_locus) - halfwindow):
        window = mutpos[x - halfwindow:x + halfwindow]  # get window list of Match(M) or SNP(X)
        if window.count("X") > int(snp_limit):
            # if num of SNPS greater than limit mask all positions in current window
            for pos in range(x - halfwindow, x + halfwindow):
                outlocus[pos] = "N"  # change to N
    outlocus = "".join(outlocus)

    if outlocus.count("N") > (1 - float(0.8)) * len(ref_locus):
        print("Too many Ns",locus)

    return outlocus

def generate_query_allele_seqs(partial_hsps, query_genome, missing_perc_cutoff, wordsize, tophitlocus,
                               qgenome, hsp_thresh, uncallable):
    """

    reconstruct allele sequences from hsps that partially cover the locus

    :param partial_hsps: each locus' partially matching hsps
    :param query_genome: path to query genome file
    :param alleles_sizes: allele sizes dict
    :param missing_perc_cutoff: max amount of locus allowed to be missing as fraction (i.e. 0.8)
    :param wordsize: blast word size
    :param ref_alleles: allele seqs derived from "reference" (all are allele 1)
    :param qgenome: query genome as dict
    :param hsp_thresh: BLAST identity threshold to pass hsp filter
    :param uncallable: dict - loci called 0 with reason as value

    :return: reconstructed alleles in dict and loci where reconstruction failed in uncallable dict
    """
    query_genome = SeqIO.parse(query_genome, "fasta")
    q_genome = {}
    calls = {}

    full_allele = ""

    testlocus = "BPXXXX"

    for s in query_genome:
        q_genome[s.id] = str(s.seq)

    # check that number of identities in blast hits is at least X fraction of normal reference allele length
    # need to check that at least x of allele is covered
    hspcov = 0
    for locus in partial_hsps:
        hspls = partial_hsps[locus]
        reflen = len(tophitlocus[locus])
        refhit = tophitlocus[locus]

        frac_covered = get_combined_hsp_coverage_of_ref_allele(reflen, hspls, hsp_thresh)  # annotation in function

        if frac_covered < float(missing_perc_cutoff):
            uncallable[locus] = "unscorable_too_much_missing"
            hspcov +=1
        hspls = list(remove_hsps_entirely_within_others(hspls, locus, hsp_thresh))
        # removes small hsps within larger ones caused by partial hits to non-orthologous but related genes

        hspls = check_ends_for_snps(hspls, tophitlocus[locus], "", qgenome)  # annotation in function

        hspls2 = []
        if len(hspls) == 0:
            uncallable[locus] = "failed_filter"
        elif len(hspls) > 1:
            contigs = {}
            for tup in hspls:
                hsp = tup[0]
                # scriptvariable hsp min size
                if hsp_filter_ok(hsp, 30, hsp_thresh):
                    hspls2.append(tup)
                    contig = tup[1].split(" ")[0]
                    if contig not in contigs:
                        contigs[contig] = [tup]
                    else:
                        contigs[contig].append(tup)

            # if hits come from > 1 contig
            if len(contigs.keys()) > 1:

                message, full_allele = check_split_over_contigs(hspls2, query_genome, reflen,
                                                                locus)  # annotation in function
                if locus == testlocus:
                    print("MESSAGE",message)
                if message == "inconsistent_overlap":
                    uncallable[locus] = message
                else:
                    calls[locus] = full_allele

            else:

                for c in contigs:  # there will only be one contig
                    fixed_mid = check_mid(c, contigs[c], q_genome, wordsize, reflen, locus,refhit)  # annotation in function

                    if locus == testlocus:
                        print("fixed_mid", fixed_mid)

                    if fixed_mid == "possible_insertion":
                        uncallable[locus] = "possible_insertion"
                    elif fixed_mid == "mixed_orientation":
                        uncallable[locus] = "mixed_orientation"
                    else:
                        calls[locus] = fixed_mid


        else:  # if only one hsp matches

            hsp = hspls[0][0]
            queryid = hspls[0][1].split(" ")[0]
            contig = q_genome[queryid]

            seq = remove_indels_from_hsp(hsp).query

            full_allele, added_start, added_end = check_ends(contig, hsp.query_start, hsp.query_end, hsp.sbjct_start,
                                                             hsp.sbjct_end, reflen, seq,
                                                             locus)  # annotation in function

            calls[locus] = full_allele


    for locus in calls:
        newseq = str(calls[locus])

        calls[locus] = mask_high_snp_regions(locus, newseq, tophitlocus[locus], args.snpwindow,
                                       args.densitylim)

    missingperc = 0
    calls2 = dict(calls)
    for locus in calls:
        reflen = float(len(tophitlocus[locus]))
        if float(len(calls[locus])) > 1.5 * reflen:  # this is not currentlyused but if indels used later will be important
            print("too long",locus, reflen,len(calls[locus]), calls[locus].count("N"))
            uncallable[locus] = "unscorable_too_long"
        elif calls[locus].count("N") > (1 - float(missing_perc_cutoff)) * reflen:
            print("too much missing",locus,reflen,calls[locus].count("N"),(1 - float(missing_perc_cutoff)) * reflen)
            # if too much of locus is missing (replaced/filled in with Ns) call 0
            uncallable[locus] = "unscorable_too_much_missing"
            missingperc +=1

        else:
            calls2[locus] = calls[locus]
    print("missing:",missingperc)

    return calls2, uncallable


######## PER LOCUS ########

def get_combined_hsp_coverage_of_ref_allele(reflen, hspls, hsp_thresh):
    """

    :param reflen: length of intact allele
    :param hspls: list of hsps matching
    :param hsp_thresh: minimum amount of locus below which 0 is called (i.e 0.8 = >80% must be present)
    :return: fraction of intact locus covered by partial hsps
    """
    range_lis = []
    for tup in hspls:
        hsp = tup[0]
        if hsp_filter_ok(hsp, 30, hsp_thresh):
            if hsp.sbjct_start > hsp.sbjct_end:
                range_lis.append((hsp.sbjct_end, hsp.sbjct_start))
            else:
                range_lis.append((hsp.sbjct_start, hsp.sbjct_end))
    mrange_lis = merge_intervals(
        range_lis)  # merge intervals by overlapping regions (i.e. 100-180 + 160-220 -> 100-220)
    tot_covered = 0
    for hit in mrange_lis:
        tot_covered += hit[1] - hit[0]
    fraction_covered = float(tot_covered) / float(reflen)
    return fraction_covered



def merge_intervals(intervals):
    sorted_by_lower_bound = sorted(intervals, key=lambda tup: tup[0])
    merged = []

    for higher in sorted_by_lower_bound:
        if not merged:
            merged.append(higher)
        else:
            lower = merged[-1]

            if int(higher[0]) - 1 <= int(lower[1]):
                upper_bound = max(int(lower[1]), int(higher[1]))
                merged[-1] = (int(lower[0]), upper_bound)  # replace by merged interval
            else:
                merged.append(higher)
    return merged



def hsp_filter_ok(hsp, length, fraction_snps_diff):
    """
    Check whether hsp is long enough (> min length) + is similar enough (fraction snp diff)
    ignores Ns in query or subject
    :param hsp:
    :param length: min length of match
    :param fraction_snps_diff: i.e. 0.9 = max allowed snp fraction is 10%
    :return: Boolean
    """
    ncount = 0
    for pos in range(hsp.align_length - 1):
        if hsp.query[pos] == "N" or hsp.sbjct[pos] == "N":
            ncount += 1
    if hsp.align_length > length:
        if (float(hsp.identities + hsp.gaps + ncount) / hsp.align_length) > float(fraction_snps_diff):
            return True
    return False



def check_ends_for_snps(hsplis, full_subj, locus, qgenome):
    """
    BLAST will not match ends of loci where a SNP is in the final position, therefore need to check with below code
    and insert correct nucleotide (from the query genome) if a SNP is present
    :param hsplis: list of high scoring pairs (hsps) from blast
    :param full_subj: allele subject
    :param locus: not needed except for error reporting
    :param qgenome: query genome

    :return: list of modified hsps with locus ending snps included
    """
    nhspls = []
    for hsp in hsplis:
        contig = hsp[1]
        allele = hsp[2]

        thsp = hsp[0]
        nhsp = hsp[0]

        contig2 = contig.split(" ")[0]
        contigseq = qgenome[contig2]
        subseq = full_subj

        trial = 0
        if thsp.sbjct_start > thsp.sbjct_end:
            if thsp.sbjct_end == 2:
                if thsp.query_end < len(contigseq):
                    q_snp = contigseq[thsp.query_end]
                else:
                    q_snp = "N"  # if only final nucleotide is deleted from allele add N TODO INDEL record this as a del when dels are included for this and next 3 instances
                s_snp = reverse_complement(subseq[0])
                nhsp.align_length = nhsp.align_length + 1
                nhsp.match = nhsp.match + " "
                nhsp.query = nhsp.query + q_snp
                nhsp.sbjct = nhsp.sbjct + s_snp
                nhsp.sbjct_end = nhsp.sbjct_end - 1
                nhsp.query_end = nhsp.query_end + 1
            if thsp.sbjct_start == len(subseq) - 1:
                # trial = 1
                if thsp.query_start - 2 >= 0:
                    q_snp = contigseq[thsp.query_start - 2]
                else:
                    q_snp = "N"
                s_snp = reverse_complement(subseq[-1])
                nhsp.align_length = nhsp.align_length + 1
                nhsp.match = " " + nhsp.match
                nhsp.query = q_snp + nhsp.query
                nhsp.sbjct = s_snp + nhsp.sbjct
                nhsp.sbjct_start = nhsp.sbjct_start + 1
                nhsp.query_start = nhsp.query_start - 1
        else:
            if thsp.sbjct_start == 2:
                if thsp.query_start - 2 >= 0:
                    q_snp = contigseq[thsp.query_start - 2]
                else:
                    q_snp = "N"
                s_snp = subseq[0]
                nhsp.align_length = nhsp.align_length + 1
                nhsp.match = " " + nhsp.match
                nhsp.query = q_snp + nhsp.query
                nhsp.sbjct = s_snp + nhsp.sbjct
                nhsp.sbjct_start = nhsp.sbjct_start - 1
                nhsp.query_start = nhsp.query_start - 1
            if thsp.sbjct_end == len(subseq) - 1:
                try:
                    if thsp.query_end < len(contigseq):
                        q_snp = contigseq[thsp.query_end]
                    else:
                        q_snp = "N"
                    s_snp = subseq[-1]
                    nhsp.align_length = nhsp.align_length + 1
                    nhsp.match = nhsp.match + " "
                    nhsp.query = nhsp.query + q_snp
                    nhsp.sbjct = nhsp.sbjct + s_snp
                    nhsp.sbjct_end = nhsp.sbjct_end + 1
                    nhsp.query_end = nhsp.query_end + 1
                except:
                    print(locus, "query > subject")
        nhspls.append((nhsp, contig, allele))

    '''
    blast hits structure: 
    list of results

    result attributes: >>>'alignments'<<<, 'application', 'blast_cutoff', 'database', 'database_length', 'database_letters', 'database_name', 'database_sequences', 'date', 'descriptions', 'dropoff_1st_pass', 'effective_database_length', 'effective_hsp_length', 'effective_query_length', 'effective_search_space', 'effective_search_space_used', 'expect', 'filter', 'frameshift', 'gap_penalties', 'gap_trigger', 'gap_x_dropoff', 'gap_x_dropoff_final', 'gapped', 'hsps_gapped', 'hsps_no_gap', 'hsps_prelim_gapped', 'hsps_prelim_gapped_attemped', 'ka_params', 'ka_params_gap', 'matrix', 'multiple_alignment', 'num_good_extends', 'num_hits', 'num_letters_in_database', 'num_seqs_better_e', 'num_sequences', 'num_sequences_in_database', 'posted_date', 'query', 'query_id', 'query_length', 'query_letters', 'reference', 'sc_match', 'sc_mismatch', 'threshold', 'version', 'window_size']
        alignment attributes: 'accession', 'hit_def', 'hit_id', >>>'hsps'<<<, 'length', 'title']
            hsp attributes: 'align_length', 'bits', 'expect', 'frame', 'gaps', 'identities', 'match', 'num_alignments', 'positives', 'query', 'query_end', 'query_start', 'sbjct', 'sbjct_end', 'sbjct_start', 'score', 'strand'

    '''
    return nhspls



def check_split_over_contigs(hspls, query_genome, reflen, locus):
    """
    Check if matches are at ends of contigs (or are that last non N part of the contigs)
    if so get any overlap that may have occured

    :param contigs_dict: dict of {contig_name:hsp(s) for that contig}
    :param query_genome:
    :param reflen: required length of locus
    :return: outcome of reconstruction and sequence (if successful, if not then empty string returned)
    """
    testlocus = 'BPXXXX'
    # generate list of hsps as tuples of locus position match (start, end)
    range_lis = []
    range_d = {}
    for tup in hspls:
        hsp = tup[0]

        if hsp.sbjct_start > hsp.sbjct_end:
            sst = hsp.sbjct_end
            send = hsp.sbjct_start
        else:
            sst = hsp.sbjct_start
            send = hsp.sbjct_end
        t = (sst, send)
        range_lis.append(t)
        range_d[t] = tup

    # sort list to be in order of match start position
    sorted_range_list = sorted(range_lis, key=lambda tup: tup[0])
    if locus == testlocus:
        print(sorted_range_list)

    # get first hsp
    hsp1 = range_d[sorted_range_list[0]][0]

    newseq = remove_indels_from_hsp(hsp1).query


    for rang in range(len(sorted_range_list) - 1):
        cur_range_end = sorted_range_list[rang][1]  # position of current hsp end
        next_range_start = sorted_range_list[rang + 1][0]  # position of next hsp start
        cur_hsp = range_d[sorted_range_list[rang]][0]  # current hsp range
        next_hsp = range_d[sorted_range_list[rang + 1]][0]  # next hsp range
        # check for overlap in current and next hsp in list
        if cur_range_end > next_range_start - 1:

            # if there is an overlap of two hsps check that region of overlap is identical, if not call 0
            # if consistent ignore the first part of the next hsp that makes up the overlap and add to new seq
            overlap = cur_range_end - next_range_start + 1

            cur_query = remove_indels_from_hsp(cur_hsp).query

            next_query = remove_indels_from_hsp(next_hsp).query

            olstart = -1 * (overlap)
            end_cur = cur_query[olstart:]

            start_next = next_query[:overlap]

            if locus == testlocus:
                print(end_cur)
                print(start_next)

            if end_cur == start_next:
                add_seq = next_query[overlap:]
                newseq += add_seq

            else:
                add_seq = "N"*overlap + next_query[overlap:]
                newseq = newseq[:olstart] + add_seq
                # return "inconsistent_overlap", ""

            # check overlap for identity

        elif cur_range_end == next_range_start - 1:
            # if the hsps end and start on consecutive positions then just add next hsp to new seq
            add = remove_indels_from_hsp(next_hsp).query
            newseq += add
        elif cur_range_end < next_range_start - 1:
            # if there is a gap add Ns the size of the gap to newseq and then the next hsp
            # add Ns in gap
            missing_no = next_range_start - cur_range_end - 1
            nstring = "N" * missing_no
            newseq += nstring
            add_seq = remove_indels_from_hsp(next_hsp).query
            newseq += add_seq
        else:
            print("\n\nPROBLEM SPLIT CONTIGS\n\n")
    if len(newseq) == reflen:
        return "reconstructed split", newseq
    else:
        # this case caused by BLAST not calling missmatches at end of match
        # use check_ends_split_contigs to correct
        st_hsp = range_d[sorted_range_list[0]]
        en_hsp = range_d[sorted_range_list[-1]]

        full_allele, added_start, added_end = check_ends_split_contigs(st_hsp, en_hsp, reflen, newseq, locus)

        return "reconstructed split w ends", full_allele



def check_mid(contig, hspls, q_genome, wordsize, reflen, locus,refhit):
    """
    where two or more partial hsps match same contig
    sequentially add them together with Ns filling gaps and removing identical ovelaps to create full length allele
    use word length ratio as cutoff for allowing non-N letters in restored gap sequence(i.e. if word length is 12. non-N sequence chunk between 2 hsps can be a max of 18 before possible insertion is called)
    :param contig:
    :param hspls:
    :param q_genome:
    :param wordsize:
    :param reflen:
    :param locus:
    :return:
    """
    test_locus="BPXXXX"
    # check that all hsps that match a locus are oriented the same way on the query genome contig
    orient = check_all_orient(hspls)

    if orient == "mixed":
        # TODO work out what to do with mixed orientation, currently call as 0
        return "mixed_orientation"
    else:

        order = {}
        for tup in hspls:
            hsp = tup[0]
            order[hsp.sbjct_start] = hsp

        sorted_hsps = sorted(map(int, order.keys()))

        full_allele = remove_indels_from_hsp(order[sorted_hsps[0]]).query

        sstart = order[sorted_hsps[0]].sbjct_start
        send = order[sorted_hsps[-1]].sbjct_end
        qstart = order[sorted_hsps[0]].query_start
        qend = order[sorted_hsps[-1]].query_start

        if orient == "positive":
            for start in range(len(sorted_hsps) - 1):

                ## current and next hsps in sorted list
                hsp = order[sorted_hsps[start]]
                hspnext = order[sorted_hsps[start + 1]]

                ## end of one hsp and start of next = mid_section
                mid_section_st = int(hsp.sbjct_end)
                mid_section_en = int(hspnext.sbjct_start)

                if mid_section_en < mid_section_st:
                    if locus == test_locus:
                        print("OVERLAP")

                    # if mid hspA and B overlap then get length to ignore in hspB start
                    olcheck, ollen = check_matching_overlap(hsp, hspnext, "positive")
                    hspnext = remove_indels_from_hsp(hspnext)
                    if olcheck == "nomatch":
                        addr = q_genome[contig][hspnext.query_start + ollen-1:hspnext.query_end]
                        add = hspnext.query[ollen:]
                        full_allele = full_allele[:-1*(ollen)] + "N"*ollen + add
                    else:
                        addr = q_genome[contig][hspnext.query_start + ollen-1:hspnext.query_end]
                        add = hspnext.query[ollen:]
                        full_allele = full_allele + add
                    if locus == test_locus:
                        print("OLCHECK",olcheck)

                else:

                    # if no overlap then add string of N length of gap
                    mid_section_seq = "N" * (hspnext.sbjct_start - hsp.sbjct_end - 1)
                    full_allele += mid_section_seq
                    full_allele += remove_indels_from_hsp(hspnext).query  # hspnext.query
                    nonn_size = largest_nonn_strings(mid_section_seq)

                    # if length of gap is 2 times blast word size then the gap is likely caused by an insertion - call as 0
                    # scriptvariable multiple of word size to call as insertion
                    if nonn_size > (wordsize * 2):
                        return "possible_insertion"

        # below is v similar to above
        elif orient == "negative":
            sstart = order[sorted_hsps[0]].sbjct_end
            send = order[sorted_hsps[-1]].sbjct_start
            qstart = order[sorted_hsps[0]].query_start
            qend = order[sorted_hsps[-1]].query_start

            for start in range(len(sorted_hsps) - 1):
                hsp = order[sorted_hsps[start]]
                hspnext = order[sorted_hsps[start + 1]]
                mid_section_st = int(hsp.sbjct_start)
                mid_section_en = int(hspnext.sbjct_end)

                if mid_section_en < mid_section_st:
                    olcheck, ollen = check_matching_overlap(hsp, hspnext, "negative")
                    hspnext = remove_indels_from_hsp(hspnext)
                    if olcheck == "nomatch":
                        add = hspnext.query[ollen:]
                        full_allele = full_allele[:-1*(ollen)]+ "N"*ollen + add
                    else:
                        add = hspnext.query[ollen:]
                        full_allele = full_allele + add
                else:
                    mid_section_seq = "N" * (hspnext.sbjct_end - hsp.sbjct_start - 1)
                    full_allele = full_allele + mid_section_seq
                    add = remove_indels_from_hsp(hspnext).query
                    full_allele = full_allele + add
                    nonn_size = largest_nonn_strings(mid_section_seq)
                    if nonn_size > (wordsize * 2):
                        return "possible_insertion"

        full_allele, added_start, added_end = check_ends(contig, qstart, qend, sstart, send, reflen, full_allele,
                                                         locus)  # Annotation in function

        if locus == test_locus:
            print("full_fixed",len(full_allele),full_allele)

        return full_allele



def check_all_orient(hsp_list):
    """
    Check orientation of hsps in list relative to subject ( existing alleles)
    and returns oritentation if the same or "mixed" if both orientations are found in same list
    :param hsp_list:
    :return:
    """
    orient = []
    for tup in hsp_list:
        hsp = tup[0]
        if hsp.sbjct_end < hsp.sbjct_start:
            orient.append("negative")
        else:
            orient.append("positive")
    if len(list(set(orient))) > 1:
        return "mixed"
    else:
        return orient[0]



def check_matching_overlap(hsp1, hsp2, orient):
    if orient == "positive":
        ol_len = hsp1.sbjct_end - hsp2.sbjct_start + 1
        if hsp1.query[-1 * ol_len:] != hsp2.query[:ol_len]:
            return "nomatch", ol_len
        else:
            return "match", ol_len
    elif orient == "negative":
        ol_len = hsp1.sbjct_start - hsp2.sbjct_end + 1
        if hsp1.query[:ol_len] != hsp2.query[-1 * ol_len:]:
            return "nomatch", ol_len
        else:
            return "match", ol_len



def remove_indels_from_hsp(hsp):
    """

    :param hsp:
    :return:
    """
    hsp1 = deepcopy(hsp)
    orient = "+"
    unknown_allele = hsp1.query
    ref_allele = hsp1.sbjct
    matches = hsp1.match
    refstart = hsp1.sbjct_start
    refend = hsp1.sbjct_end

    # re-orient matches so positions are always in direction of reference allele
    if int(hsp1.sbjct_start) > int(hsp1.sbjct_end):
        orient = "-"
        unknown_allele = reverse_complement(unknown_allele)
        ref_allele = reverse_complement(ref_allele)
        matches = matches[::-1]
        refstart, refend = refend, refstart

    seq = ""
    intact_nucs = ["A", "T", "G", "C", "a", "t", "c", "g"]
    for i in range(len(unknown_allele)):
        if matches[i] == " ":
            if unknown_allele[i] in intact_nucs and ref_allele[i] in intact_nucs:
                seq += unknown_allele[i]
            elif unknown_allele[i] == "-" and ref_allele[i] in intact_nucs:
                # TODO INDEL REMOVE Below replaces deletion in unknown allele with reference nucleotides to IGNORE DELETIONS
                seq += ref_allele[i]
            elif unknown_allele[i] in intact_nucs and ref_allele[i] == "-":
                continue
                # TODO INDEL REMOVE No addition of unknown allele seq if insertion in new allele
                # seq+=unknown_allele[i]
            elif unknown_allele[i] == "N":
                seq += "N"
        else:
            seq += unknown_allele[i]

    hsp1.query = seq
    return hsp1



def check_ends(contig, qstart, qend, sstart, send, reflen, alleleseq, locus):
    """
    Add Ns to start and/or end
    :param contig: :param alleleseq:
    :param qstart: not used with no del calls
    :param qend: not used with no del calls
    :param sstart: hsp locus position start
    :param send: hsp locus position end
    :param reflen: required length of locus
    :param alleleseq: sequence of allele
    :param locus: not used with no del calls
    :return: reconstructed allele with sequences added, seq added to start, seq added to end
    """

    new_qstart = 0
    new_qend = 0
    added_start = ''
    added_end = ''

    full_allele = ""

    # if hit in reverse orientation have to check opposite end of hit in query genome

    if int(sstart) > int(send):

        # new_qstart = int(qstart) - (reflen - int(sstart))
        # new_qend = int(qend) + int(send) - 1
        added_start = "N" * (int(reflen) - (int(sstart)))
        # TODO Indel: following commented out elifs check for identity of missing region; if not Ns then assumed to be truncated allele - however when ignoring dels we can just add Ns to all of these regions becuase we treat dels and N regions the same
        '''
        # added_st = contig[new_qstart:int(qstart) - 1]
        # if added_st.count("N") == len(added_st):
        #     added_start = reverse_complement(added_st)
        # else:
        #     added_start = "N"*(int(reflen) - int(sstart))
        #     print("len of added start", int(reflen) - int(sstart))
        '''
        added_end = "N" * (int(send) - 1)
        '''
        # added_e = contig[int(qend):new_qend - 1]
        # if added_e.count("N") == len(added_e):
        #     added_end = reverse_complement(added_e)
        # else:
        #     added_end = "N"*(int(send)-1)
        #     print("len of added end",int(send)-1)
        '''
        full_allele = added_end + alleleseq + added_start


    elif int(sstart) < int(send):
        added_start = "N" * (int(sstart) - 1)
        added_end = "N" * (reflen - (int(send)))
        full_allele = added_start + alleleseq + added_end
        '''
        # new_qstart = int(qstart) - int(sstart)
        # new_qend = int(qend) + (reflen - int(send) - 1)
        
        # added_st = contig[new_qstart:int(qstart) - 1]
        # if added_st.count("N") == len(added_st):
        #     added_start = added_st
        # else:
        #     added_start = "N"*int(sstart-1)
        
        # added_e = contig[int(qend):new_qend - 1]
        # if added_e.count("N") == len(added_e):
        #     added_end = added_e
        # else:
        #     added_end = "N"*(reflen - int(send))
        '''

    # if missing flanking region is not all Ns then use original query hit edge - allows for rearrangements/deletions where flanking regions are really gone


    return full_allele, added_start, added_end



def check_ends_split_contigs(hsp_start_tup, hsp_end_tup, reflen, alleleseq, locus):
    """
    functions almost the same as check_ends()
    :param hsp_start_tup:
    :param hsp_end_tup:
    :param reflen:
    :param alleleseq:
    :return:
    """

    start_hsp = hsp_start_tup[0]
    end_hsp = hsp_end_tup[0]

    # start hsp

    if start_hsp.sbjct_start < start_hsp.sbjct_end:
        sstart = start_hsp.sbjct_start
        send = start_hsp.sbjct_end
    else:
        sstart = start_hsp.sbjct_end
        send = start_hsp.sbjct_start

    if int(sstart) > int(send):
        added_start = "N" * (int(send))
        # TODO Indel: following commented out elifs check for identity of missing region; if not Ns then assumed to be truncated allele - however when ignoring dels we can just add Ns to all of these regions becuase we treat dels and N regions the same
        '''
        # new_qstart = int(qstart) - (reflen - int(sstart))
        # added_st = start_contig[new_qstart:int(qstart) - 1]
        # if added_st.count("N") == len(added_st):
        #     added_start = reverse_complement(added_st)
        # else:
        #     added_start = "N"*len(added_st)
        # print(locus, "p3", added_start)
        '''
    else:
        added_start = "N" * (int(sstart) - 1)
        '''
        # new_qstart = int(qstart) - int(sstart)
        # added_st = start_contig[new_qstart:int(qstart) - 1]
        # if added_st.count("N") == len(added_st):
        #     added_start = added_st
        # else:
        #     added_start = "N"*len(added_st)
        # print(locus, "p4", added_start)
        '''

    # end_hsp

    if end_hsp.sbjct_start < end_hsp.sbjct_end:
        sstart2 = end_hsp.sbjct_start
        send2 = end_hsp.sbjct_end
    else:
        sstart2 = end_hsp.sbjct_end
        send2 = end_hsp.sbjct_start


    added_end = ""

    if int(sstart2) < int(send2):
        added_end = "N" * (reflen - (int(send2)))
        '''
        # new_qend = int(qend2) + int(send2) - 1
        # added_e = end_contig[int(qend2):new_qend - 1]
        # if added_e.count("N") == len(added_e):
        #     added_end = reverse_complement(added_e)
        # else:
        #     added_end = "N"*len(added_e)
        '''
    elif int(sstart2) > int(send2):
        added_end = "N" * (reflen - (int(sstart2)))
        '''
        # new_qend = int(qend2) + (reflen - int(send2) - 1)
        # added_e = end_contig[int(qend2):new_qend - 1]
        # if added_e.count("N") == len(added_e):
        #     added_end = added_e
        # else:
        #     added_end = "N"*len(added_e)
        '''

    full_allele = added_start + alleleseq + added_end

    return full_allele, added_start, added_end


def get_allowed_locus_sizes(locusfile):
    sizes = {}
    seqs = {}
    file = SeqIO.parse(locusfile, "fasta")
    for allele in file:
        locus = allele.id.split(":")[0]
        allelelen = len(allele.seq)
        if locus not in sizes:
            sizes[locus] = [allelelen]
            seqs[locus] = {allele.id:allele.seq}
        else:
            seqs[locus][allele.id] = allele.seq
            if allelelen not in sizes[locus]:
                sizes[locus].append(allelelen)
    return sizes,seqs

######## PARTIAL BLAST HIT PROCESSING ########


def remove_hsps_entirely_within_others(hspls, locus, hsp_thresh):
    """

    :param hspls:
    :param reflen:
    :return:
    """
    range_d = {}
    range_d_new = {}

    for tup in hspls:

        hsp = tup[0]
        if hsp_filter_ok(hsp, 30, hsp_thresh):
            sst = 0
            send = 0
            if hsp.sbjct_start > hsp.sbjct_end:
                sst = hsp.sbjct_end
                send = hsp.sbjct_start
            else:
                sst = hsp.sbjct_start
                send = hsp.sbjct_end
            range_d[(sst, send)] = tup

    # if new range is entirely within existing one ignore
    # if new range entirely encompases existing one, remove existing and add new
    # otherwise add range
    remove = []
    for existing_range in range_d:
        for test_range in range_d:
            exst = existing_range[0]
            exend = existing_range[1]
            testst = test_range[0]
            testend = test_range[1]
            if exst <= testst and exend >= testend and existing_range != test_range:
                remove.append(test_range)
    nhspls = []
    for rang in range_d:
        if rang not in remove:
            range_d_new[rang] = range_d[rang]
            nhspls.append(range_d[rang])

    if len(nhspls) > 1:
        # TODONE write section to remove middle hsps like this:[(1, 220), (134, 285), (169, 498)] - i.e. remove (134, 285)
        r2_rangelist = []
        for rang in range_d_new:
            r2_rangelist.append(rang)

        r2_rangelist = sorted(r2_rangelist, key=lambda tup: tup[0])

        overlaps = []
        for r1 in r2_rangelist:
            list1_remove_r1 = [x for x in r2_rangelist if x != r1]
            for r2 in list1_remove_r1:
                if r1[1] > r2[0] and r1[1] < r2[1] and r1[0] < r2[0]:
                    overlaps.append((r1, r2))
        remove = []
        for ol in overlaps:
            for rang in r2_rangelist:
                if rang not in ol:
                    if ol[0][0] < rang[0] and rang[1] < ol[1][1]:
                        remove.append(rang)
        outls = []
        testls = []
        for x in r2_rangelist:
            if x not in remove:
                outls.append(range_d[x])
                testls.append(x)

        return outls
    else:
        return nhspls



def check_for_multiple_ol_partial_hsps(hspls, hsp_thresh,locus):
    """
    check for large overlaps of hsps matching one locus currently cutoff is 60% length of larger hsp
    :param hspls: list of hsps
    :param hsp_thresh: hsp snp limit/ identity minimum (i.e. 0.98)
    :return:
    """
    # scriptvariable - hsp overlap % - cutoff for overlap elimination of partial hsps is currently 0.6 - could change / make variable to adjust
    testlocus = "XXXXXX"
    # get list of hsps with start end and
    ## if 2 or more hsps pass filter but overlap by more that 60% call as 0
    hspls = [x[0] for x in hspls]

    filterpass = []
    for hsp in hspls:
        # if locus == testlocus:
        #     print("olcheck",hsp)
        if hsp_filter_ok(hsp, 100, hsp_thresh):
            filterpass.append(hsp)


    for a, b in itertools.combinations(filterpass, 2):
        if a.align_length >= b.align_length:
            longer = a
            shorter = b
        else:
            longer = b
            shorter = a
        longerst = longer.sbjct_start
        longeren = longer.sbjct_end
        if longer.sbjct_start > longer.sbjct_end:
            longerst = longer.sbjct_end
            longeren = longer.sbjct_start
        shorterst = shorter.sbjct_start
        shorteren = shorter.sbjct_end
        if shorter.sbjct_start > shorter.sbjct_end:
            shorterst = shorter.sbjct_end
            shorteren = shorter.sbjct_start

        if locus == testlocus:
            print("\nlstart",longerst,"lend",longeren)
            print("sstart",shorterst,"send",shorteren,"\n")

        if longerst <= shorterst <= longeren <= shorteren:
            if float(longeren - shorterst) >= float(0.6 * longer.align_length):
                return "overlap"
        elif shorterst <= longerst <= shorteren <= longeren:
            if float(shorteren - longerst) >= float(0.6 * longer.align_length):
                return "overlap"
        elif longerst <= shorterst <= shorteren <= longeren:
            if float(shorter.align_length) >= float(0.6 * longer.align_length):
                return "overlap"
    return "no overlap"


######## UTILS ########


def reverse_complement(dna):
    """

    :param dna:
    :return:
    """
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', "-": "-", "N": "N"}
    return ''.join([complement[base] for base in dna[::-1]])



def largest_nonn_strings(string):
    """

    :param string:
    :return:
    """
    matches = re.findall(r"[ATGC]*", string)
    mx = max([len(x) for x in matches])
    return mx



def check_zp(fq1):
    if ".gz" in fq1:
        return True
    return False


######## IO ########


def get_sizes_dict(inf):
    infile = open(inf, "r").read().splitlines()
    infile = [x.split("\t") for x in infile]
    outd = {x[0]: str((int(x[2]) - int(x[1])) + 1) for x in infile}
    return outd



def write_outalleles(outpath, reconstructed, ref, uncall, locuslist, mgt1st, no_hits, serotype):
    outf = open(outpath, "w")
    outf.write(">{}:{}\n\n".format("species_serotype", serotype))
    outf.write(">{}:{}\n\n".format("7_gene_ST", mgt1st))
    call = 0
    new = {}
    missing = {}
    absent = 0
    for locus in locuslist:
        if locus in ref:
            outf.write(">{}:{}\n\n".format(locus, ref[locus]))
            call+=1
        elif locus in uncall:
            outf.write(">{}:0_{}\n\n".format(locus, uncall[locus]))
            if uncall[locus] not in missing:
                missing[uncall[locus]] = 1
            else:
                missing[uncall[locus]] +=1
        elif locus in reconstructed:

            outf.write(">{}:new\n{}\n".format(locus, reconstructed[locus]))
            if "N" in reconstructed[locus]:
                if "partial" not in new:
                    new["partial"] = 1
                else:
                    new["partial"] += 1
            else:
                if "intact" not in new:
                    new["intact"] = 1
                else:
                    new["intact"] += 1

        elif locus in no_hits:
            outf.write(">{}:0_{}\n\n".format(locus, "no_blast_hits"))
            absent +=1
        else:
            outf.write(">{}:0_{}\n\n".format(locus, "no_result"))
            print("MISSING: ", locus)
            absent+=1
    print("called:",call)
    for i in new:
        print("{}: {}".format(i,new[i]))
    for i in missing:
        print("{}: {}".format(i,missing[i]))
    print("absent:", absent)
    outf.close()


######## ARGUMENTS/HELP ########


if __name__ == "__main__":


    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i","--input",
                        help="If reads: Input paired fastq(.gz) files, comma separated (i.e. name_1.fastq,name_2.fastq )\nIf genome the assembly fasta file",required=True)
    parser.add_argument("--intype",
                        help="select input type from either reads (illumina paired end reads) for genome (assembled genome in fasta format)",
                        required=True,
                        choices=["reads","genome"])
    parser.add_argument("--refalleles", help="File path to MGT reference allele file. By default sistr results will be used to determine which subfolder within the default folder",
                        default="/species_specific_files/")
    parser.add_argument("--strainid", help="id for strain to use in output")
    parser.add_argument("--tmpdir",help="temporary folder")
    parser.add_argument("-o","--outpath", help="Path to ouput file name,required=True",required=True)
    parser.add_argument("-s", "--species", help="String to find in kraken species confirmation test",
                        default="Salmonella enterica")
    parser.add_argument("--serotyping", help="run Serotyping of Salmonella using SISTR (OFF by default)", action='store_true')
    parser.add_argument("-y", "--serotype", help="Serotype to match in SISTR, semicolon separated",
                        default="Typhimurium;I 4,[5],12:i:-")
    parser.add_argument("-t", "--threads", help="number of computing threads",
                        default="4")
    parser.add_argument("-m", "--memory", help="memory available in GB",
                        default="8")
    parser.add_argument("-f", "--force", help="overwrite output files with same strain name?", action='store_true')
    parser.add_argument("--min_largest_contig",
                        help="Assembly quality filter: minimum allowable length of the largest contig in the assembly in bp",
                        default=60000,
                        type=int)
    parser.add_argument("--max_contig_no",
                        help="Assembly quality filter: maximum allowable number of contigs allowed for assembly",
                        default=700,
                        type=int)
    parser.add_argument("--genome_min",
                        help="Assembly quality filter: minimum allowable total assembly length in bp",
                        default=4500000,
                        type=int)
    parser.add_argument("--genome_max",
                        help="Assembly quality filter: maximum allowable total assembly length in bp",
                        default=5500000,
                        type=int)
    parser.add_argument("--n50_min",
                        help="Assembly quality filter: minimum allowable n50 value in bp (default for salmonella)",
                        default=20000,
                        type=int)
    parser.add_argument("--kraken_db",
                        help="path for kraken db (if KRAKEN_DEFAULT_DB variable has already been set then ignore)",
                        default="/srv/scratch/lanlab/mgtdb/kraken/minikraken_20171019_8GB")
    parser.add_argument("--hspident",
                        help="BLAST percentage identity needed for hsp to be returned",
                        default=0.98,type=float)
    parser.add_argument("--locusnlimit",
                        help="minimum proportion of the locus length that must be present (not masked with Ns)",
                        default=0.80,type=float)
    parser.add_argument("--snpwindow",
                        help="Size of sliding window to screen for overly dense SNPs",
                        default=40,
                        type=int)
    parser.add_argument("--densitylim",
                        help="maximum number of SNPs allowed to be present in window before window is masked",
                        default=4,
                        type=int)
    parser.add_argument("--refsize",
                        help="Approx size of genome for shovill input in megabases i.e. 5.0 or 2.9",type=float,
                        default=5.0)
    parser.add_argument("--blastident",
                        help="BLAST percentage identity needed for hsp to be returned",
                        default=90,
                        type=int)

    if len(sys.argv) < 5:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    main(args)