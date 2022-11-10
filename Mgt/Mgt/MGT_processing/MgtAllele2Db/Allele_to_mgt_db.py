import psycopg2
from Bio import SeqIO
import sys
import itertools
import operator
from os import path
import argparse
import math
import importlib.util
import re
from operator import itemgetter

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
# print(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
# sys.path.append('../../../')
import time

from time import sleep as sl

from MGT_processing.MgtAllele2Db.UpdateScripts.addAlleles import addAlleles
from MGT_processing.MgtAllele2Db.UpdateScripts.addSnps import addSnpMutsToDb
from MGT_processing.MgtAllele2Db.UpdateScripts.addAllelicProfiles import addApForScheme
from MGT_processing.MgtAllele2Db.UpdateScripts.addClonalComplexes import doAddClonalComplexes
from MGT_processing.MgtAllele2Db.UpdateScripts.addIsolates import addInfo
from MGT_processing.MgtAllele2Db.UpdateScripts.addHgts import addTheHstMatrix
from MGT_processing.MgtAllele2Db.convert_metadata import convert_from_enterobase, convert_from_mgt


"""
STARTING POINT
Have some alleles assigned and allele sequences for unknown/partial

1 - Get complete allele profile by comparing "new" alleles to existing in the db
    for loci that are not already called
    get alleles to compare
    get sequences of alleles of interest
    run functions to assign allele nos
    return full AP

2 - with complete AP compare to existing APs to assign existing ST or assign new

3 - with complete AP also look for APs that differ by 1 allele (for CC) or 2,5,10 (for ODC, only in MGT9)

4 - use CC to subset next scheme (along with previous scheme CC) (loop back to 1 until MGT9)

5 - calculate odc for MGT9

"""


## RETREIVE SCHEME DETAILS ##

def get_table_nos(conn, args):
    """
    retrieve information about allele profile tables for each scheme
    :param conn: sql connection
    :param args: inputs
    :return: allele profile tables in format: {level:{table number: [list of locus names in table]}}
    """
    sqlquery = """ SELECT "scheme_id","table_num" FROM "{}_tables_ap";  """.format(args.appname)

    res = sqlquery_to_outls(conn, sqlquery)
    tables = {}
    levs = []
    for i in res:
        lev = int(i[0].replace("MGT", ""))
        levs.append(int(lev))
        if lev not in tables:
            tables[lev] = {i[1]: []}
        else:
            tables[lev][i[1]] = []

    maxlev = max(levs)
    for lev in tables:
        for no in tables[lev]:

            sqlcommand = "select column_name from INFORMATION_SCHEMA.COLUMNS where table_name = '{}_ap{}_{}';".format(
                args.appname, lev, no)

            cur = conn.cursor()

            cur.execute(sqlcommand)

            res = cur.fetchall()

            cur.close()

            locus_columns = [x[0] for x in res if (x[0] not in ["st","dst","id","main_id","date_created","date_modified"]) and ( not x[0].startswith("cc") and not x[0].endswith("id"))]

            tables[lev][no] = locus_columns

    return tables


def get_max_scheme(connection, args):
    """
    :param connection: sql connection
    :param args: inputs
    :return: highest MGT level in current database
    """
    sqlquery = """ SELECT MAX("display_order") FROM "{}_tables_ap";  """.format(args.appname)

    res = sqlquery_to_outls(connection, sqlquery)

    maxno = int(res[0][0])

    return maxno

def get_min_scheme(connection, args):
    """
    :param connection: sql connection
    :param args: inputs
    :return: highest MGT level in current database
    """
    sqlquery = """ SELECT MIN("display_order") FROM "{}_tables_ap";  """.format(args.appname)

    res = sqlquery_to_outls(connection, sqlquery)

    maxno = int(res[0][0])

    return maxno


## ALLELE PROFILE GENERATION ##


def get_allele_profile(connection, lev, NewPosAlleles, NewNegAlleles, Allloc, PosMatches, ZeroCallAlleles,
                       no_tables, all_assignments, args, nodash_to_dash, start_time, ccb1="", ccb2="", ccsubsetlevs=()):
    """

    :param connection: sql connection
    :param lev: MGT level as integer
    :param NewPosAlleles: dictionary of alleles not matching reads to alleles reference alleles file with no missing data
    :param NewNegAlleles: dictionary of alleles not matching reads to alleles reference alleles file with missing data
    :param Allloc: all parsed results from alleles input file
    :param sizes: required sizes for loci
    :param PosMatches:
    :param ZeroCallAlleles: dict of loci called 0 {locus:reason for 0 call}
    :param no_tables: descriptions of allele profile tables in format: {level:{table number: [list of locus names in table]}}
    :param all_assignments: assignments in {locus:allele assignment} format at this point just pre-existing alleles
    :param args: input argparse arguments
    :param ccmin1: clonal complex number of the previous scheme (i.e. if lev = 5 then the MGT4 CC for current isolates)
    :param ccmin2: clonal complex number of the previous scheme (i.e. if lev = 5 then the MGT3 CC for current isolates)
    :return:
    profile assignments of alleles from input
    all_assignments dict of all assignments for loci in level
    matching_st_ids STs found in ccmin1 and ccmin2 subsets
    new_allele_outdict details about any new alleles including SNPs etc
    """

    pqsl_query = """SELECT locus_id from "{}_scheme_loci" WHERE "scheme_id" = 'MGT{}';""".format(args.appname, lev)

    loci_list = sqlquery_to_outls(connection, pqsl_query)
    loci_list = [x[0] for x in loci_list]
    profile = {}
    new_allele_outdict = {}

    to_process = []
    ## get list of loci that are in newpos (novel positive alleles) or negative and therefore need further analysis

    for locus in loci_list:

        if locus in all_assignments:
            profile[locus] = all_assignments[locus]
        elif Allloc[locus] == "newpos" or Allloc[locus] == "neg":
            to_process.append(locus)
        elif locus in ZeroCallAlleles:
            profile[locus] = "0"
        elif locus in PosMatches:
            profile[locus] = PosMatches[locus]


    # ## if no alleles need further analysis then can return profile already
    # if to_process == []:
    #     matching_st_ids = []
    #     pass
    #     # print(profile)
    #
    # ##otherwise need to process remaining loci
    # else:
    #
    #     # returns dict with alleles that need to be examined after number is reduced by subsetting
    #     # structure alleles = {locus:{allelenumber:alleleseq}}
    #
    #     if ccsubsetlevs == ():
    #         #  for first 2 levels get all alleles
    #         alleles, all_alleles_lists, all_pos_alleles_lists, matching_st_ids = retrieve_alleles_to_compare(connection,
    #                                                                                                          lev,
    #                                                                                                          Allloc,
    #                                                                                                          loci_list,
    #                                                                                                          to_process,
    #                                                                                                          no_tables,
    #                                                                                                          args,
    #                                                                                                          nodash_to_dash)
    #     else:
    #         #  for all levels past MGT3 get alleles subset by cc
    #         alleles, all_alleles_lists, all_pos_alleles_lists, matching_st_ids = retrieve_alleles_to_compare(connection,
    #                                                                                                          lev,
    #                                                                                                          Allloc,
    #                                                                                                          loci_list,
    #                                                                                                          to_process,
    #                                                                                                          no_tables,
    #                                                                                                          args,
    #                                                                                                          nodash_to_dash,
    #                                                                                                          ccb1=ccb1,
    #                                                                                                          ccb2=ccb2,
    #                                                                                                          ccsubsetlevs=ccsubsetlevs)


    if args.timing:
        print("{} retrieve subset alleles/sts".format(lev), (" --- %s seconds ---" % (time.time() - start_time)))

    #  match any unmatched alleles to current db
    #  this will be needed for loci where positive allele wasn't in ref allele fasta in reads->alleles OR
    #  where the allele is negative
    #  OTHERWISE if no match assign new (st or dst)
    profile, new_allele_outdict = match_or_assign_alleles(lev, NewPosAlleles, NewNegAlleles,profile, loci_list,no_tables, connection, args)

    if args.timing:
        print("{} match and assign alleles".format(lev), (" --- %s seconds ---" % (time.time() - start_time)))

    # for locus in new_allele_outdict:
    #     if new_allele_outdict[locus] == "1":
    #         print(locus,new_allele_outdict[locus])
    #         sl(10)
    #  add loci profile if not already assigned in all_assignments
    # print(profile)
    if profile != "newst":
        for locus in profile:
            if locus not in all_assignments:
                all_assignments[locus] = profile[locus]

    if args.query and profile == "newst":
        return profile, "", "", ""

    if len(profile.keys()) != len(loci_list):  # Catch cases where a locus is missing from allelic profile
        print(profile)
        missing = []
        for i in loci_list:
            if i not in profile.keys():
                missing.append(i)
        sys.exit("some loci are missing from profile: {}".format(",".join(missing)))

    else:
        return profile, all_assignments, new_allele_outdict


