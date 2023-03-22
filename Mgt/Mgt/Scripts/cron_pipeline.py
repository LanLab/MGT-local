from time import sleep as sl
import datetime
import argparse
import psycopg2
import subprocess
import sys
import glob
from os import path
import os
import shutil
import uuid

import importlib.util


# print(sys.path)


from bioentrezMetadataGet import metadl_main

from addIsolates import addInfo
# from bpAntigens_cron import bp_antigen_calling
# from bp_eryth_res import bp_eryth_res



"""
Run in KDM with:
correct conda env (conda activate /srv/www/mgt/VirtualEnvMgt)


check database and retrieve status for all strains 2 lists: 
    ignore: for completed or currently running
    todo: for ids that should be downloaded

run bioentrezMetadataGet.py
    get new STM isolates from previous 2 days
    exclude SRRs already in ignore or todo
    add new ids to start of todo list
    add new ids to database

run a loop over the isolates in the todo database:
    for each try to download using:
     python3 /srv/scratch/lanlab/enaBrowserTools/python3/enaDataGet.py --format fastq -as /srv/scratch/lanlab/enaBrowserTools/aspera_settings.ini SRRNUMBER

Once downloading attempts are completed check for successfully downloaded isolates and change status on db

submit array of freshly downloaded reads to reads_to_alleles.py
    catch and store job id

wait for array to finish (interact with qstat??)
    loop with time delay until qstat doesn't contain job id

check outputs of reads_to_alleles.py and assign status to DB

for isolates with alleles files run loop to add all to db (need to change so that hgt is linked to existing isolate - not sure if already handled
    
set isolate to C in status (if not done in above script)


"""

def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]


def sqlquery_to_outls(con, query):
    """
    Run sql query string with supplied connection and return results as a list of tuples
    :param con: psycopg2 sql connection object
    :param query: sql query string
    :return: sql query results (which are in a list of tuples)
    one tuple for each row returned and each tuple with the selected columns
    """
    cur = con.cursor()  # generate cursor with connection
    cur.execute(query)  # execute the sql query
    res = cur.fetchall()  # get results and save to res as list
    cur.close()  # close cursor
    return res

def getStatusFromDb(args,conn):
    """

    :param args:
    :param conn:
    :return:
    """
    """
    server_status_choices = (
    ('U', 'Uploaded'),
    ('D', 'Downloading'), ********
    ('I', 'InQueue'),
    ('R', 'Running'),
    ('H', 'Holding'),
    ('C', 'Complete'),
    ('F', 'allele file format error'),
    ('V', 'uploaded allele file'),
    ('S', ' running Allele2db'),
    
    assignment_status_choices = (
    ('A', 'Assigned'),
    ('L', 'Alleles called'), ********
    ('F', 'Failed: contamination'),
    ('G', 'Failed: genome quality'),
    ('S', "Failed: serovar incompatibility"),
    ('E', 'Error: other'),

    """


    status = """ SELECT "identifier" FROM "{}_isolate" WHERE ("privacy_status" = 'PU' AND "server_status" IN ('C','R','D','I','H','U','V','S','F')); """.format(args.appname)
    res = sqlquery_to_outls(conn,status)


    ignore = [x[0] for x in res] # isolates that do not need metadata downloaded

    return ignore

def run_metdata_get(args,ignore,conn):

    args.outpath = args.tmpfolder + "/tmp_metadata.txt"

    completedsrr,errlist = metadl_main(ignore,args)

    if len(completedsrr) == 0:
        print("No new isolates to add to {} DB".format(args.appname))
        sys.exit(0)
    else:
        print("{} isolates to be added to DB".format(len(completedsrr)))
        sys.stderr.write("{} isolates to be added to {} DB".format(len(completedsrr),args.appname))
    try:
        addInfo(args.projectPath, args.projectName,args.appname,args.outpath,args.settings)
    except Exception as ex:
        print("Isolate metadata addition failed - possibly due to field being too long?")
        print(ex)

    sql_cmd = """ UPDATE "{0}_isolate" SET "server_status" = 'D' WHERE "identifier" in ('{1}');""".format(
        args.appname, "','".join(completedsrr))

    cur = conn.cursor()  # generate cursor with connection
    cur.execute(sql_cmd)
    cur.close()

    # TODOne make new strains with SRR id as name and add metadata if in completedsrr change status to D
    # set status of errlist to M and just add strain id


def ncbi_dl(ids,args):

    dlpathfile = args.tmpfolder + "/ncbi_readpaths.txt"
    dlpaths = open(dlpathfile, "w")
    for id in ids:
        if len(id) == 9:
            path1 = "/vol1/fastq/" + id[:6] + "/" + id + "/"+ id + "_1.fastq.gz"
            path2 = "/vol1/fastq/" + id[:6] + "/" + id + "/" + id + "_2.fastq.gz"
        elif len(id) == 10:
            path1 = "/vol1/fastq/" + id[:6] + "/00" + id[-1] + "/" + id + "/"+ id + "_1.fastq.gz"
            path2 = "/vol1/fastq/" + id[:6] + "/00" + id[-1] + "/" + id + "/" + id + "_2.fastq.gz"
        elif len(id) == 11:
            path1 = "/vol1/fastq/" + id[:6] + "/0" + id[-2:] + "/" + id + "/"+ id + "_1.fastq.gz"
            path2 = "/vol1/fastq/" + id[:6] + "/0" + id[-2:] + "/" + id + "/" + id + "_2.fastq.gz"
        elif len(id) == 12:
            path1 = "/vol1/fastq/" + id[:6] + "/" + id[-3:] + "/" + id + "/"+ id + "_1.fastq.gz"
            path2 = "/vol1/fastq/" + id[:6] + "/" + id[-3:] + "/" + id + "/" + id + "_2.fastq.gz"
        else:
            print("SRA ID {} not length 9,10,11 or 12:".format(id))
        dlpaths.write(path1 + "\n")
        dlpaths.write(path2 + "\n")
    dlpaths.close()




    key = args.ascpkey
    dlstring = "ascp -k1 -T -l 100m -P33001 -i {} --mode=recv --user=era-fasp --host=fasp.sra.ebi.ac.uk --file-list={} {}".format(key,dlpathfile,args.readsfolder)
    
    print(dlstring)

    res = subprocess.run(dlstring.split(" "), capture_output=True)
    out = res.stdout

    os.remove(dlpathfile)


def download_reads(args,conn):


    # get reads to DL
    reads_query = """ SELECT "id","identifier","project_id" FROM "{}_isolate" WHERE "server_status" = 'D'; """.format(args.appname)
    res = sqlquery_to_outls(conn,reads_query)

    print("attempting to download {} read sets".format(len(res)))

    listsOfRes = list(chunks(res, 10))

    nolists = len(listsOfRes)

    failedDL = []
    successDL = []
    c=0
    for sublist in listsOfRes:
        c+=1
        print("\nDownloading {} isolate set number {} of {}".format(10,c,nolists))

        ids = [x[0] for x in sublist]
        strains = [x[1] for x in sublist]

        id2strain = {x[0]:x[1] for x in sublist}

        # id2idno = {x[1]:x[0] for x in sublist}

        id2proj = {x[0]:x[2] for x in sublist}

        # for id in ids:
        #     dlpaths =
        ncbi_dl(strains,args)


        #check for successful DL

        filenames = glob.glob(args.readsfolder + "/*_1.fastq.gz")
        filenames = [path.basename(x).replace("_1.fastq.gz","") for x in filenames]

        uploadlocation = settings.ABS_MEDIA_ROOT
        # uploadlocation = get_abs_from_rel_and_abs(hard_media_root, args.projectPath) + "/"

        # hard_media_root = settings.MEDIA_ROOT.replace("..","/")
        #
        # if not hard_media_root.startswith("/"):
        #     hard_media_root = "/" + hard_media_root

        for id in ids:
            strain = id2strain[id]
            if strain not in filenames:
                failedDL.append(strain) # ids that fail to download are left as D to try again next time
            else:

                ## move reads to correct folder here: # settingslocation / AppName / userID /  projectID /strainID

                fq1 = "{}/{}_1.fastq.gz".format(args.readsfolder, strain)
                fq2 = "{}/{}_2.fastq.gz".format(args.readsfolder, strain)

                fqbase = "/{}/{}/{}/{}/".format(args.appname,args.dbuser,id2proj[id],id)

                if path.exists(fq1) and path.exists(fq2):

                    if not path.exists(uploadlocation + fqbase):
                        os.makedirs(uploadlocation + fqbase)

                    newf1 = uploadlocation + fqbase + str(id) + "_1.fastq.gz"
                    newf2 = uploadlocation + fqbase + str(id) + "_2.fastq.gz"
                    if not path.exists(newf1):
                        shutil.move(fq1, newf1)
                    else:
                        os.remove(newf1)
                        shutil.move(fq1, newf1)

                    if not path.exists(newf2):
                        shutil.move(fq2, newf2)
                    else:
                        os.remove(newf2)
                        shutil.move(fq2, newf2)

                    f1db = "{}{}_1.fastq.gz".format(fqbase,id)
                    f2db = "{}{}_2.fastq.gz".format(fqbase,id)

                    reads_query = """ UPDATE "{0}_isolate" SET "server_status" = 'U' WHERE "id" = '{1}';
                                      UPDATE "{0}_isolate" SET "file_forward" = '{2}' WHERE "id" = '{1}';
                                      UPDATE "{0}_isolate" SET "file_reverse" = '{3}' WHERE "id" = '{1}';""".format(
                        args.appname, id,f1db,f2db)
                    print("{} ( with id = {} ) read paths added, status set to U".format(strain,id))

                    cur = conn.cursor()  # generate cursor with connection
                    cur.execute(reads_query)
                    cur.close()

                    successDL.append(strain)
                else: # ids that fail to download are left as D to try again next time
                    failedDL.append(strain)

                folder = args.readsfolder + "/" + strain
                if path.exists(folder):
                    shutil.rmtree(folder)

    print("{} isolate reads sets downloaded.\n{} isolate read sets failed to download.".format(len(successDL),len(failedDL)))

def generate_commands_local(scriptpath,refalleles,readsets,assembliesfolder,args,genomeinput):

    serotyping = ""
    if args.species == "Salmonella enterica":
        serotype = "--serotype " + args.serotype.replace(" or ", ";") + " "
        serotyping = " --serotyping"
    else:
        serotyping = ""
        serotype = ""
    command = "source ~/.bash_profile\n"
    command += "source ~/.bashrc\n"
    command += "source ~/.zshrc\n"
    command += "conda activate {r2a_env}\n".format(r2a_env = args.condaenv)
    for id in readsets:
        if genomeinput:
            infiles = readsets[id]
            intype = "genome"
        else:
            f1 = readsets[id][0]
            f2 = readsets[id][1]
            infiles = f1+","+f2
            intype = "reads"

        strainfolder = assembliesfolder + "/" + id #FIXME id seems to be identifier not id...
        if not path.exists(strainfolder):
            os.mkdir(strainfolder)
        command += """python {scriptpath} -i {infiles} --intype {intype} -o {outfolder}"/" -f -m 20 -t 1 --kraken_db {krakendb} --refalleles {refalleles} --species "{species}" {serotype}--min_largest_contig {min_largest_contig} --max_contig_no {max_contig_no} --n50_min {n50_min} --genome_min {genome_min} --genome_max {genome_max} --hspident {hspident} --locusnlimit {locusnlimit} --snpwindow {snpwindow} --densitylim {densitylim} --refsize {refsize} --blastident {blastident}{nosero}\n""".format(
            infiles=infiles,
            intype=intype,
            scriptpath=scriptpath,
            refalleles=refalleles,
            krakendb = args.krakendb,
            species=args.species,
            serotype=serotype,
            min_largest_contig = args.min_largest_contig,
            max_contig_no = args.max_contig_no,
            n50_min = args.n50_min,
            genome_min = args.genome_min,
            genome_max = args.genome_max,
            hspident = args.hspident,
            locusnlimit = args.locusnlimit,
            snpwindow = args.snpwindow,
            densitylim = args.densitylim,
            refsize = args.refsize,
            blastident = args.blastident,
            nosero = serotyping,
            outfolder = assembliesfolder)
    return command