def retrieve_alleles_to_compare(connection, lev, Allloc, loci_list, to_process, table_nos, args, nodash_to_dash,
                                ccb1="", ccb2="", ccsubsetlevs=()):
    """
    Get alleles and their sequences after getting subset using higher level CC
    :param connection: sql conn
    :param lev: MGT level
    :param Allloc: dictionary of allele outcomes parsed from allele file
    :param loci_list: list of loci for the current level
    :param to_process: loci that are still uncertain/unassigned
    :param table_nos: descriptions of allele profile tables in format: {level:{table number: [list of locus names in table]}}
    :param args: inpur args
    :param ccminus1: CC of previous MGT scheme (i.e. if level = 7 this this is the current strains mgt6 CC)
    :param ccminus2: CC of 2previous MGT scheme (i.e. if level = 7 this this is the current strains mgt5 CC)
    :return: allele ids,sequences and sts in CC subset + list of all alleles + list of all positive allele
    """
    subset = True
    if ccsubsetlevs == ():
        subset = False
    ## get all alleles for locus

    ## add new_pos_allele to to_process_w_pos (only in this function)

    allelesseqs = {}

    all_alleles_lists = None
    all_pos_alleles_lists = []
    matching_st_ids = []

    ##TODONE write allele subset query and function to return dict of {locus:list of alleles - list of pos alleles so that when matching later can get all alleles (pos or neg)}
    all_alleles_lists, all_pos_alleles_lists, matching_st_ids = get_locus_allele_freqs_in_higher_cc(lev, ccb1,
                                                                                                    ccb2,
                                                                                                    to_process,
                                                                                                    loci_list,
                                                                                                    table_nos,
                                                                                                    connection, args,
                                                                                                    nodash_to_dash,
                                                                                                    ccsubsetlevs=ccsubsetlevs)

    # print(all_pos_alleles_lists)

    # if not all_alleles_lists or all_pos_alleles_lists == []:
    #     subset = False
    #
    # if not args.subsetwcc:
    #     subset = False

    #  Below sql query retrieves allele fasta file locations for loci in "to process" list

    sqlcommand = """SELECT locus_id,file_location FROM "{}_allele" WHERE "identifier" = '1' AND "locus_id" in ('{}');""".format(
        args.appname, "','".join(to_process))

    files = sqlquery_to_outls(connection, sqlcommand)
    files = {x[0]: "/"+x[1] for x in files}  # {locus name: fasta file path}

    if len(list(files.keys())) != len(to_process):
        sys.exit("allele files not being retrieved correctly")

    # print("SUBSET",subset)

    for locus in files:
        if ":" in files[locus]:
            file = files[locus].split(":")[0] + ".fasta"
        else:
            file = files[locus]
        # print(file)
        if not path.exists(file):
            sys.exit("{} allele file does not exist at {}".format(locus,file))

        alleles = SeqIO.parse(file, "fasta")
        allelesseqs[locus] = {}
        # TODO BELOW COMMENT RESTRICTS ALLELE SEQS TO SEARCH SHOULD BE USED FOR SPEEDUPS - CURRENTLY NOT WORKING CORRECTLY EXCLUDES REAL HITS also causes positive hits to be missed
        subset = False  # this subset is artificially removing matching alleles - probably delete
        if subset:
            for allele in alleles:
                allelenumber = allele.id.split(":")[-1]
                # if "-" in allelenumber:
                #     pos = allelenumber.split("_")[0][1:]
                # else:
                #     pos = str(allelenumber)
                # # print(pos)
                # if pos in all_pos_alleles_lists[locus] or allelenumber == "1":
                #     allelesseqs[locus][allelenumber] = str(allele.seq)
        else:
            for allele in alleles:
                allelenumber = allele.id.split(":")[-1]
                allelesseqs[locus][allelenumber] = str(allele.seq)

    return allelesseqs, all_alleles_lists, all_pos_alleles_lists, matching_st_ids


def get_locus_allele_freqs_in_higher_cc(lev, ccb1, ccb2, to_process, locuslist, table_nos, connection, args,
                                        nodash_to_dash, ccsubsetlevs=()):
    """
    THIS FUNCTION MOSTLY NOT NEEDED BUT KEPT IN CASE SUBSETTING IS EVER NEEDED IN FUTURE
    given a locus and higher CCs (-1 and -2 from current)
    get the list of positive alleles already called in the 0 level
    :param lev: current level
    :param ccminus1: CC of previous MGT scheme (i.e. if level = 7 this this is the current strains mgt6 CC)
    :param ccminus2: CC of 2previous MGT scheme (i.e. if level = 7 this this is the current strains mgt5 CC)
    :param locuslist: loci in current level left to process
    :param table_nos: descriptions of allele profile tables in format: {level:{table number: [list of locus names in table]}}
    :param connection: sql connection
    :param args: input args
    :return:all_alleles = dictionary of each locus with list of matching alleles as key,
     pos_alleles = like all_alleles but only listing positive alleles (including positive versions where only neg where assigned)
     matching_st_ids = list of STs found after CC restriction
    """
    ##for cc at level 4 need to get all cases where 4 is id and merge id, possible also need to get cases where results of previous also return corresponding merge_ids and ids
    start_time1 = time.time()
    if ccsubsetlevs == ():
        outp = ""
        if args.timing:
            print("\tNo {} cc subsetting".format(lev), (" --- %s seconds ---" % (time.time() - start_time1)))
    elif args.subsetwccs:
        prevlevst = ccb1[0]
        prevlevdst = ccb1[1]
        outp = """ WHERE ("ap0_{0}_st" = {1})""".format(lev - 1, prevlevst)
    else:
        ccb1lev = ccsubsetlevs[0]
        ccb2lev = ccsubsetlevs[1]
        if ccb1 in (None, "", "None", "0", 0) and ccb2 in (None, "", "None", "0", 0):
            return None, None, []
        elif ccb1 in (None, "", "None", "0", 0):
            cclisb2 = rec_get_merge_cclis([str(ccb2)], 1, lev - ccb2lev, connection, args)
            outp = """ WHERE ("cc1_{0}" IN ('{1}'))""".format(lev - ccb2lev, cclisb2)
        elif ccb2 in (None, "", "None", "0", 0):
            cclisb1 = rec_get_merge_cclis([str(ccb1)], 1, lev - ccb1lev, connection, args)
            outp = """ WHERE ("cc1_{0}" IN ('{1}'))""".format(lev - ccb1lev, cclisb1)
        else:
            cclisb1 = rec_get_merge_cclis([str(ccb1)], 1, lev - ccb1lev, connection, args)
            cclisb2 = rec_get_merge_cclis([str(ccb2)], 1, lev - ccb2lev, connection, args)
            outp = """ WHERE ("cc1_{0}" IN ('{1}') OR "cc1_{2}" IN ('{3}'))""".format(lev - ccb1lev, cclisb1,
                                                                                      lev - ccb2lev, cclisb2)

        if args.timing:
            print("\t{} cc subsetting".format(lev), (" --- %s seconds ---" % (time.time() - start_time1)))
    combined_res = {}
    combined_locils = []
    stidlis = []
    for num in table_nos[lev]:  # For each table that makes up the combined allele profile for a particular level

        cur = connection.cursor()

        tablesloci = table_nos[lev][num]  # get loci for that table
        restricted_tablesloci = [x for x in tablesloci if
                                 nodash_to_dash[x] in to_process]  ## only need ot get loci that are not assigned already

        if len(restricted_tablesloci) == 0:
            continue

        combined_locils += restricted_tablesloci

        if num == 0:
            ident = "id"
        else:
            ident = "main_id"

        locuslist_string = '"' + ident + '","' + '","'.join(restricted_tablesloci) + '"'

        """
        below sql query:
        gets values for loci in an allele profile table 'num' for a given MGT 'lev'
        where the allele profile id ('ident') is in a list defined by:
        whether the allele profile id is in the same view_apcc row as a clonal complex which matches either cc-1 or cc-2 lists
        as defined at start of the function
        (sorry^)
        """
        if args.timing:
            print("\t{} table {} pre sql".format(lev,num), (" --- %s seconds ---" % (time.time() - start_time1)))
        sqlcomm = """SELECT {0} FROM "{1}_ap{2}_{3}";""".format(
            locuslist_string, args.appname, lev, num)

        cur.execute(sqlcomm)

        res = cur.fetchall()
        if args.timing:
            print("\t{} table {} post sql".format(lev,num), (" --- %s seconds ---" % (time.time() - start_time1)))
        for result in res:
            id = result[0]
            if id not in stidlis:
                stidlis.append(id)
            if id not in combined_res:
                combined_res[id] = result[1:]
            else:
                combined_res[id] += result[1:]

        cur.close()

    if args.timing:
        print("\t{} retrieve sts/alleles".format(lev), (" --- %s seconds ---" % (time.time() - start_time1)))
    all_alleles = {x: [] for x in locuslist}
    pos_alleles = {x: [] for x in locuslist}

    matching_st_ids = []



    for id in combined_res:
        # matching_st_ids.append(id)
        for pos in range(len(combined_locils)):
            loc = combined_locils[pos]
            loc = nodash_to_dash[loc]
            allele = combined_res[id][pos]  # get allele from sql output dict
            posallele = neg_to_pos(allele)  # convert allele to positive
            all_alleles[loc].append(allele)  # store original allele from sql out
            pos_alleles[loc].append(posallele)  # store positive version of original allele

    # matching_st_ids = list(set(matching_st_ids))
    # print("Level and matching sts",lev,len(matching_st_ids))

    if args.timing:
        print("\t{} higher cc retrieve done".format(lev), (" --- %s seconds ---" % (time.time() - start_time1)))

    return all_alleles, pos_alleles, matching_st_ids

def get_allele_seqs(args,conn,NewPosAlleles,NewNegAlleles,lev,table_nos):
    loci_to_get = list(NewPosAlleles.keys()) + list(NewNegAlleles.keys())
    combined_locils = []
    loci_alleles = {}

    sqlcommand = """SELECT locus_id,file_location FROM "{}_allele" WHERE "identifier" = '1' AND "locus_id" in ('{}');""".format(
        args.appname, "','".join(loci_to_get))

    files = sqlquery_to_outls(conn, sqlcommand)
    files = {x[0]: "/" + x[1] for x in files}  # {locus name: fasta file path}
    posallelesseqs = {}
    negallelesseqs = {}
    for locus in files:
        if ":" in files[locus]:
            file = files[locus].split(":")[0] + ".fasta"
        else:
            file = files[locus]
        # print(file)
        if not path.exists(file):
            sys.exit("{} allele file does not exist at {}".format(locus,file))
        alleles = SeqIO.parse(file, "fasta")
        posallelesseqs[locus] = {}
        negallelesseqs[locus] = {}
        for allele in alleles:
            allelenumber = allele.id.split(":")[-1]
            if "-" not in allelenumber:
                posallelesseqs[locus][allelenumber] = str(allele.seq)
            else:
                negallelesseqs[locus][allelenumber] = str(allele.seq)
    return posallelesseqs,negallelesseqs

def match_or_assign_alleles(lev, NewPosAlleles, NewNegAlleles, assignments,
                            loci_list,no_tables, connection, args):
    """
    match any unmatched alleles to current db
    this will be needed for loci where positive allele wasn't in ref allele fasta in reads->alleles OR
    where the allele is negative
    OTHERWISE if no match assign new (st or dst)
    :param alleles: dictionary of {locus:{allele:allele seq}}
    :param lev: MGT level
    :param NewPosAlleles: dictionary of alleles not matching reads to alleles reference alleles file with no missing data
    :param NewNegAlleles: dictionary of alleles not matching reads to alleles reference alleles file with missing data
    :param sizes: required sizes for loci
    :param all_alleles_lists: dictionary of {locus:[list of alleles in subset (if not subset all existing)]}
    :param assignments: dictionary of already assigned loci
    :param loci_list: list of loci for current level
    :param connection: sql connection object (psycopg2)
    :param args: input arguments
    :return: assignments of alleles from input + details about any new alleles including SNPs etc
    """
    # Add exact matches to pos alleles to assignments and record novel positive alleles that need naming in newpos_todo

    posalleles,negalleles = get_allele_seqs(args,connection,NewPosAlleles,NewNegAlleles,lev,no_tables)

    time1 = time.time()
    assignments, newpos_todo = exactmatch(posalleles, NewPosAlleles, assignments, loci_list)

    if args.timing:
        print("\tassign_alleles_exact".format(lev), (" --- %s seconds ---" % (time.time() - time1)))
    time1 = time.time()
    if args.query and len(newpos_todo) > 0:
        # print("newexact")
        # print(newpos_todo)
        return "newst",""

    outcomes = get_negmatches_sql(posalleles,negalleles, NewNegAlleles, assignments, loci_list, newpos_todo,
                                  args,connection)
    if args.timing:
        print("\tassign_alleles_negmatch".format(lev), (" --- %s seconds ---" % (time.time() - time1)))
    time1 = time.time()
    assignments, new_allele_outdict = sort_outcomes_and_assign(outcomes, assignments, connection, args)
    if args.timing:
        print("\tassign_alleles_all".format(lev), (" --- %s seconds ---" % (time.time() - time1)))
    return assignments, new_allele_outdict


## ALLELE PROCESSING ###


def exactmatch(alleles, NewPosAlleles, assignments, loci_list):
    """
    Takes positive alleles that were not present in set of alleles used for reads2alleles script and:
    checks if they exist in the current DB and assigns if they do
    if completely novel add to dict of new pos alleles

    :param alleles: dictionary of {locus:{allele:allele seq}}
    :param NewPosAlleles: dictionary of {locus:sequence_of_novel_pos_allele}
    :param assignments: dictionary of loci already assigned allele numbers: {locus:allele_number}
    :param loci_list: list of loci for current level

    :return: assignments dict with additional positive assignments and
    """
    newloci_todo = {}
    for locus in NewPosAlleles:
        if locus not in assignments:
            if locus in loci_list:
                for allele in alleles[locus]:
                    if "-" not in allele:
                        alleleseq = alleles[locus][allele]
                        if alleleseq == NewPosAlleles[locus]:
                            assignments[locus] = allele
                if locus not in assignments:
                    newloci_todo[locus] = NewPosAlleles[locus]

    return assignments, newloci_todo

def get_muts(newnegs,alleles,locus,newseq,muts,matchallelelist):
    #TODO only return newnegs if input alleles are negative (i.e. no matches to positive alleles)
    match = False
    for existlocus in alleles[locus]:
        oldseq = str(alleles[locus][existlocus])
        if len(newseq) == len(oldseq):
            anymut = 'no'
            for pos in range(len(newseq)):
                if newseq[pos] != oldseq[pos] and newseq[pos] not in ["N", "-"] and oldseq[pos] not in [
                    "N", "-"]:
                    anymut = 'yes'
            if anymut == 'no':
                if "-" not in existlocus:
                    matchallelelist.append(existlocus)
                allele = existlocus.split("_")[0].strip("-")
                newnegs.append(("", allele, newseq, muts))
                match = True
    return newnegs,muts,matchallelelist,match


def get_negmatches_sql(posalleles,negalleles, NewNegAlleles, assignments, loci_list, newloci_todo, args,conn):
    """
    Determine what type of allele the locus should be called as after masking high snp regions
    and calling SNPs (relative to ref allele "1") by matching seqs to existing allele seqs in DB
    :param alleles: dictionary of {locus:{allele:allele seq}}
    :param NewNegAlleles: dictionary of {locus:sequence_of_any allele with missing sequence from reads2alleles}
    :param assignments: dictionary of loci already assigned allele numbers: {locus:allele_number}
    :param sizes: dict of locus sizes
    :param all_alleles_lists: dictionary of {locus:[list of alleles in subset (if not subset all existing)]}
    :param loci_list: list of loci in current level
    :param newloci_todo: dict of {locus:sequence of novel positive allele}
    :return: outcomes dictionary {locus:("type of allele assignment", possible matching allele (can be "" or 0), newseq, muts)}
    """

    outcomes = {}
    done = []

    # scriptvariable snp_density_win = size of snp density filter sliding window
    # scriptvariable snp_density_max_num = maximum allowed snps in above window before masking with Ns will occur
    # scriptvariable Nfraction = the fraction of the gene length allowed to be Ns before being called 0

    snp_density_win = args.snpwindow
    snp_density_max_num = args.densitylim
    Nfraction = args.locusnlimit

    ## check if exact negative match exists


    for locus in NewNegAlleles:
        if locus not in assignments:  # If locus not already assigned allele
            if locus in loci_list:  # If locus is in the current level allele profile
                #  Check if new negative allele matches other negative alleles and add to assignments and done list
                for allele in negalleles[locus]:
                    newallele = NewNegAlleles[locus]
                    oldallele = negalleles[locus][allele]
                    if newallele == oldallele:
                        assignments[locus] = allele
                        done.append(locus)

    #  combine novel positive alleles with unmatched negative alleles for further processing
    combined_todo = dict(NewNegAlleles)
    for i in newloci_todo:
        combined_todo[i] = newloci_todo[i]

    #  determine what type of new allele should be assigned loci in combined_todo
    for locus in combined_todo:
        if locus not in assignments:  # if locus not already assigned
            if locus in loci_list:
                if locus not in done:  # if locus not already assigned to exact negative match (i.e. in done list)
                    muts = []
                    newnegs = []
                    newseq = str(combined_todo[locus])
                    existing_allele_sizes = [len(posalleles[locus][x]) for x in posalleles[locus]]

                    if len(newseq) not in existing_allele_sizes:
                        outcomes[str(locus)] = ("new pos allele", "0", newseq, muts)

                    else:
                        matchallelelist = []
                        if args.appname not in ["Enterica","Vibrio"]:
                            oldseq = posalleles[locus]["1"]

                            #  Get SNPs from allele relative to "1"/ref allele
                            for pos in range(len(oldseq)):
                                if newseq[pos] != oldseq[pos] and newseq[pos] not in ["N", "-"] and oldseq[pos] not in ["N",
                                                                                                                        "-"]:
                                    muts.append((oldseq[pos], str(pos), newseq[pos]))
                                    # if locus == "STM0777":
                                    #     print(muts)
                            if args.printinfo:
                                print(muts)

                        #  For each existing allele in locus check for any SNPS relative to current locus
                        #  If no muts for a given allele then add to newnegs with that allele, the sequence and mutations to ref

                        mut_per_allele = {}

                        newnegs,muts,matchallelelist,posmatch = get_muts(newnegs,posalleles,locus,newseq,muts,matchallelelist)
                        if not posmatch:
                            newnegs, muts, matchallelelist, posmatch = get_muts(newnegs, negalleles, locus, newseq,
                                                                                muts, matchallelelist)
                        # for existlocus in alleles[locus]:
                        #     oldseq = str(alleles[locus][existlocus])
                        #     if len(newseq) == len(oldseq):
                        #         anymut = 'no'
                        #         for pos in range(len(newseq)):
                        #             if newseq[pos] != oldseq[pos] and newseq[pos] not in ["N", "-"] and oldseq[pos] not in [
                        #                 "N", "-"]:
                        #                 anymut = 'yes'
                        #         if anymut == 'no':
                        #             if "-" not in existlocus:
                        #                 matchallelelist.append(existlocus)
                        #             allele = existlocus.split("_")[0].strip("-")
                        #             newnegs.append(("", allele, newseq, muts))
                        #             mut_per_allele[existlocus] = anymut
                            # if locus == "STMMW_13971":
                            #     print(existlocus,anymut,muts)

                        ##check if neg match is contradicted by pos match to same allele and remove neg match if so.
                        nnewnegs = []
                        for match in newnegs:  # a match to a
                            if match[1] in posalleles[locus]:
                                if match[1] not in matchallelelist:
                                    pass
                                else:
                                    nnewnegs.append(match)

                        newnegs = list(nnewnegs)

                        if len(newnegs) == 0:  # if no matches to new allele
                            if "N" in newseq:  # if any missing data then call 0
                                ##call as 0
                                outcomes[locus] = ("novel neg allele", "", newseq, muts)
                            else:  # if no missing data call new pos allele
                                outcomes[locus] = ("novel pos allele", "", newseq, muts)
                        elif len(newnegs) == 1:  # if only one match
                            if "N" in newseq:  # if new allele is negative
                                allele = newnegs[0][1]
                                outcomes[locus] = ("new neg allele", allele, newseq, muts)
                            else:
                                allele = newnegs[0][1]
                                #  new positive version of negative match allele (neg matches with other, non-matching pos allele are already removed)
                                outcomes[locus] = ("new pos allele", allele, newseq, muts)
                        else:  # if more than one match to new allele
                            allele_hits = list(set([neg_to_pos(x[1]) for x in
                                                    newnegs]))  # Get set of positive versions of allele that match
                            if len(allele_hits) > 1:
                                if "N" in newseq:
                                    ## this means a negative allele matches 2 or more other alleles: call as 0
                                    ##check what other related sts have at this position (by higher CC) if any called with one that can match then assign otherwise 0
                                    allele = "0"
                                    #  new negative allele for allele assigned by check_locus_allele_freqs_in_higher_cc
                                    outcomes[locus] = ("new neg allele", allele, newseq, muts)
                                else:
                                    ## check if negative matches have any pos allele associated if no then assign to neg number otherwise next pos
                                    outcomes[locus] = check_locus_allele_freqs(posalleles[locus],allele_hits, newseq, muts)
                            else:
                                if "N" in newseq:
                                    ##this means new allele is negative and only matches one other allele number (could be many neg +pos)
                                    allele = allele_hits[0]
                                    ##check what other related sts have at this position (by higher CC) if any called with one that can match then assign otherwise 0
                                    outcomes[locus] = ("new neg allele", allele, newseq, muts)
                                else:
                                    ## if there is only one possible positive match and the matches are negative
                                    allele = neg_to_pos(newnegs[0][1])
                                    outcomes[locus] = ("new pos allele", allele, newseq, muts)
    return outcomes


def sort_outcomes_and_assign(outcome, allele_assignments, connection, args):
    """
    Take outcome dict and assign allele numbers and collect new allele info
    :param outcome: dict of outcomes of get_negmatches_sql in format {locus:(outcome,possible allele, sequence,snps)}
    :param allele_assignments: dictionary of loci already assigned allele numbers: {locus:allele_number}
    :param connection: sql psycopg2 connection object
    :param args: input argparse args
    :return: updated allele assignments and new allele info in format {locus:(locus,allele assignment,sequence,snps)}
    """

    # get next allele number and next dst for each allele for loci in outcome
    next_pos_dict, next_neg_dict = get_max_loci_dict(outcome, connection, args)

    new_allele_outdict = {}
    for locus in outcome:
        if outcome[locus][1] == "0":
            allele_assignments[locus] = "0"
        else:

            # assign new number based on outcome info
            newno = assign_new_allele_names(locus, outcome[locus][0], outcome[locus][1], next_pos_dict[locus],
                                            next_neg_dict[locus])

            allele_assignments[locus] = str(newno)  # add assignment to others

            #  output new allele info
            new_allele_outdict[locus] = [(locus, str(newno), outcome[locus][2], outcome[locus][3])]

    return allele_assignments, new_allele_outdict