def generate_commands_katana(scriptpath,refalleles,readfolder,assembliesfolder,args,uid,single):

    if args.species == "Salmonella enterica":
        serotype = "--serotype " + args.serotype.replace(" or ", ";") + " "
        serotyping = " --serotyping"
    else:
        serotyping = ""
        serotype= ""

    pbstemplate = """#!/bin/bash
#PBS -N {app}{test}R2A
#PBS -l nodes=1:ppn=1
#PBS -l mem=30gb
#PBS -l walltime=11:59:00


FILES=($FILES)
OUTPUT=${{OUTPUT}}

if [[ -z ${{PBS_ARRAY_INDEX+x}} ]]; then
  f1=${{FILES[0]}};
else
  f1=${{FILES[${{PBS_ARRAY_INDEX}}]}};
fi




if [[ $f1 == *"fastq"* ]]; then
  f2=${{f1%1.fastq.gz}}""2.fastq.gz
elif [[ $f1 == *"fq"* ]]; then
  f2=${{f1%1.fq.gz}}""2.fq.gz
else
  echo "fastq files in _1.fastq.gz or _1.fq.gz format required"
  exit 1  
fi

echo $f1" "$f2" "$OUTPUT


source /srv/scratch/lanlab/michael/miniconda_newkatana/bin/activate read2allele

echo "started at: $(date)"

cores=$PBS_NUM_PPN
mem=16

sleep $((RANDOM % 5))

python {scriptpath} -i $f1,$f2 --intype reads -o $OUTPUT"/" -f -m 20 -t 1 --kraken_db {krakendb} --refalleles {refalleles} --species "{species}" {serotype}--min_largest_contig {min_largest_contig} --max_contig_no {max_contig_no} --n50_min {n50_min} --genome_min {genome_min} --genome_max {genome_max} --hspident {hspident} --locusnlimit {locusnlimit} --snpwindow {snpwindow} --densitylim {densitylim} --refsize {refsize} --blastident {blastident}{nosero}     
    """.format(
        app=str(args.appname)[:3],
        scriptpath=scriptpath,
        refalleles=refalleles,
        krakendb = args.krakendb,
        test=args.testdb,
        species=args.species,
        serotype=serotype,
        min_largest_contig = args.min_largest_contig,
        max_contig_no = args.max_contig_no,
        n50_min = args.n50_min,
        genome_min = args.genome_min,
        genome_max = args.genome_max,
        hspident = args.hspident,
        locusnlimit = args.locusnlimit,
        snpwindow = args.snpwindow,
        densitylim = args.densitylim,
        refsize = args.refsize,
        blastident = args.blastident,
        nosero = serotyping)

    pbsfile = args.tmpfolder+"/"+uid+"_read_to_allele.pbs"

    pbs = open(pbsfile,"w")
    pbs.write(pbstemplate)
    pbs.close()


    if single:
        sshtemplate = """OUTPUT={tmp}

mkdir -p $OUTPUT
mkdir -p $OUTPUT"/oe_files"
cd $OUTPUT"/oe_files"

FP="{fqFolder}/*_1.fastq.gz";FILES=($FP);arrayno=${{#FILES[@]}};let arrayno=$arrayno-1;qsub -v FILES=$FP,OUTPUT=$OUTPUT {pbs}
        """.format(tmp=assembliesfolder, fqFolder=readfolder, pbs=pbsfile)
    else:
        sshtemplate = """OUTPUT={tmp}
    
mkdir -p $OUTPUT
mkdir -p $OUTPUT"/oe_files"
cd $OUTPUT"/oe_files"
    
FP="{fqFolder}/*_1.fastq.gz";FILES=($FP);arrayno=${{#FILES[@]}};let arrayno=$arrayno-1;qsub -v FILES=$FP,OUTPUT=$OUTPUT -J 0-$arrayno {pbs}
        """.format(tmp=assembliesfolder,fqFolder=readfolder,pbs=pbsfile)

    return pbsfile,sshtemplate


def generate_commands_katana_genome(scriptpath, refalleles, readfolder, assembliesfolder, args, uid, single):
    if args.species == "Salmonella enterica":
        serotype = "--serotype " + args.serotype.replace(" or ", ";") + " "
        serotyping = " --serotyping"
    else:
        serotyping = ""
        serotype= ""
    #TODO conda env as a variable
    pbstemplate = """#!/bin/bash
#PBS -N {app}{test}R2A
#PBS -l nodes=1:ppn=1
#PBS -l mem=30gb
#PBS -l walltime=11:59:00


FILES=($FILES)
OUTPUT=${{OUTPUT}}

if [[ -z ${{PBS_ARRAY_INDEX+x}} ]]; then
  genome=${{FILES[0]}};
else
  genome=${{FILES[${{PBS_ARRAY_INDEX}}]}};
fi



echo $genome" "$OUTPUT


source /srv/scratch/lanlab/michael/miniconda_newkatana/bin/activate read2allele

echo "started at: $(date)"

cores=$PBS_NUM_PPN
mem=16

sleep $((RANDOM % 5))

python {scriptpath} -i $genome --intype genome -o $OUTPUT"/" -f -m 20 -t 1 --kraken_db {krakendb} --refalleles {refalleles} --species "{species}" {serotype}--min_largest_contig {min_largest_contig} --max_contig_no {max_contig_no} --n50_min {n50_min} --genome_min {genome_min} --genome_max {genome_max} --hspident {hspident} --locusnlimit {locusnlimit} --snpwindow {snpwindow} --densitylim {densitylim} --refsize {refsize} --blastident {blastident}{nosero}     
    """.format(
        app=str(args.appname)[:3],
        scriptpath=scriptpath,
        refalleles=refalleles,
        krakendb=args.krakendb,
        test=args.testdb,
        species=args.species,
        serotype=serotype,
        min_largest_contig=args.min_largest_contig,
        max_contig_no=args.max_contig_no,
        n50_min=args.n50_min,
        genome_min=args.genome_min,
        genome_max=args.genome_max,
        hspident=args.hspident,
        locusnlimit=args.locusnlimit,
        snpwindow=args.snpwindow,
        densitylim=args.densitylim,
        refsize=args.refsize,
        blastident=args.blastident,
        nosero=serotyping)

    pbsfile = args.tmpfolder + "/" + uid + "_read_to_allele.pbs"

    pbs = open(pbsfile, "w")
    pbs.write(pbstemplate)
    pbs.close()

    if single:
        sshtemplate = """OUTPUT={tmp}

mkdir -p $OUTPUT
mkdir -p $OUTPUT"/oe_files"
cd $OUTPUT"/oe_files"

FP="{tmp}/*.fasta";FILES=($FP);arrayno=${{#FILES[@]}};let arrayno=$arrayno-1;qsub -v FILES=$FP,OUTPUT=$OUTPUT {pbs}
        """.format(tmp=assembliesfolder, pbs=pbsfile)
    else:
        sshtemplate = """OUTPUT={tmp}

mkdir -p $OUTPUT
mkdir -p $OUTPUT"/oe_files"
cd $OUTPUT"/oe_files"

FP="{tmp}/*.fasta";FILES=($FP);arrayno=${{#FILES[@]}};let arrayno=$arrayno-1;qsub -v FILES=$FP,OUTPUT=$OUTPUT -J 0-$arrayno {pbs}
        """.format(tmp=assembliesfolder, pbs=pbsfile)

    return pbsfile, sshtemplate