def assign_new_allele_names(locus, type, negallele, nextpos, nextneg_dict):
    """

    :param locus: locus being named
    :param type: positive, negative or novel negative - what type of assignment is happening
    :param negallele: if it is a neg allele which pos allele is it based on
    :param existing_alleles: list of existing alleles for that locus
    :return: next allele number in the sequence
    """

    if type == "novel pos allele":
        # assign new pos allele i.e. 8 where 7 is current highest
        newallele = nextpos

        return newallele


    elif type == "new pos allele":
        # assign pos allele where negative alleles already exist i.e. new 8 where -8_1 exists
        # (current model where pos must exist for negs to exist excludes this)
        newposallele = negallele.split("_")[0].replace("-", "")

        if int(newposallele) < int(nextpos):
            newallele = newposallele
        else:
            newallele = nextpos

        return newallele

    elif type == "new neg allele":
        # assign new negative allele i.e. -8_3 where -8_2 or 8 exists
        posallele = negallele.split("_")[0].replace("-", "")

        nextneg = nextneg_dict[posallele]

        newallele = "-" + str(posallele) + "_" + str(nextneg)

        return newallele

    elif type == "novel neg allele":
        # assign neg allele to new overall allele i.e. -8.1 where 8 does not exist
        # (current model where pos must exist for negs to exist excludes this)
        newallele = nextpos
        newallele = "-" + str(newallele) + "_1"

        return newallele


def check_locus_allele_freqs(locusalleles,poshits, newseq, muts):
    """
    Check whether potential matches are present in subset of alleles defined by previous level CCs and assign as
    0 if not
    :param allele_subset: alleles present in subset for current locus (if subset else all alleles)
    :param called_alleles: called matches to current allele
    :return: 0 if matching allele not present in subset else matching allele number
    """
    # iterate over new allele matches and related strain allele matches, look for any match
    match = []
    existingalleles = list(locusalleles.keys())

    notexistingpos = [x for x in poshits if x not in existingalleles]

    if len(notexistingpos) == 0:
        return ("novel pos allele", "", newseq, muts)
    elif len(notexistingpos) == 1:
        newpos = notexistingpos[0]
        return ("new pos allele", newpos, newseq, muts)
    else:
        newpos = str(min(list(map(int,notexistingpos))))
        return ("new pos allele", newpos, newseq, muts)


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

    if len(recon_locus) != len(ref_locus):  # comparison with reference will break if lengths not the same
        return recon_locus

    halfwindow = int(window_size / 2)
    mutpos = []
    outlocus = list(str(recon_locus))  # Convert test sequence into list of letters
    for pos in range(len(recon_locus)):
        if recon_locus[pos] != ref_locus[pos] and recon_locus[pos] not in ["N", "-"] and ref_locus[pos] not in ["N",
                                                                                                                "-"]:
            mutpos.append(
                "X")  # if the same position doesn't match (i.e. a SNP) and that missmatch is not caused by an N or an indel
        else:
            mutpos.append("M")  # If ref and new seq are the same

    #  Get list of ranges allowing for window length over whole locus
    for x in range(halfwindow, len(ref_locus) - halfwindow):
        window = mutpos[x - halfwindow:x + halfwindow]  # get window list of Match(M) or SNP(X)
        if window.count("X") > snp_limit:
            # if num of SNPS greater than limit mask all positions in current window
            for pos in range(x - halfwindow, x + halfwindow):
                outlocus[pos] = "N"  # change to N
    outlocus = "".join(outlocus)
    return outlocus


def get_max_loci_dict(outcome, connection, args):
    """
    get next allele number and next dst for each allele for loci in outcome
    :param outcome: loci with unresolved alleles in input seqs
    :param connection: sql psycopg2 connection object
    :param args: input argparse args
    :return: next_pos_dict {locus:next allele number} & next_neg_dict {locus:{allele:next dst number for allele}}
    """
    get_max_for_loci = []
    for i in outcome:
        if outcome[i][1] != "0":
            get_max_for_loci.append(i)

    #  Get allele numbers for all loci in  get_max_for_loci
    locuslisstr = "('" + "','".join(get_max_for_loci) + "')"
    sqlquery = """Select * FROM "{}_allele" WHERE "locus_id" IN {};""".format(args.appname, locuslisstr)
    tablels = sqlquery_to_outls(connection, sqlquery)

    #  process sql out and store allele numbers as a list for each locus
    loci_allele_dict = {}
    for line in tablels:
        loc = line[-1]
        if loc not in loci_allele_dict:
            loci_allele_dict[loc] = [line[1]]
        else:
            loci_allele_dict[loc].append(line[1])

    next_pos_dict = {}
    next_neg_dict = {}

    for locus in loci_allele_dict:
        #  For each locus get maximum allele number after converting all alleles to positive
        next_neg_dict[locus] = {}
        allelelist = loci_allele_dict[locus]
        pos = [x.split("_")[0].replace("-", "") for x in allelelist if x != '']
        # assign next allele number
        posnext = max(map(int, pos)) + 1
        # if posnext == 1:
        #     input("posnext Press Enter to continue...{}".format(locus))
        next_pos_dict[locus] = str(posnext)
        next_neg_dict[locus] = {}

        #  For each called allele get all negative numbers i.e. -33_2 -> 2
        for i in pos:
            negs = [x.split("_")[1] for x in allelelist if "-" + i in x]

            if negs == []:  # if no negative values then next = 1
                next_neg_dict[locus][i] = "1"
            else:  # otherwise next = max negatives +1
                nextneg = max(map(int, negs)) + 1
                next_neg_dict[locus][i] = str(nextneg)

    return next_pos_dict, next_neg_dict


## ST/CC CALLING ###

def rec_get_merge_cclis(ccls, newmerge, level, conn, args):
    if newmerge == 0:
        return "','".join(ccls)
    else:
        query = """ SELECT DISTINCT "identifier","merge_id_id" FROM "{0}_cc1_{1}" WHERE ("identifier" in ('{2}') OR "merge_id_id" in ('{2}'));""".format(
            args.appname, level, "','".join(ccls))
        res = sqlquery_to_outls(conn, query)
        tmpls = [x[0] for x in res] + [x[1] for x in res]
        tmpls = list(set(map(str, tmpls)))
        tmpls = [x for x in tmpls if x != "None"]
        tmpls = [x for x in tmpls if x != ""]
        new = len(tmpls) - len(ccls)
        if args.timing:
            print(level, new, ccls, tmpls)
        return rec_get_merge_cclis(tmpls, new, level, conn, args)


def get_next_dst(connection, args, level, st):
    """
    for a given level and st get the next dst
    :param connection: psycopg2 connection object
    :param args: input argparse arguments
    :param level: MGT level
    :param st: ST to check for max dst
    :return: next dst
    """

    #  select largest dst give the level and st
    nextstquery = """SELECT MAX("dst") FROM "{}_ap{}_0" WHERE "st" = {};""".format(args.appname, level, st)

    res = sqlquery_to_outls(connection, nextstquery)
    if args.query:
        dst = res[0][0]
    else:
        dst = res[0][0] + 1  # get value and add 1 to result

    return dst


def get_next_st(connection, args, level):
    if args.query:
        return 0
    nextstquery = """SELECT MAX("st") FROM "{}_ap{}_0";""".format(args.appname, level)
    res = sqlquery_to_outls(connection, nextstquery)
    # print("CURRENT MAX ST",res)
    if res[0][0] == None:
        nextst=1
    else:
        nextst = res[0][0] + 1
    return nextst


def call_st_cc(stres, ccres, odcres, profile, level, odcdiffs, connection, args):
    """
    Assign ST, CC, ODCs and identify merges for CC and ODCs assigned

    :param stres: st matches in list of tuples [(st,dst),(st,dst)...]
    :param ccres: cc matches in list of tuples [(st,dst,cc),(st,dst,cc)...]
    :param odcres: dictionary of lists of tuples one for each odc {odcno:[(stA,dstA,odcA),(stB,dstB,odcA)...],
    odcno2:[(stA,dstA,odcB),(stB,dstB,odcB)...]}
    :param profile: allele profile for level as dict {locus:allele,locusb:alleleb...}
    :param level: current MGT level
    :param odcdiffs: dictionary of odc number to number of differences {1:1,2:2,3:5,4:10}
    :param connection: psycopg2 connection object
    :param args: input argparse arguments

    :return: st,dst and cc as assignment values, merges as list of ccs merged with assigned cc,
    odc dictionary of odc assignments, odcmerges dictionary of lists one for each odc with corresponding merges
    """

    ### st dst calling ###

    if args.query and profile == "newst":
        st = 0
        dst = 0
        cc = 0
        merges = []
        odc = {x: 0 for x in odcdiffs}
        odcmerges = {x: [] for x in odcdiffs}

        return st, dst, cc, merges, odc, odcmerges

    ## for query mode if function get_next_st is called in any circumstance it will return "new"

    ## check if any neg or 0 - if so then need to have dst
    need_dst = False
    zerocount = 0
    for i in profile:
        if profile[i] == "0":
            need_dst = True
            zerocount += 1
        elif "-" in profile[i]:
            need_dst = True
    # scriptvariable max_zeros = fraction of profile sts that can be called 0 - 2% (rounded up to allow 1 in small schemes)

    # get maximum number of 0s allowed (rounded up to allow 1 in small schemes)
    max_zeros_float = (len(profile.keys()) * float(args.apzerolim))
    max_zeros = math.floor(max_zeros_float)

    #  check if number of 0 allele counts is greater that limit set above
    #  if true assign blank merges and st,dst,cc as 0
    if args.printinfo:
        print('max percen can be : ' + str(max_zeros) + '\t' + 'num of zeros :' + str(zerocount))
    if zerocount > max_zeros:
        st = 0
        dst = 0
        cc = 0
        merges = []
        odc = {x: 0 for x in odcdiffs}
        odcmerges = {x: [] for x in odcdiffs}

        return st, dst, cc, merges, odc, odcmerges

    if len(stres) == 0:  # if no ST matches assign new ST and if missing data add dst of 1
        if args.query:
            st=0
            dst=0
        else:
            nextst = get_next_st(connection, args, level)
            if need_dst:
                st = nextst
                dst = 1
            else:
                st = nextst
                dst = 0
    else:
        sthits = []
        for i in stres:
            sthits.append(i[0])  # get list of sts (i[0]) ignoring dst values (i[1])

        if len(list(set(sthits))) > 1:
            ## if only one of the multiple hits is a st.0 AP then assign new neg to that ST
            intact_hits = []
            for i in stres:
                if i[1] == 0:
                    intact_hits.append(i[0])

            if len(intact_hits) > 1:
                st = get_most_frequent_st(args,intact_hits,level,connection)
                dst = get_next_dst(connection, args, level, st)
            elif len(intact_hits) == 1:
                st = intact_hits[0]
                dst = get_next_dst(connection, args, level, st)
            elif len(intact_hits) == 0:  # happens when multiple hits to non-intact st types
                # go through each st in ascending order - check if st has positive version, if so check next
                sortedhits = sorted(sthits)
                st = 0
                for sthit in sortedhits:
                    ##check if st.0 exists
                    nextstquery = """SELECT "st" FROM "{}_ap{}_0" WHERE ("st" = '{}' AND "dst" = '0');""".format(
                        args.appname, level, sthit)
                    res = sqlquery_to_outls(connection, nextstquery)

                    #  if match to st with no dst 0 profile then assign new dst to that st otherwise continue checking
                    if len(res) == 0:
                        st = sthit
                        dst = get_next_dst(connection, args, level, st)
                        break

                #  If all sthit sts have dst 0 STs that did not match then new st with dst 1
                if st == 0:
                    if args.query:
                        st = 0
                        dst = 0
                    else:
                        nextst = get_next_st(connection, args, level)
                        st = nextst
                        dst = 1




        elif len(list(set(sthits))) == 1:
            st = sthits[0]
            if need_dst:
                ## get next dst
                dst = get_next_dst(connection, args, level, st)
            else:
                ##check if st.0 exists
                nextstquery = """SELECT "st" FROM "{}_ap{}_0" WHERE ("st" = '{}' AND "dst" = '0');""".format(
                    args.appname, level, st)
                res = sqlquery_to_outls(connection, nextstquery)

                if len(res) > 0:
                    # if st.0 already exists then call new st.0, caused by situation where only difference between
                    # aps is a 0 in old AP and a new allele in new AP
                    if args.query:
                        st = 0
                        dst = 0
                    else:
                        st = get_next_st(connection, args, level)
                        dst = 0
                else:
                    dst = 0

    ### CC calling ###

    cchits = list()
    merges = list()

    for hit in ccres:
        if hit[2] != None and hit[2] != 0 and hit[2] != "":
            cchits.append(hit[2])

    cchits = list(set(cchits))  # remove redundant entries

    if len(cchits) == 0:
        if args.query:
            cc = 0
        else:
            # get max cc value from cc table for correct level
            nextstquery = """SELECT MAX("identifier") FROM "{}_cc1_{}";""".format(args.appname, level)
            res = sqlquery_to_outls(connection, nextstquery)
            if res[0][0] == None:
                nextcc = 1
            else:
                nextcc = res[0][0] + 1  # get next cc level (max+1)
            cc = nextcc
    else:
        cc = min(cchits)

        # make non-redundant pairwise tuples of merge pairs
        # this is only new merges - others may exist for this cc in the database

        if args.query:
            merges = []
        else:
            merges = [(cc, x) for x in cchits if x != cc]
            merges = list(set(merges))


    #### ODC calling

    odcmerges = {}
    odc = {}
    # print("ODCRES", odcres, odcdiffs)

    if odcres == {}:
        odcres = {x: [] for x in odcdiffs}

    for pos in range(1, len(odcdiffs)):  # get 1,2,3,4
        odchits = []
        odcdiff = odcdiffs[pos]  # get odc difference number for odc level
        odcmerges[odcdiff] = []
        odcno = pos + 1
        for hit in odcres[odcdiff]:
            if hit[2] != 0:
                odchits.append(hit[2])

        odchits = list(set(odchits))  # non-redundant list of odc matches

        if len(odchits) == 0:  # if no matches to odc assign new
            if args.query:
                odc[odcdiff] = 0
            else:
                ## get next odc number for level
                nextstquery = """SELECT MAX("identifier") FROM "{}_cc2_{}";""".format(args.appname, odcno)
                res = sqlquery_to_outls(connection, nextstquery)
                if res[0][0] == None:
                    nextodc = 1
                else:
                    nextodc = res[0][0] + 1
                odc[odcdiff] = nextodc
        else:  # if there are matches assign to smallest value and get any merges as list of merge tuples

            odccall = min(odchits)
            odc[odcdiff] = odccall  # assign the smallest odc value to result

            mergesodclist = [(odccall, x) for x in odchits if x != odccall]  # make merge tuples
            mergesodclist = list(set(mergesodclist))  # make merge tuples non-redundant

            if args.query:
                odcmerges[odcdiff] = []
            else:
                odcmerges[odcdiff] = mergesodclist

    return st, dst, cc, merges, odc, odcmerges

def get_most_frequent_st(args,stlist,level,connection):
    ## get ids for all st (including all dsts) in stlist
    ## at the same time get number of strains with that mgt id
    ## do for each st in stlist
    largest = (0, "")


    for st in stlist:
        sqlq = """SELECT * FROM "{app}_view_apcc" JOIN "{app}_isolate" ON "{app}_view_apcc".mgt_id =  "{app}_isolate".mgt_id WHERE "{app}_view_apcc".ap{l}_0_st = {st};""".format(
            app=args.appname, l=level, st=st)
        match_isolates = sqlquery_to_outls(connection, sqlq)
        nohits = len(match_isolates)
        if args.printinfo:
            print("st counts", nohits, st)
        if nohits > largest[0]:
            largest = (nohits, st)

    return largest[1]

def detect_exact_ap_matches(connection, tablesdict, level, inquery, dbname, odc_level):
    """

    :param connection: psycopg2 connection object
    :param tablesdict:
    :param level:
    :param inquery:
    :param dbname:
    :param odc_level:
    :return:
    """
    exacthitcombined = []
    for no in list(sorted(tablesdict[level].keys())):  # for each allele profile table for a given level table 0 has different columns
        if no == 0:
            #  build locus query string from locus id and allele assignments
            locus_columns = tablesdict[level][no]
            querylis = []
            for i in locus_columns:
                q = nodash_to_dash[i]
                inquery_allele = inquery[q]
                querylis.append(""""{}" = '{}'""".format(i, inquery_allele))
            andstring = " AND ".join(querylis)

            #  Use locus query string to get allele profiles that match exactly (for a given allele profile table)
            exactmatch_query = """SELECT "id" FROM "{}_ap{}_{}" WHERE ({})""".format(dbname, level, no, andstring)
            exact_hits = sqlquery_to_outls(connection, exactmatch_query)
        else:
            #  build locus query string from locus id and allele assignments
            locus_columns = tablesdict[level][no]
            querylis = []
            for i in locus_columns:
                q = nodash_to_dash[i]
                inquery_allele = inquery[q]
                querylis.append(""""{}" = '{}'""".format(i, inquery_allele))
            andstring = " AND ".join(querylis)

            #  Use locus query string to get allele profiles that match exactly (for a given allele profile table)
            exactmatch_query = """SELECT "main_id" FROM "{}_ap{}_{}" WHERE ({})""".format(dbname, level, no, andstring)
            exact_hits = sqlquery_to_outls(connection, exactmatch_query)

        #  combine exact matches from multiple allele profile tables into exacthitcombined list
        if len(exact_hits) == 0:
            exacthitcombined = []
            break
        else:
            if no == 0:
                for i in exact_hits:
                    exacthitcombined.append(i[0])
            else:
                simple_exact_hits = [x[0] for x in exact_hits]
                exacthitcombined = list(set(simple_exact_hits) & set(exacthitcombined))
                if len(exacthitcombined) == 0:
                    break

    # If one exact hit get st,dst,cc (and odc info if MGT9) info and output
    # if >1 something has gone wrong!
    # if 0 do nothing and let further processing occur

    if len(exacthitcombined) == 1:
        match = exacthitcombined[0]
        # TODO odc id names in more automated way - Salmonella_tables_cc
        if odc_level:
            ccsub = 'SELECT "st","dst","cc1_{}_id","cc2_2_id","cc2_3_id","cc2_4_id" FROM "{}_ap{}_0" WHERE "id" = {} ;'.format(
                level, dbname, level,
                match)
        else:
            ccsub = 'SELECT "st","dst","cc1_{}_id" FROM "{}_ap{}_0" WHERE "id" = {} ;'.format(level, dbname, level,
                                                                                              match)
        res = sqlquery_to_outls(connection, ccsub)
        return res, "EXACT"
        ### get st,dst,cc
    elif len(exacthitcombined) > 1:
        sys.exit("Level {} profile matches more than one ST exactly!! ({})".format(str(level), ",".join(
            list(map(str, exacthitcombined)))))
    else:
        return "", "NONE"


def remove_sts_with_nonmatching_dsts(connection, level, dbname, idmatchcounts):
    # get id and st from ap table
    get_sts = """ SELECT "id","st" FROM "{}_ap{}_0" """.format(dbname, level)

    stres = sqlquery_to_outls(connection, get_sts)

    stcounts = {}
    id_to_st = {}

    # count number of st.dsts per st total
    for inf in stres:
        st = inf[1]
        id = inf[0]
        stcounts[st] = stcounts.get(st, 0) + 1
        id_to_st[id] = st

    # count number of st.dsts per st in matching APs
    matches_st_check = {}
    for ap_id in idmatchcounts:
        st = id_to_st[int(ap_id)]
        matches_st_check[st] = matches_st_check.get(st, 0) + 1

    # if number of total st.dsts is not the same as total matching st.dsts then remove st from matches
    delst = []
    for st in matches_st_check:
        if matches_st_check[st] != stcounts[st]:
            delst.append(st)

    # remove all st.dsts from idmatchcounts if the st is in delst list
    idkeys = list(idmatchcounts.keys())
    for ap_id in idkeys:
        st = id_to_st[int(ap_id)]
        if st in delst:
            del idmatchcounts[ap_id]

    return idmatchcounts