def make_reads_folder(args,uid):
    reads2run = args.tmpfolder + "/fq_"+uid
    if os.path.exists(reads2run):
        pass
        # shutil.rmtree(reads2run)
        # os.mkdir(reads2run)

    else:
        os.mkdir(reads2run)
    return reads2run

def make_alleles_tmpfolder(args,uid):
    reads2run = args.tmpfolder + "/processing_alleles"+uid
    if os.path.exists(reads2run):
        shutil.rmtree(reads2run)
        os.mkdir(reads2run)

    else:
        os.mkdir(reads2run)
    return reads2run

def make_assemout_folder(args,uid):
    assemout = args.tmpfolder + "/assemout"+uid + "/"
    if os.path.exists(assemout):
        pass
    else:
        os.mkdir(assemout)
    return assemout


def wait_till_finished(jobid):
    sl(30)
    while True:

        proc = subprocess.Popen("qstat -t", shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        out, err = proc.communicate()

        ids = []
        inlist = False
        for line in out.splitlines():
            line = line.decode('utf8')
            status = line.split()[-2]
            if jobid in line and status not in ["X","C"]:
                inlist = True
        # print(ids)
        if not inlist:
            break

        sl(10)

def update_status(newstatus,args,conn,ids,field):

    sqlcmd = """UPDATE "{0}_isolate" SET "{1}" = '{2}' WHERE "id" in ('{3}');""".format(
        args.appname,
        field,
        newstatus,
        "','".join(ids))

    cur = conn.cursor()  # generate cursor with connection
    cur.execute(sqlcmd)
    cur.close()

def update_status_NULL(args,conn,ids,field):

    sqlcmd = """UPDATE "{0}_isolate" SET "{1}" = NULL WHERE "id" in ('{2}');""".format(
        args.appname,
        field,
        "','".join(ids))

    cur = conn.cursor()  # generate cursor with connection
    cur.execute(sqlcmd)
    cur.close()


def check_r2al_outcomes(args,ids,conn,assemOutFolder,readlocs,id2projid,id2user,projid2projname):

    successful_ids = []

    uploadlocation = settings.ABS_MEDIA_ROOT
    # uploadlocation = get_abs_from_rel_and_abs(hard_media_root, args.projectPath) + "/"

    # hard_media_root = settings.MEDIA_ROOT.replace("..", "/")
    # if not uploadlocation.startswith("/"):
    #     uploadlocation = "/" + uploadlocation

    for id in ids:
        print(id)
        strainfolder = assemOutFolder + "/" + id
        if os.path.exists(strainfolder):

            strainProject = id2projid[id]

            # make path for file storage location
            isolatebase = "/{}/{}/{}/{}/".format(args.appname, id2user[id], strainProject,
                                                   id)
            #todo get project id
            #expected file paths to check
            allelesfile = strainfolder + "/" + id + "_alleles.fasta"
            failure = strainfolder + "/" + id + "_failure_reason.txt"
            passgenomefile = strainfolder + "/" + id + "_pass.fasta"
            failgenomefile = glob.glob(strainfolder + "/" + id + "fail*_.fasta")

            if os.path.exists(allelesfile):

                # copy allele and genome to isolatebase folder
                shutil.copyfile(allelesfile, uploadlocation + isolatebase + id + "_alleles.fasta")
                shutil.copyfile(passgenomefile, uploadlocation + isolatebase + id + "_pass.fasta") # keep genome file in same folder as others
                newloc = isolatebase + "/" + id + "_alleles.fasta"

                ## update alleles file location
                update_status(newloc,args,conn,[id],"file_alleles")
                update_status("V", args, conn, [id], "server_status")
                successful_ids.append(id)

                ## remove reads files and switch file forwars and reverse to null
                if projid2projname[strainProject] == "ENA-SRA":
                    os.remove(readlocs[id][0])
                    os.remove(readlocs[id][1])
                    update_status_NULL(args, conn, [id], "file_forward")
                    update_status_NULL(args, conn, [id], "file_reverse")


            elif os.path.exists(failure):
                failreason = open(failure,"r").read()[0]
                if len(failgenomefile) > 0:
                    shutil.copyfile(failgenomefile[0], uploadlocation + isolatebase)
                    shutil.copyfile(failure, uploadlocation + isolatebase)
                update_status(failreason, args, conn, [id], "assignment_status")
                update_status("C", args, conn, [id], "server_status")
                #TODO decide what to do with files for failed filters

            else:
                print("alleles_file_missing at {}".format(allelesfile))
                update_status("E", args, conn, [id], "assignment_status")
                update_status("C", args, conn, [id], "server_status")
                # TODO decide what to do with files with errors in reads/runs
        else:
            print("strain folder missing at {}".format(strainfolder))
            update_status("E",args,conn,[id],"assignment_status")
            update_status("C", args, conn, [id], "server_status")
            # TODO decide what to do with files with errors in reads/runs

    return successful_ids

def run_reads_to_alleles(args,conn):
    """
    Will be run from kdm but can qsub from there

    Run the reads_to_alleles script - using array so need to:
        get list of all reads to use as input - split into multiple folders if more than ~150-200
        work out where they should be output
        somehow monitor progress and read in either alleles file or failure reason

    with list of inputs will need to generate loop which submits 150 at a time
        this could be in default location so can just automatically move reads to 150 batch folders
        then loop over folders running array each time

    :param args:
    :param conn:
    :param script_loc:
    :return:
    """


    if args.local:
        folder = path.dirname(path.dirname(path.abspath(__file__)))
        r2alPath = folder + "/MGT_processing/Reads2MGTAlleles/reads_to_alleles.py"
    else:
        r2alPath = args.katanalocal + "/Mgt/Mgt/MGT_processing/Reads2MGTAlleles/reads_to_alleles.py"


    uploadlocation = settings.ABS_MEDIA_ROOT
    # uploadlocation = get_abs_from_rel_and_abs(hard_media_root, args.projectPath) + "/"

    allelepos = "{alleles}/{appname}/{appname}_intact_alleles.fasta".format(alleles=args.blastalleles,appname=args.appname)

    if not os.path.exists(allelepos):
        sys.exit("allele file for this database ({}) was not where it was expected: {}".format(args.database,allelepos))

    reads_query = """ SELECT "{0}_isolate".id,"{0}_isolate".identifier,"project_id","user_id","{0}_project".identifier,"{0}_isolate".server_status FROM "{0}_isolate" INNER JOIN "{0}_project" ON "{0}_isolate".project_id = "{0}_project".id WHERE "server_status" in ('U','W');""".format(args.appname)

    # split into two lists, genomes (server_status="W") and reads (server_status="U")
    # If any genomes run them first then run read if no genomes
    # print(reads_query)
    res = sqlquery_to_outls(conn,reads_query)
    # print(res)
    if len(res) == 0:
        print("No new read sets or genomes to process")
        return
    genomes = [x for x in res if x[5] == "W"]
    reads = [x for x in res if x[5] == "U"]

    genomeinput = False

    if len(genomes) > 0:
        res = genomes
        genomeinput = True
    elif len(reads) > 0:
        res = reads
    else:
        print("No new read sets or genomes to process")
        return

    ids = [str(x[0]) for x in res]

    if len(ids) == 0:
        print("No new read sets to process")
        return


    # update_status("I", args, conn, ids, "server_status")

    # id2idno = {x[1]: x[0] for x in res}
    id2projid = {str(x[0]): str(x[2]) for x in res}
    id2user = {str(x[0]): str(x[3]) for x in res}
    projid2projname = {str(x[2]): str(x[4]) for x in res}
    if args.local:
        lsofls = chunks(ids, 20000000000)
    else:
        lsofls = chunks(ids,200)

    uid=str(uuid.uuid1())

    assembliesfolder = make_assemout_folder(args,uid)

    for sublist in lsofls:

        update_status("R", args, conn, sublist, "server_status")

        print(sublist)


        if genomeinput:
            input_query = """ SELECT "id","identifier","file_assembly" FROM "{}_isolate" WHERE "id" in ('{}'); """.format(
                args.appname, "','".join(sublist))
        else:
            input_query = """ SELECT "id","identifier","file_forward","file_reverse" FROM "{}_isolate" WHERE "id" in ('{}'); """.format(
                args.appname, "','".join(sublist))

        fileres = sqlquery_to_outls(conn, input_query)

        readlocs = {}
        if args.local:
            readsfolder = make_reads_folder(args, uid)
            for set in fileres:
                id = str(set[0])
                identifier = str(set[1])
                if not genomeinput:
                    if set[2] != None and set[3] != None and set[2] != "" and set[3] != "":
                        f1 = uploadlocation + set[2]
                        f2 = uploadlocation + set[3]
                        r1 = readsfolder + id + "_1.fastq.gz"
                        r2 = readsfolder + id + "_2.fastq.gz"
                        if not path.exists(f1) or not path.exists(f2):
                            print("One or both of forward read ({}) or reverse read ({}) is missing at indicated location".format(f1,f2))
                            continue
                        shutil.move(f1,r1)
                        shutil.move(f2,r2)
                        readlocs[id] = [r1, r2]
                    else:
                        if set[2] in [None,""]:
                            print(id,identifier, "forward read not specified in database - redownload")
                        if set[3] in [None,""]:
                            print(id,identifier, "reverse read not specified in database - redownload")
                else:
                    if set[2] != None and set[2] != "":
                        assem = uploadlocation + set[2]
                        print(set)
                        print(assem)
                        if not path.exists(assem):
                            print("genome file missing for strain {} with id {} at location {}".format(identifier,id,assem))
                            continue

                        assemmod = assembliesfolder + "/" + id + ".fasta"
                        shutil.move(assem,assemmod)
                        readlocs[id] = assemmod
                    else:
                        print(id, identifier, "assembly not specified in database".format())
                        print(set)

        else:
            #NOTE make genome inpput version for katana
            readsfolder = make_reads_folder(args, uid)
            for set in fileres:
                id=str(set[0])
                if not genomeinput:
                    if set[2] != None and set[3] != None and set[2] != "" and set[3] != "":
                        f1=uploadlocation+set[2]
                        f2=uploadlocation+set[3]

                        readlocs[id] = [f1,f2]

                        #TODO modify so copy is not required -> pass list of locations to generate commands file
                        if os.path.exists(f1) and os.path.exists(f2):
                            shutil.copyfile(f1, readsfolder + "/" + id + "_1.fastq.gz")
                            shutil.copyfile(f2, readsfolder + "/" + id + "_2.fastq.gz")
                            print(id, "reads copied")
                        elif os.path.exists(f1) and not os.path.exists(f2):
                            os.remove(f1)
                            update_status_NULL(args, conn, [id], "file_forward")
                            update_status_NULL(args, conn, [id], "file_reverse")
                            update_status_NULL(args, conn, [id], "assignment_status")
                            update_status("D", args, conn, [id], "server_status")
                            print(id, "forward read missing - redownload")
                        elif os.path.exists(f2) and not os.path.exists(f1):
                            os.remove(f2)
                            update_status_NULL(args, conn, [id], "file_forward")
                            update_status_NULL(args, conn, [id], "file_reverse")
                            update_status_NULL(args, conn, [id], "assignment_status")
                            update_status("D", args, conn, [id], "server_status")
                            print(id, "reverse read missing - redownload")
                        else:
                            update_status_NULL(args, conn, [id], "file_forward")
                            update_status_NULL(args, conn, [id], "file_reverse")
                            update_status_NULL(args, conn, [id], "assignment_status")
                            update_status("D", args, conn, [id], "server_status")
                            print(id, "forward and reverse reads missing - redownload")
                    else:
                        update_status_NULL(args, conn, [id], "file_forward")
                        update_status_NULL(args, conn, [id], "file_reverse")
                        update_status_NULL(args, conn, [id], "assignment_status")
                        update_status("D", args, conn, [id], "server_status")
                        print(id, "forward and reverse reads missing - redownload")
                else:
                    if set[2] != None and set[2] != "":
                        assem = uploadlocation + set[2]
                        print(set)
                        print(assem)
                        if not path.exists(assem):
                            print("genome file missing for strain {} with id {} at location {}".format(identifier,id,assem))
                            continue

                        assemmod = assembliesfolder + "/" + id + ".fasta"
                        shutil.move(assem,assemmod)
                        readlocs[id] = assemmod
                    else:
                        print(id, identifier, "assembly not specified in database".format())
                        print(set)

        single = False
        if len(sublist) == 1:
            single = True

        if args.local:
            ##scriptpath,refalleles,readsets,assembliesfolder,args
            sshcmd = generate_commands_local(r2alPath,allelepos,readlocs,assembliesfolder,args,genomeinput)

            res = subprocess.run(sshcmd, shell=True, capture_output=True)
            out = res.stdout
            err = res.stderr

            print(out.decode(), err.decode())

        else:
            if genomeinput:
                pbsfile, sshcmd = generate_commands_katana_genome(r2alPath, allelepos, readsfolder, assembliesfolder, args,
                                                           uid, single)
            else:
                pbsfile,sshcmd = generate_commands_katana(r2alPath,allelepos,readsfolder,assembliesfolder,args,uid,single)


            res = subprocess.run(sshcmd, shell=True,capture_output=True)
            out = res.stdout
            jobid = out.decode('utf8')
            print(jobid)
            jobid = jobid.splitlines()[-1].split(".")[0].split("[")[0]

            print("job submitted with ID: {}".format(jobid))

            wait_till_finished(jobid)

        strainsWithAlleles = check_r2al_outcomes(args,sublist,conn,assembliesfolder,readlocs,id2projid,id2user,projid2projname)

        # print(out,err)
        # if not args.local:
        #     os.remove(pbsfile)
        #     shutil.rmtree(readsfolder)
        # else:
        #     shutil.rmtree(readsfolder)

        print("{} of {} isolates in this sublist were successfully processed for alleles".format(len(strainsWithAlleles),len(sublist)))

    # shutil.rmtree(assembliesfolder)

def wait_for_previous_Allele_to_db(args):
    sl(10)
    while True:

        proc = subprocess.Popen("qstat -t", shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        out, err = proc.communicate()

        ids = []
        inlist = False

        jobname = "{app}{test}A2M".format(app=str(args.appname)[:3],test=args.testdb)

        for line in out.splitlines():

            line = line.decode('utf8')

            status = line.split()[-2]

            if jobname in line and status not in ["X", "C"]:
                inlist = True
                sys.exit("Previous allele_to_db still running")
        # print(ids)
        if not inlist:
            break

        sl(10)

def runAllele2Db(args,conn,alleleslocation):

    """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("inalleles", help="File path to strain alleles file (output from genomes_to_alleles.py)")
    parser.add_argument("database", help="Name of database (i.e. Salmonella)")
    parser.add_argument("-m", "--inmeta", help="File path to strain metadata")
    parser.add_argument("-t", "--metadata_type", help="The source of metadata for conversion (mgt or enterobase or none if no file)",
                        default="enterobase")

    get from settings
    parser.add_argument("--postgresdbname", help="name of postgres database (warning may be different to website db option)",default="salmonella")
    parser.add_argument("--port", help="port for postgres connection",default='5432')
    parser.add_argument("--postgresuser", help="postgres user login",default='postgres')
    parser.add_argument("--postgrespass", help="Password for postgres database",required=True)

    get from args.projectpath and args.projectName
    parser.add_argument("--mgtpath", help="path to mgt project folder", required=True)
    parser.add_argument("--mgtapp", help="folder in mgtpath with mgt in it", required=True)

    get from settings
    parser.add_argument("--mgtalleles", help="folder containing db alleles", required=True)

    leave default
    parser.add_argument("--locusnlimit",
                        help="minimum proportion of the locus length that must be present (not masked with Ns)",
                        default=0.80)
    parser.add_argument("--snpwindow",
                        help="Size of sliding window to screen for overly dense SNPs",
                        default=40)
    parser.add_argument("--densitylim",
                        help="maximum number of SNPs allowed to be present in window before window is masked",
                        default=4)
    parser.add_argument("--apzerolim",
                        help="maximum proportion of loci that can be called zero before the ST (and CC) is called 0",
                        default=0.02)


    parser.add_argument("-p", "--printinfo", help="print random extra info", action='store_true')
    """

    ###have path to MGT/Mgt/Mgt as args.projectPath
    ### count no .. + 1 and remove from projectpath. then joint together
    ### SUBDIR_ALLELES = '../../../../Documents/MGT/general_db_files/alleles/' # replace with full path without leading "/"

    # dircount = alleleslocation.count("..")-1
    # print(dircount)

    # alleleslocation = get_abs_from_rel_and_abs(alleleslocation,args.projectPath) + "/"

    if not os.path.exists(alleleslocation):
        sys.exit("Alleles location provided does not exist: {}".format(alleleslocation))
    # else:
    #     sys.exit("found: {}".format(alleleslocation))

    if not args.local:
        wait_for_previous_Allele_to_db(args)

    uploadlocation = settings.ABS_MEDIA_ROOT
    # uploadlocation = get_abs_from_rel_and_abs(hard_media_root, args.projectPath) + "/"
    #use L assignment status to get strains, allele file @ file_alleles
    # USE -c to skip isolate/metadata add and use -t "none" so no meta file is looked for
    reads_query = """ SELECT "id","file_alleles","project_id","isQuery" FROM "{}_isolate" WHERE "server_status" in ('V'); """.format(args.appname) # NOTE add return of query flag here
    res = sqlquery_to_outls(conn,reads_query)

    print(res)

    submission_subset_res = list([x for x in res if not x[3]])
    query_subset_res = list([x for x in res if x[3]])
    runasquery = True
    if len(submission_subset_res) == 0 and len(query_subset_res) == 0:
        print("no new alleles to process")
        return
    elif len(submission_subset_res) != 0:
        res = submission_subset_res
        runasquery = False
    else:
        res = query_subset_res
        runasquery = True


    ids = list([str(x[0]) for x in res])
    all2id = {x[1]:str(x[0]) for x in res}

    if len(ids) > 100:
        if not args.local:
            ids = ids[:100]

    alleles = list([x[1] for x in res if str(x[0]) in ids])


    id2projid = {str(x[0]): str(x[2]) for x in res if str(x[0]) in ids}
    print(alleles)

    # in webiste upload location is determined by : settingslocation/AppName/userID/#/strainID

    uid=str(uuid.uuid1())

    alleles_tmp = make_alleles_tmpfolder(args,uid)

    #verify allele files exist and no others

    update_status("S", args, conn, ids, "server_status")

    if args.nestedsubsetting:
        nestedcall = " --subsetst "
    else:
        nestedcall = ""

    if runasquery:
        q =  " --query "
    else:
        q = ""


    if args.local:
        conda_activate = os.path.join(os.path.dirname(os.path.dirname(shutil.which('conda'))), 'etc', 'profile.d',
                                      'conda.sh')
        folder = path.dirname(path.dirname(path.abspath(__file__)))
        al2dbpath = folder + "/MGT_processing/MgtAllele2Db/Allele_to_mgt_db.py"
        command = "cd {tmp}\n".format(tmp=args.tmpfolder)
        command = '/bin/bash -c "cd {tmp}\n'.format(tmp=args.tmpfolder)
        command += 'source {}\n'.format(conda_activate)
        # command += "source ~/.bash_profile\n"
        # command += "source ~/.bashrc\n"
        # command += "source ~/.zshrc\n"
        command += "conda activate {conda_env}\n".format(conda_env=args.condaenv)
        for f in alleles:
            ident = all2id[f]
            fullpath = uploadlocation + f
            command += """python {scriptpath} {allelesfile} {appname} -s {settings} --apzerolim {apzero} -c -t none --project {mgtproj} --local --timing --id {ident}{nested}{query}\n""".format(allelesfile=fullpath,
                                                                                                                                                        scriptpath=al2dbpath,
                                                                                                                                                        appname=args.appname,
                                                                                                                                                        tmp=args.tmpfolder,
                                                                                                                                                        mgtproj=args.dbproject,
                                                                                                                                                        settings=args.settings,
                                                                                                                                                        apzero=args.apzero,
                                                                                                                                                        ident=ident,
                                                                                                                                                        nested=nestedcall,
                                                                                                                                                        query=q)
        command += '"'

        subprocess.run(command, shell=True)
        # with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as sp:
        #     for line in sp.stdout:
        #         sys.stdout.write(line.decode())
        #     for line in sp.stderr:
        #         sys.stderr.write(line.decode())



    else:
        for f in alleles:
            ident = all2id[f]
            f = uploadlocation + f
            destname = alleles_tmp + "/" + ident + "_alleles.fasta"
            print("cp {} to {}".format(f,destname))
            shutil.copyfile(f,destname)



        al2dbpath = args.katanalocal + "/Mgt/Mgt/MGT_processing/MgtAllele2Db/Allele_to_mgt_db.py"

        if args.subsetst:
            subset = " --subsetst"
        else:
            subset = ""

        pbstemplate = """#!/bin/bash
#PBS -N {app}{test}A2M
#PBS -l nodes=1:ppn=4
#PBS -l mem=30gb
#PBS -l walltime=11:59:00
#PBS -e {tmp}/error.txt
#PBS -o {tmp}/output.txt
    
    
cd {tmp}
    
source /srv/scratch/lanlab/michael/miniconda_newkatana/bin/activate mgtdbpaper
    
for allelesfile in {allelesfolder}/*.fasta; do python {scriptpath} $allelesfile {appname} -s {settings} --timing --apzerolim {apzero} -c -t none --project {mgtproj} --timing{subset}{nested}{query}; done""".format(allelesfolder=alleles_tmp,
                                                                                                                                                                            scriptpath=al2dbpath,
                                                                                                                                                                            appname=args.appname,
                                                                                                                                                                            tmp=args.tmpfolder,
                                                                                                                                                                            mgtproj=args.dbproject,
                                                                                                                                                                            app=str(args.appname)[:3],
                                                                                                                                                                            settings=args.settings,
                                                                                                                                                                            apzero=args.apzero,
                                                                                                                                                                            test=args.testdb,
                                                                                                                                                                            subset=subset,
                                                                                                                                                                            nested=nestedcall,
                                                                                                                                                                            query=q)

        pbsfile = args.tmpfolder + "/"+uid+"_allele_2_db.pbs"

        pbs = open(pbsfile, "w")
        pbs.write(pbstemplate)
        pbs.close()

        proc = subprocess.Popen("qsub " + pbsfile, shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()

        jobid = out.decode('utf8')
        print(jobid)
        jobid = jobid.splitlines()[-1].split(".")[0].split("[")[0]

        # jobid = out.decode('utf8').splitlines()
        # print(jobid)
        # jobid = jobid[0].split(".")[0].split("[")[0]

        print("job submitted with ID: {}".format(jobid))

        wait_till_finished(jobid)

        shutil.copyfile("{tmp}/error.txt".format(tmp=args.tmpfolder),"{tmp}/error_{uid}.txt".format(tmp=args.tmpfolder,uid=uid))
        shutil.copyfile("{tmp}/output.txt".format(tmp=args.tmpfolder),
                    "{tmp}/output_{uid}.txt".format(tmp=args.tmpfolder,uid=uid))
        shutil.rmtree(alleles_tmp)
        os.remove(pbsfile)

        print("finished processing")

# def runSpeciesSpecific(args,conn,settings):
#     if args.appname == "Pertussis":
#         """
#         run antigen typing
#         if reads: run 23S typing
#         """
#         numrun = bp_antigen_calling(args,conn)
#         print(f'antigen alleles called for {numrun} isolates')
#         success,failed =bp_eryth_res(args,conn,settings)
#         if len(failed) > 0:
#             print(f'{",".join(failed)} isolates kma run failed')
#         print(f'23s mutation (erythromycin res) called for {len(success)} isolates')
#         print("Finished species specific analysis: {}".format(args.appname, datetime.datetime.now()))




def cleanup(args):
    print("cleanup")
    # shutil.rmtree(args.tmpfolder + "/assemout")
    # readsfolders = glob.glob(args.readsfolder+"/*")
    # for folder in readsfolders:
    #     shutil.rmtree(folder)
    print("All Done")

def getProjIdFromName(args,conn):

    reads_query = """ SELECT "id" FROM "{}_project" WHERE "identifier" = '{}'; """.format(args.appname,args.dbproject)
    res = sqlquery_to_outls(conn,reads_query)
    try:
        projid = res[0][0]
    except:
        sys.exit("Are you sure the project {} exists?".format(args.dbproject))
    return projid

def load_settings(args):
    if ".py" in args.settings:
        folder = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
        s = args.settings.split("/")[-1]
        settingsfile = folder + "/Mgt/Mgt/" + s
    else:
        folder = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
        settingsfile = folder + "/Mgt/Mgt/settings_" + args.settings + ".py"

    if not path.exists(settingsfile):
        sys.exit("settings file not found at: {}".format(settingsfile))
    spec = importlib.util.spec_from_file_location("settings", settingsfile)
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)

    return settings

def parseargs():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--appname", help="App name", default="Salmonella")
    parser.add_argument("-s", "--settings", help="path to settings file to use",required=True)
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--days", help="Number of days prior to current to search for isolates in NCBI")
    group.add_argument("--range", help="range of dates in dd-mm-yyyy,dd-mm-yyyy format")
    parser.add_argument("--dbproject",
                        help="MGT database project identifier that strains will have",
                        default="ENA-SRA")
    parser.add_argument("--dbuser",
                        help="MGT user that the strain is added under",
                        default="Lanlab")
    parser.add_argument("--privacy",
                        help="Privacy status of strains to be added",
                        default="Public")
    parser.add_argument("--sra_retrieve", help="run a search for the species that matches the appname",
                        action='store_true')
    parser.add_argument("--dl_reads", help="download read sets with 'D' server status",
                        action='store_true')
    parser.add_argument("--reads_to_alleles", help="run the raw reads to allele pipeline for isolates with server_status in queue (I)",
                        action='store_true')
    parser.add_argument("--allele_to_db", help="run alleles to database pipeline for isolates with assignment_status of Alleles done (L)",
                        action='store_true')
    parser.add_argument("--species_specific",
                        help="run species specific analyses (i.e. antigen typing for pertussis)",
                        action='store_true')
    parser.add_argument("--subsetst",
                        help="include st subsetting in allele to db script PROTOTYPE DO NOT USE",
                        action='store_true')
    parser.add_argument("--nestedsubsetting",
                        help="WARNING THIS WILL ONLY WORK FOR NESTED DESIGNS AND WILL BREAK CC AND ODC CALLS - ONLY USE FOR INCREASED SPEED IN large scheme calling",
                        action='store_true')
    localgroup = parser.add_argument_group("local MGT run options")
    localgroup.add_argument("--local",
                        help="run reads_to_alleles and allele_to_db on the local machine rather that submitting to HPC",
                        action='store_true')
    localgroup.add_argument("-c", "--condaenv", help="name of conda environment used for local mgt run (reqs in X file)")## TODO get yaml for conda env generation modify from r2a one






    args = parser.parse_args()

    args.projectPath = path.dirname(path.dirname(path.abspath(__file__))) + "/"

    args.projectName = "Mgt"

    return args


def main():

    args = parseargs()

    global settings

    settings = load_settings(args)

    alleleslocation = settings.ABS_SUBDIR_ALLELES

    # alleleslocation = settings.SUBDIR_ALLELES.replace("..","/") + "/" + args.appname + "/"
    # if not path.exists(alleleslocation):
    #     if path.exists("/"+alleleslocation):
    #         alleleslocation = "/"+alleleslocation
    database = settings.APPS_DATABASE_MAPPING[args.appname]
    psql_details = settings.DATABASES[database]

    args.database = database

    args.psqldb = psql_details['NAME']

    args.katanahost = str(psql_details['HOST'])

    args.ascpkey =  settings.ASCPKEY

    args.readsfolder = settings.TMPFOLDER + "/" + args.appname + "/fastq_tmp"
    args.tmpfolder = settings.TMPFOLDER + "/" + args.appname + "/tmp"
    args.krakendb = settings.KRAKEN_DEFAULT_DB
    if not args.local:
        args.katanalocal = settings.KATANA_LOCATION
        args.katanasettings = settings.KATANA_SETTINGS
    args.blastalleles = settings.ABS_BLASTALLELES

    args.species = settings.SPECIES_SEROVAR[args.appname]["species"]
    args.serotype = settings.SPECIES_SEROVAR[args.appname]["serovar"]
    args.min_largest_contig = settings.SPECIES_SEROVAR[args.appname]["min_largest_contig"]
    args.max_contig_no = settings.SPECIES_SEROVAR[args.appname]["max_contig_no"]
    args.n50_min = settings.SPECIES_SEROVAR[args.appname]["n50_min"]
    args.genome_min = settings.SPECIES_SEROVAR[args.appname]["genome_min"]
    args.genome_max = settings.SPECIES_SEROVAR[args.appname]["genome_max"]
    args.hspident = settings.SPECIES_SEROVAR[args.appname]["hspident"]
    args.locusnlimit = settings.SPECIES_SEROVAR[args.appname]["locusnlimit"]
    args.snpwindow = settings.SPECIES_SEROVAR[args.appname]["snpwindow"]
    args.densitylim = settings.SPECIES_SEROVAR[args.appname]["densitylim"]
    args.refsize = settings.SPECIES_SEROVAR[args.appname]["refsize"]
    args.blastident = settings.SPECIES_SEROVAR[args.appname]["blastident"]
    args.apzero = settings.SPECIES_SEROVAR[args.appname]["apzero"]



    if settings.TESTDB == "True":
        args.testdb = "test"
    elif settings.TESTDB == "False":
        args.testdb = ""

    DbConString = "dbname='{0}' host='{1}' port='{2}' user='{3}' password='{4}'".format(psql_details['NAME'],psql_details['HOST'],psql_details['PORT'],psql_details['USER'],psql_details['PASSWORD'])  ## connection info for Db - assign new user that can only do what is needed for script
    conn = psycopg2.connect(DbConString)
    conn.autocommit = True




    if args.sra_retrieve:
        print("running sra data search at: {}".format(datetime.datetime.now()))
        ignore = getStatusFromDb(args,conn)

        run_metdata_get(args,ignore,conn)

    if args.dl_reads:
        print("running read download at: {}".format(datetime.datetime.now()))
        download_reads(args,conn)


    if args.reads_to_alleles:
        print("running reads to alleles at: {}".format(datetime.datetime.now()))
        run_reads_to_alleles(args,conn)

    if args.allele_to_db:
        print("running alleles to mgtdb at: {}".format(datetime.datetime.now()))
        runAllele2Db(args,conn,alleleslocation)

    if args.species_specific:
        if args.local:
            sys.exit("--species_specific only on mgtdb central server as it is specific to species located there")
        print("running {} specific analyses at: {}".format(args.appname,datetime.datetime.now()))
        # runSpeciesSpecific(args,conn,settings)

    cleanup(args)
    return

if __name__ == '__main__':
    main()