def gather_st_cc_odc_matches(allowed_diffs, totquery, idmatchcounts, odc_level, zerocounts, args):
    """
    Gather lists of allele profile ids either matching or passing cutoffs for ST, CC and ODC calls

    :param allowed_diffs: allowed differences in each odc missmatch level
    :param totquery: length of total query (equivalent to number of loci per MGT level)
    :param idmatchcounts: {APs matching input query: the number of matches}
    :param odc_level: Boolean odc level or not
    :param zerocounts: dict of number of zero calls for each idmatchcounts AP

    :return: stmatch for ap that match exactly, ccmatch for ap that differ by 0 or 1,
    odcmatches for aps than match with at least cutoff for each odc level
    """
    ccmatch = []
    stmatch = []
    odcmatches = {x: [] for x in allowed_diffs}

    # get maximum number of 0s allowed per allele profile
    zeromatch_limit = int(
        totquery * float(
            args.apzerolim))  # scriptvariable - max number of 0s for match - set at 2% of loci rounded down

    # get st, cc and odc matches
    for id in idmatchcounts:
        if len(idmatchcounts[id]) == 0:  # if no missmatches call st match
            stmatch.append(id)

        if odc_level:
            for missmatch in allowed_diffs:  # for each allowable missmatch level for odcs


                #  if matches are >= min allowed and number of zeros is less than limit add to match list
                if len(idmatchcounts[id]) <= int(missmatch) and zerocounts[id] < zeromatch_limit:
                    if missmatch == 1:
                        ccmatch.append(id)  # if missmatch = 1 then add to ccmatch
                    odcmatches[missmatch].append(id)  # add matchto odcmatch dict

        else:  # if not odc level then just get clonal complex matches
            # TODO get 1 value from db tables
            min_matches = totquery - 1
            #  if matches are >= min allowed and number of zeros is less than limit add to match list
            if len(idmatchcounts[id]) <= 1 and zerocounts[id] < zeromatch_limit:
                ccmatch.append(id)

    return stmatch, ccmatch, odcmatches


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def get_mostvariable(args,conn):

    sqlquery="""SELECT "identifier","locus_id" FROM "{appname}_allele" WHERE identifier NOT LIKE '-%';""".format(appname=args.appname)
    stres = sqlquery_to_outls(conn, sqlquery)
    maxno = {}
    for row in stres:
        if row[0] != '':
            alleleno = int(row[0])
            locus = row[1]
            if locus not in maxno:
                maxno[locus] = alleleno
            else:
                if alleleno > maxno[locus]:
                    maxno[locus] = alleleno

    sortedloci = sorted(maxno.items(), key=itemgetter(1), reverse=True)
    sortedloci = [x[0] for x in sortedloci]
    return sortedloci


def get_matches(level, connection, inquery, allowed_diffs, tablesdict, odc_level, args, start_time,
                ignore_zeros=True):
    """
    Get matches in the correct level to input dict with structure {locus:allele_call}
    :param level: MGT level being examined
    :param connection: psycopg2 connection object
    :param inquery: input query dict
    :param allowed_diffs: number of differences allowed for CC calling in list (for normal level this ill be 1)
    for odclevel this will include the different odc cutoffs
    :param tablesdict: number and name of allele profile tables for each level
    :param matching_st_ids: sts within the current subset (if subset on defined by ccminus1 and ccminus2)
    :param odc_level: boolean if level is used for odcs
    :param args: input argparse object
    :param ignore_zeros: whether to count alleles called 0 as a match (True) or as a missmatch (False) - at the moment
    always True
    :return: lists/dicts of st matches, cc matches and odc matches
    """

    ############ first check for exact match and if there is a hit return that ST,dST and CC

    if args.timing:
        print("{} start get matches".format(level), (" --- %s seconds ---" % (time.time() - start_time)))

    if args.query and inquery == "newst":
        return [], [], {}

    dbname = args.appname
    output, outcome = detect_exact_ap_matches(connection, tablesdict, level, inquery, dbname, odc_level)

    if args.timing:
        print("{} exact get matches".format(level), (" --- %s seconds ---" % (time.time() - start_time)))


    if outcome == "EXACT":
        if args.printinfo:
            print(level, "exact match", output)
        return output, outcome, {}

    ## test below "if" - effectively if cc subsetting returns nothing below will assume new ST. if below is removed then will search whole DB - much slower.
    # if matching_st_ids == [] and args.subsetwcc:
    #     print(level, "subset ST matches")
    #     return [], [], {}
    #
    # if matching_st_ids == [] and args.subsetst:
    #     print(level, "nested subset ST matches")
    #     return [], [], {}


    idmissmatchcounts = {}
    zerocounts = {}  # store number of allele matches caused by 0 in query or existing allele


    totquery = 0

    initialise = True
    sublisno = 0
    for no in list(sorted(tablesdict[level].keys())):
        dash_nodash = {nodash_to_dash[x]:x for x in tablesdict[level][no]}
        locus_columns = [nodash_to_dash[x] for x in tablesdict[level][no]]
        sorted_locus_columns = []
        for l in args.variable_alleles:
            if l in locus_columns:
                sorted_locus_columns.append(l)


        if args.timing:
            print("table no: {}, sublist no: {}".format(no, sublisno),
                  (" --- %s seconds ---" % (time.time() - start_time)))
        query = []
        locusls = []
        for i in sorted_locus_columns:
            # q = nodash_to_dash[i]
            query_allele = inquery[i]
            locusls.append(dash_nodash[i])
            if "new" in query_allele and "-" not in query_allele:
                query.append('0')
            else:
                query.append(neg_to_pos(query_allele))
        totquery += len(query)
        locus_retreive_string = '","'.join(locusls)

        #  depending on AP table the AP name has different column heading
        if no == 0:
            keyname = "id"
            matchstring = ''
        else:
            keyname = "main_id"
            matchstring =   """ WHERE {keyname} IN ('{idls}')""".format(keyname=keyname,idls="','".join(map(str, idmissmatchcounts.keys())))

        # #  list of ids that are already over the allowdiff - below are placeholders to be added to after table 1 of a given level
        # if over_max == []:
        #     over_max_string = "(1000000000000000000000000000,2000000000000000000000000000000)"
        # else:
        #     over_max_string = "(" + ",".join(map(str, matching_st_ids.keys())) + ")"

        if odc_level:
            allowdiff = max(allowed_diffs)
        else:
            allowdiff = allowed_diffs[0]

        #  if a subset of sts is selected (matching_st_ids is not empty)
        #  then add conditional to sql requiring matches to be in subset


        sqlquery = """SELECT "{kname}","{locusls}" FROM "{db}_ap{lev}_{tableno}"{match};""".format(
            locusls=locus_retreive_string, db=dbname, lev=level, tableno=str(no), kname=keyname,
            match=matchstring)
        # print(sqlquery)
        ## submit above huge query




        stres = sqlquery_to_outls(connection, sqlquery)

        if args.timing:
            print("sql_query done", (" --- %s seconds ---" % (time.time() - start_time)))
        stres = "\n".join(["\t".join(map(str,x)) for x in stres])
        stres = re.sub(r"_[0-9]+", "", stres)
        stres = re.sub(r"-", "", stres)
        stres = stres.split("\n")
        stres = [x.split("\t") for x in stres]
        if args.timing:
            print("regex_replace done", (" --- %s seconds ---" % (time.time() - start_time)))

        min_matches = len(query) - int(allowdiff)
        res = []
        chunk = 50
        chunkls = range(0, len(locusls), chunk)
        if initialise:
            idmissmatchcounts = {x[0]: [] for x in stres}
            zerocounts = {x[0]: 0 for x in stres}
        newap = query
        existap = {x[0]:x[1:] for x in stres}

        for pstart in chunkls:
            start_time2 = time.time()
            if pstart + chunk > len(newap):
                pend = len(newap)
            else:
                pend = pstart + chunk
            newmatch = dict(idmissmatchcounts)
            for appos in idmissmatchcounts:
                ex = existap[appos]
                missmatchno = []
                for pos in range(pstart, pend):
                    #     try:
                    if newap[pos] != ex[pos]:
                        if newap[pos] != '0' and ex[pos] != '0':
                            missmatchno += [(newap[pos], ex[pos])]
                    if newap[pos] == '0' or ex[pos] == '0':
                        zerocounts[appos] += 1
                    # if not out:
                    #     missmatchno+=[(newap[pos], ex[pos])]
                newmatch[appos] += missmatchno
            idmissmatchcounts = {x: newmatch[x] for x in newmatch if len(newmatch[x]) <= allowdiff}
            if args.timing:
                print("\tmatchingstep" + str(pstart), (" --- %s seconds ---" % (time.time() - start_time2)))
        initialise = False
        if idmissmatchcounts == {}:
            break
    if idmissmatchcounts == {}:
        if args.printinfo:
            print("No Ap matches at level {}".format(level))
        return [], [], {}



    if args.timing:
        print("{} after postgres get matches".format(level), (" --- %s seconds ---" % (time.time() - start_time)))

    # Need to remove APs for all dSTs when ONE dST is ruled out - i.e. 34.0 is ruled out but not 34.2, 34.3 - need to remove all three
    ## GET list of how many AP ids correspond to each ST - use to check if all neg profiles of an ST match (if not then remove match)
    idmissmatchcounts = remove_sts_with_nonmatching_dsts(connection, level, dbname, idmissmatchcounts)

    #  Gather lists of allele profile ids either matching or passing cutoffs for ST, CC and ODC calls
    stmatch, ccmatch, odcmatches = gather_st_cc_odc_matches(allowed_diffs, totquery, idmissmatchcounts, odc_level,
                                                            zerocounts, args)

    if args.timing:
        print("{} after gather matches".format(level), (" --- %s seconds ---" % (time.time() - start_time)))

    #  convert ap ids to ST and DST ids for stmatches and save in stres
    if len(stmatch) == 0:
        stres = []
    else:
        id_list_st = "('" + "','".join(map(str, stmatch)) + "')"
        stsub = 'SELECT "st","dst" FROM "{}_ap{}_0" WHERE "id" in {} ;'.format(dbname, level, id_list_st)

        stres = sqlquery_to_outls(connection, stsub)

    #  convert ap ids to ST,DST and CC ids save in ccres
    if len(ccmatch) == 0:
        ccres = []
    else:
        id_list_cc = "('" + "','".join(map(str, ccmatch)) + "')"
        ### TODONE add mod for MGT9 to allow ODCs - need to get all 4 odc groups instead of one CC group
        ccsub = 'SELECT "st","dst","cc1_{}_id" FROM "{}_ap{}_0" WHERE "id" in {} ;'.format(level, dbname, level,
                                                                                           id_list_cc)
        ccres = sqlquery_to_outls(connection, ccsub)

    #  convert ap ids to ST,DST and ODC ids for each odc level, save each level in odcresdict
    odcresdict = {x: [] for x in allowed_diffs if x != 1}

    if odc_level:
        for pos, dif in enumerate(allowed_diffs):
            if pos != 0:
                odcmatchlis = odcmatches[dif]
                if odcmatchlis == []:
                    odcresdict[dif] = []
                else:
                    id_list_odc = "('" + "','".join(map(str, odcmatchlis)) + "')"
                    odcsub = 'SELECT "st","dst","cc2_{}_id" FROM "{}_ap{}_0" WHERE "id" in {} ;'.format(pos + 1,
                                                                                                        dbname,
                                                                                                        level,
                                                                                                        id_list_odc)

                    odcres = sqlquery_to_outls(connection, odcsub)
                    odcresdict[dif] = odcres

    if args.printinfo:
        print("\nstres", stres, "\nCCres", ccres, "\nODCres", odcresdict)

    if args.timing:
        print("{} final get matches".format(level), (" --- %s seconds ---" % (time.time() - start_time)))

    return stres, ccres, odcresdict


###### UTILS #######


def CheckDbForName(connection, name, args):
    sqlquery = """ SELECT "identifier" FROM "{}_isolate" WHERE "identifier" = '{}'; """.format(args.appname, name)

    res = sqlquery_to_outls(connection, sqlquery)

    if len(res) > 0:
        if res[0][0] == name:
            sys.exit("A Strain named {} is already present in the database".format(name))


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def neg_to_pos(inallele):
    if "-" in inallele:
        pos = inallele.split("_")[0][1:]
        return pos
    else:
        return inallele


def most_common(L):
    # get an iterable of (item, iterable) pairs
    SL = sorted((x, i) for i, x in enumerate(L))
    # print 'SL:', SL
    groups = itertools.groupby(SL, key=operator.itemgetter(0))

    # auxiliary function to get "quality" for an item
    def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        # print 'item %r, count %r, minind %r' % (item, count, min_index)
        return count, -min_index

    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]


######## IO ########


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


def split_in_alleles(InputAllelesFile):
    InputAlleles = SeqIO.parse(InputAllelesFile, "fasta")
    AllCalls = {}
    PosMatch = {}
    NewPos = {}
    NewNeg = {}
    ZeroCalls = {}
    MGT1 = ""
    species_sero = ""

    global dash_to_nodash
    global nodash_to_dash

    dash_to_nodash = {}
    nodash_to_dash = {}

    for allele in InputAlleles:
        locus = allele.description.split(":",1)[0]
        seq = str(allele.seq)
        allele = allele.description.split(":",1)[1]

        dash = str(locus)
        nodash = str(locus.replace("_", ""))

        dash_to_nodash[dash] = nodash
        nodash_to_dash[nodash] = dash

        if locus == "7_gene_ST":
            MGT1 = allele
        elif locus == "species_serotype":
            species_sero = allele.replace('"','').replace("'","")
        elif "N" in seq:
            AllCalls[locus] = "neg"
            NewNeg[locus] = seq
        elif allele[0] == "0":
            AllCalls[locus] = "Zero"
            ZeroCalls[locus] = allele[2:]
        elif seq == "":
            PosMatch[locus] = allele
            AllCalls[locus] = "match"
        elif allele == "new":
            NewPos[locus] = seq
            AllCalls[locus] = "newpos"


    return AllCalls, PosMatch, NewPos, NewNeg, ZeroCalls, MGT1, species_sero, dash_to_nodash, nodash_to_dash


def write_to_tables(alleles_out_dict, profile, level, st, dst, cc, merges, args, odc={}, odcmerge={}, exact=False):
    """

    Write data to database for a given MGT level

    :param alleles_out_dict:
    :param profile: allele profile assigned out dict
    :param level: current MGT level
    :param st: assigned st
    :param dst: assigned dst
    :param cc: assigned cc
    :param merges: any merges of cc
    :param args: argparse inputs
    :param odc: assigned odc dict of assignments
    :param odcmerge: any merges of odcs dict of lists
    :param exact: if the allele profile is already in database boolean
    :return: nothing. but write to MGT database with outputs
    """
    cctable = "1_" + str(level)
    mgtname = "MGT" + str(level)

    # scriptvariable: projectpath - location of database on computer
    # scriptvariable: alleleLocation - location of folder containing current allele fasta files

    projectpath = args.mgtpath
    alleleLocation = args.mgtalleles

    if alleles_out_dict != {}:  # if there are any new alleles called

        addAlleles(projectpath, args.mgtapp, args.appname, alleleLocation, alleles_out_dict,args.settings)  # add new alleles

        addSnpMutsToDb(projectpath, args.mgtapp, args.appname, alleles_out_dict,args.settings)  # add SNPs for new alleles

    if not exact and 0 not in [int(st), int(cc)]:  # if there is not an exact match to an existing AP
        addApForScheme(projectpath, args.mgtapp, args.appname, "MGT" + str(level), profile, st, dst, nodash_to_dash,args.settings)

        doAddClonalComplexes(projectpath, args.mgtapp, args.appname, cctable, mgtname, cc, st, dst, merges,args.settings)

        if odc != {}:  # {} is defualt so this is true when level is not used for odc
            for odcno in odc:
                cc2_no = list(odc.keys()).index(odcno) + 2
                cctable = "2_" + str(cc2_no)

                doAddClonalComplexes(projectpath, args.mgtapp, args.appname, cctable, mgtname, odc[odcno], st, dst,
                                     odcmerge[odcno],args.settings)


def update_status(newstatus, args, conn, ids, field, idtype):
    sqlcmd = """UPDATE "{0}_isolate" SET "{1}" = '{2}' WHERE "{3}" in ('{4}');""".format(
        args.appname,
        field,
        newstatus,
        idtype,
        "','".join(ids))

    cur = conn.cursor()  # generate cursor with connection
    cur.execute(sqlcmd)
    cur.close()


def write_finalout(isolate_info, stresults, no_tables, conn, view_update, MGT1Call, input_acc,all_assignments, args):
    """
    Update of database with isolate information and mgt object - link mgt data to isolate
    :param isolate_info: isolate metadata
    :param stresults: st results dictionary for all levels
    :param no_tables: ap table structure
    :param conn: psycopg2 connection object
    :param view_update: path to sql view update command
    :param args: argparse inputs
    :return: nothing
    """

    # creates isolate in database and attaches metadata

    if not args.cron:
        addInfo(args.mgtpath, args.mgtapp, args.appname, isolate_info,args.settings)
    else:
        # print(MGT1Call)
        if MGT1Call.isdigit():
            update_status(MGT1Call, args, conn, [input_acc], "mgt1", "id")
        else:
            update_status(0, args, conn, [input_acc], "mgt1", "id")

    if args.appname == "Vibrio":
        update_status(all_assignments["VC2210"], args, conn, [input_acc], "vc2210", "id")
        if MGT1Call in ["69","515"]:
            update_status("true", args, conn, [input_acc], "serovar", "id")
        else:
            update_status("false", args, conn, [input_acc], "serovar", "id")

    info = isolate_info.split("\t")
    mgtlist = info[0:2] + [info[3], info[-1]]
    levels = []
    for lev in no_tables:
        st = stresults[lev][0]
        dst = stresults[lev][1]
        levstdst = "{0}.{1}".format(st, dst)
        mgtlist.append(levstdst)
        levels.append("MGT{}".format(lev))

    # generates hgt object and link to strain
    addTheHstMatrix(args.mgtpath, args.mgtapp, args.appname, mgtlist,args.settings,levels)


def get_isolate_proj(name, conn, args):
    query = """select "{psql}_project".user_id,"{psql}_project".identifier,"{psql}_isolate".privacy_status,"{psql}_isolate".identifier from "{psql}_isolate" JOIN "{psql}_project" ON "{psql}_isolate".project_id = "{psql}_project".id WHERE "{psql}_isolate".id = '{name}'; """.format(
        psql=args.appname, name=name)

    cur = conn.cursor()  # generate cursor with connection
    cur.execute(query)  # execute the sql query
    res = cur.fetchall()  # get results and save to res as list
    cur.close()

    user = res[0][0]
    projectno = res[0][1]
    priv = res[0][2]
    strainname = res[0][3]

    return (user, projectno, priv, strainname)

def load_settings(args):

    if ".py" in args.settings:
        folder = path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
        s = args.settings.split("/")[-1]
        settingsfile = folder + "/Mgt/Mgt/" + s
    else:
        folder = path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
        settingsfile = folder + "/Mgt/Mgt/settings_" + args.settings + ".py"

    spec = importlib.util.spec_from_file_location("settings", settingsfile)
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)

    return settings

def check_alleles_file_format(args, conn, allelesfile,StrainName):
    InputAlleles = SeqIO.parse(allelesfile, "fasta")

    for allele in InputAlleles:
        headerls = allele.description.split(":")
        if len(headerls) < 2:
            update_status('F', args, conn, StrainName, 'server_status', 'id')
            sl(5)
            sys.exit("Allele file format incorrect: header should have format >[locus or infotype]:[alleleno or strain info]")

        if len(str(allele.seq)) > 50000:
            update_status('F', args, conn, StrainName, 'server_status', 'id')
            sl(5)
            sys.exit("allele sequence is too long to be a cgMLST locus (>50000bp)")

######## MAIN ########


def main():
    # sys.exit()

    args = parseargs()  ## get input arguments

    global settings

    settings = load_settings(args)

    database = settings.APPS_DATABASE_MAPPING[args.appname]
    psql_details = settings.DATABASES[database]


    args.projectPath = path.dirname(path.dirname(path.dirname(path.abspath(__file__)))) + "/"
    args.mgtalleles = settings.ABS_SUBDIR_ALLELES + "/" + args.appname + "/"

    metadata_type = args.metadata_type
    if not args.local:
        host = settings.NONLOCALHOST
    else:
        host=psql_details['HOST']

    DbConString = "dbname='{0}' host='{1}' port='{2}' user='{3}' password='{4}'".format(psql_details['NAME'],host,psql_details['PORT'],psql_details['USER'],psql_details['PASSWORD'])  ## connection info for Db - assign new user that can only do what is needed for script
    conn = psycopg2.connect(DbConString)
    conn.autocommit = True

    InputAllelesFile = args.inalleles
    if args.id == "":
        StrainName = str(InputAllelesFile).split("/")[-1].replace("_alleles.fasta", "")
    else:
        StrainName = args.id

    check_alleles_file_format(args, conn, InputAllelesFile,StrainName)

    isolate_info = args.inmeta

    serotype_d = settings.SPECIES_SEROVAR


    AllCalls, PosMatches, NewPosAlleles, NewNegAlleles, ZeroCallAlleles, MGT1Call, species_sero, dash_to_nodash, nodash_to_dash = split_in_alleles(
        InputAllelesFile)



    start_time = time.time()



    print(StrainName)
    args.strainname = str(StrainName)
    #TODO make this more simple
    # if species_sero not in serotype_d:
    #     update_status('C', args, conn, StrainName, 'server_status', 'id')
    #     update_status('S', args, conn, StrainName, 'assignment_status', 'id')
    #     update_status(species_sero, args, conn, StrainName, 'serovar', 'id')
    #     sl(5)
    #     sys.exit("{} is not compatible with the current database because its species and/or serovar ({})\
    #      is not supported (yet) OR this is the wrong database".format(StrainName, species_sero))

    if not args.cron:
        CheckDbForName(conn, StrainName, args)

    ##read/process alleles file produced by genomes_to_alleles.py

    start_time2 = time.time()
    no_tables = get_table_nos(conn,
                              args)  # descriptions of allele profile tables in format: {level:{table number: [list of locus names in table]}}
    if args.timing:
        print("\tget variable loci", (" --- %s seconds ---" % (time.time() - start_time2)))
    args.variable_alleles = get_mostvariable(args,conn)
    st_results = {}
    cc_results = {}
    merge_results = {}
    all_assignments = {}
    exact_level = {}
    profile_results = {}
    new_alleles_results = {}
    if args.timing:
        print(" initial loading", (" --- %s seconds ---" % (time.time() - start_time)))

    maxlevel = get_max_scheme(conn, args)
    minlevel = get_min_scheme(conn, args)

    for level in range(minlevel, maxlevel + 1):
        start_time1 = time.time()
        """ 1 - get allele profile for current level """

        """ get clonal complex assignments from previous schemes to use for Db subsetting - currently off by default in args.subset

        schemes without a level cchigher2 above them are not subset (i.e. MGT3 is not subset where cchigher2 = 3 because that would be subset by MGT0)

        in order to ensure that larger odc matches (i.e. odc10 get all possible matches it has a broader subset range.

        is args.subsetwcc is off no subsetting occurs although this can be significantly slower

        """
        cchigher1 = 3
        cchigher2 = 4

        if level > cchigher2 + 1 and args.subsetwcc and level != maxlevel:
            ccb1 = cc_results[level - cchigher1]
            ccb2 = cc_results[level - cchigher2]
            ccsubsetlevs = (cchigher1, cchigher2)


        elif level == maxlevel and args.subsetwcc:
            ccb1 = cc_results[maxlevel - 4]
            ccb2 = cc_results[maxlevel - 5]
            ccsubsetlevs = (4, 5)
        elif args.subsetst:
            ccb1 = st_results[maxlevel - 1]
            ccb2 = ""
        else:
            ccsubsetlevs = ()
            ccb1 = ""
            ccb2 = ""

        profile, all_assignments, new_allele_outdict = get_allele_profile(conn, level,
                                                                                           NewPosAlleles,
                                                                                           NewNegAlleles, AllCalls,
                                                                                           PosMatches,
                                                                                           ZeroCallAlleles,
                                                                                           no_tables,
                                                                                           all_assignments, args,
                                                                                           nodash_to_dash,
                                                                                           start_time,
                                                                                           ccb1=ccb1,
                                                                                           ccb2=ccb2,
                                                                                           ccsubsetlevs=ccsubsetlevs)

        if args.timing:
            print("{} get allele profile".format(level), (" --- %s seconds ---" % (time.time() - start_time)))

        profile_results[level] = profile
        new_alleles_results[level] = new_allele_outdict

        """ 2 - get matches of allele profile to existing allele profiles - exact for st inexact for cc/odc######## """

        ## TODO get num diffs from DB
        if level == maxlevel:
            nodiffs = [1, 2, 5, 10]
            odclev = True
        else:
            odclev = False
            nodiffs = [1]

        """
        stres = matching sequence types to allele profile in list of tuples [(stA,dstA),(stB,dstB)...]

        ccres = matching clonal complexes to allele profile in list of tuples [(stA,dstA,ccA),(stB,dstB,ccA)...]

        odcres = matching odcs in dict format with each odc level as key and list of tuple results as value
        {odcno:[(stA,dstA,odcA),(stB,dstB,odcA)...],odcno2:[(stA,dstA,odcB),(stB,dstB,odcB)...]}

        """
        stres, ccres, odcres = get_matches(level, conn, profile, nodiffs, no_tables, odclev, args,
                                       start_time)

        if args.timing:
            print("{} get matches".format(level), (" --- %s seconds ---" % (time.time() - start_time)))
        """
        outputs written to db below (when necessary i.e. when st already exists can ignore for write):
            1 - alleles
            2 - mutations
            3 - allele profiles with associated st and dst
            4 - clonal complexes (scripts also deal with any new merges)
        """

        odcdict = {}
        odcmerges = {}

        if ccres == "EXACT":
            """
            When Allele Profile matches existing AP perfectly cc is returned as "EXACT" string
            AND stres is formatted [(st,dst,cc,odc2,odc5,odc10)]
            """

            exact_level[level] = True
            merges = []

            #  get results from perfect hit result
            st = stres[0][0]
            dst = stres[0][1]
            cc = stres[0][2]
            if odclev:
                for odc in nodiffs:
                    if odc != 1:
                        odcdict[odc] = stres[0][3]
            st_results[level] = (st, dst)
            cc_results[level] = cc
            merge_results[level] = merges

        else:
            exact_level[level] = False

            if odclev:  # need to add odcs if level is used to get them (i.e. MGT9)
                st, dst, cc, merges, odcdict, odcmerges = call_st_cc(stres, ccres, odcres, profile, level,
                                                                     nodiffs, conn, args)
            else:
                st, dst, cc, merges, na, nb = call_st_cc(stres, ccres, odcres, profile, level, nodiffs, conn, args)

            """
            st, dst and cc are returned as integers

            cc merges returned in list of tuples as [(4,8)] if three then provide two merges with lowest 1st in each pair:
            so 4,5,8 merge would be [(4,5),(4,8)]

            for odc dicts - same as cc and merges but with an additional dict layer i.e. {odc2:odc2_value....}
            """

            st_results[level] = (st, dst)
            cc_results[level] = cc
            merge_results[level] = merges

            print(st_results)
            print(cc_results)
            print(merge_results)


        if args.timing:
            print("{} stcc called".format(level), (" --- %s seconds ---" % (time.time() - start_time)))

        if odclev:
            print("Level ", level, ", ST dST: ", st, dst, " ,CC: ", cc, " ,ODCS: ", odcdict, " Merges: ",merges, " odc Merges: ",odcmerges)
        else:
            print("Level ", level, ", ST dST: ", st, dst, " ,CC: ", cc, " Merges: ",merges)

        if not args.query:
            if level != maxlevel:  # if last level then use to make odcs
                write_to_tables(new_alleles_results[level], profile_results[level], level, st_results[level][0],
                                st_results[level][1], cc_results[level], merge_results[level], args,
                                exact=exact_level[level])
            else:
                write_to_tables(new_alleles_results[level], profile_results[level], level, st_results[level][0],
                                st_results[level][1], cc_results[level], merge_results[level], args, odc=odcdict,
                                odcmerge=odcmerges,
                                exact=exact_level[level])
        conn.commit()
        if args.timing:
            print("{} finished".format(level), (" --- %s seconds ---" % (time.time() - start_time)))

    # 'update view' sql command used for isolate searching through website
    view_update_command_path = path.dirname(path.abspath(__file__)) + "/UpdateScripts/runOnDb.sql"

    # Deal with different metadata input arrangements and get consistent isolate_info list

    if args.id == "":
        input_id = InputAllelesFile.split("/")[-1].replace("_alleles.fasta", "")
    else:
        input_id = args.id

    if args.cron:
        ## for alleles files from cron jobs - alleles files will be named "id"_alleles.fasta NOT strainname_alleles.fasta!!!!
        # TODO therefore need to retrieve strain name for isoalte add part - should modify this eventually##

        (userid, isolate_proj, isolate_privacy, strainID) = get_isolate_proj(input_id, conn, args)
        isolate_info = [userid, isolate_proj, isolate_privacy, strainID, strainID, "", "", "", "", "", "", "", "", "",
                        "", "", "", "", "", "", "A"]
        isolate_info = "\t".join(isolate_info)
    elif metadata_type == "enterobase":
        isolate_info = convert_from_enterobase(isolate_info, InputAllelesFile, MGT1Call)

    elif metadata_type == "mgt":
        input_acc = InputAllelesFile.split("/")[-1].replace("_alleles.fasta", "")
        isolate_info = convert_from_mgt(isolate_info, InputAllelesFile, MGT1Call)
        if isolate_info == []:
            isolate_info = ["Lanlab", args.project, "Public", input_acc, input_acc, "", "", "", "", "", "", "", "", "",
                            "",
                            "", "", "", "", "", "A"]
            isolate_info = "\t".join(isolate_info)
        else:
            isolate_info += "\tA"

    elif metadata_type == "none":  # if none make empty string except for basics and strain name
        ##TODO below "none" setting results in Lanlab user and public need to change to get from user
        input_acc = InputAllelesFile.split("/")[-1].replace("_alleles.fasta", "")
        isolate_info = ["Lanlab", args.project, "Public", input_acc, input_acc, "", "", "", "", "", "", "", "", "", "",
                        "", "", "", "", "", "A"]

        isolate_info = "\t".join(isolate_info)

    # Write isolate information and generate MGT object (if needed) - link MGT to isolate

    write_finalout(isolate_info, st_results, no_tables, conn, view_update_command_path, MGT1Call, input_id,all_assignments, args)

    print("Total time: ", (" --- %s seconds ---" % (time.time() - start_time)))


######## ARGUMENTS/HELP ########


def parseargs():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("inalleles", help="File path to strain alleles file (output from genomes_to_alleles.py)")
    parser.add_argument("appname", help="Name of database (i.e. Salmonella)")
    parser.add_argument("-s", "--settings", help="name of settings file to use (minus '.py')")
    parser.add_argument("-m", "--inmeta", help="File path to strain metadata")
    parser.add_argument("-t", "--metadata_type",
                        help="The source of metadata for conversion (mgt or enterobase or none if no file)",
                        default="enterobase")
    parser.add_argument("--id",
                        help="strain database id", default="")
    parser.add_argument("--project",
                        help="project that the data will be added to, not used in cron",
                        default="ENA-SRA")
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
                        default=0.04)
    parser.add_argument("--subsetwcc",
                        help="EXPERIMENTAL. ONLY FOR TESTING! Boolean. If set will limit ST search for a level based on the CC or the previous 2 levels",
                        action='store_true')
    parser.add_argument("--subsetst",
                        help="WARNING THIS WILL ONLY WORK FOR NESTED DESIGNS AND WILL BREAK CC AND ODC CALLS - ONLY USE FOR INCREASED SPEED IN large scheme calling (performance increase dubious)",
                        action='store_true')
    parser.add_argument("--timing",
                        help="print time taken to run various sections",
                        action='store_true')
    parser.add_argument("-p", "--printinfo", help="print random extra info", action='store_true')
    parser.add_argument("-c", "--cron", help="flag for use if run as part of cron_pipeline", action='store_true')
    parser.add_argument("--query", help="run allele to db as query only, no new alleles, or STs will be called onyl existing ones will be matched", action='store_true')
    parser.add_argument("--local",
                        help="use psql_details['HOST'] from settings for postgres host rather than NONLOCALHOST variable in settings",
                        action='store_true')

    args = parser.parse_args()

    args.mgtpath = path.dirname(path.dirname(path.dirname(path.abspath(__file__)))) + "/"

    args.mgtapp = "Mgt"

    return args


if __name__ == "__main__":

    main()
