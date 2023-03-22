from time import sleep as sl
import argparse
import importlib.util
from addIsolates import addInfo
import psycopg2
import csv
import sys
from os import path
import os
import shutil

"""
Col_username = 0
Col_projectName = 1
Col_privStatus = 2
Col_isolateId = 3

## Meta data fields

# location
# Col_continent = 13 # file isolate_metadata_.txt
# Col_country = 12 # file isolate_metadata_.txt
Col_continent = 12 # file isolate_info.txt
Col_country = 11 # file isolate_info.txt
Col_state = 10 # file isolate_info.txt
Col_postcode = 9 # file isolate_info.txt

# isolation
# Col_source = 15 # file isolate_metadata_.txt
# Col_type = 16 # file isolate_metadata_.txt
# Col_host = 17 # file isolate_metadata_.txt
# Col_hostDisease = 18 # file isolate_metadata_.txt
# Col_date = 10 # file isolate_metadata_.txt

Col_source = 13 # file isolate_metadata_.txt
Col_type = 14 # file isolate_metadata_.txt
Col_host = 15 # file isolate_metadata_.txt
Col_hostDisease = 16 # file isolate_metadata_.txt
Col_date = 6 # file isolate_metadata_.txt
Col_year = 7
Col_month = 8

Col_mgt1 = 18
Col_serovar = 19

"""


def parseargs():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--inmeta", help="input tsv file in mgt format")
    parser.add_argument("-r", "--input",
                        help="Folder containing reads (*_1.fastq.gz and *_2.fastq.gz) where *=Col_isolateId in inmeta",
                        required=True)
    parser.add_argument("-s", "--settings", help="name of settings file to use (minus '.py')",
                        required=True)
    parser.add_argument("--inreads",
                        help="inputs are reads",
                        action='store_true')
    parser.add_argument("--inalleles",
                        help="inputs are alleles",
                        action='store_true')
    parser.add_argument("--todownload",
                        help="reads not provided and should be downloaded - name must be SRA accession",
                        action='store_true')
    parser.add_argument("--appname", help="App name", default="Salmonella")
    parser.add_argument("--projectPath", help="Path to project folder",
                        required=True)
    parser.add_argument("--projectName", help="Name of project",
                        default="Mgt")

    args = parser.parse_args()

    return args


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


def get_isolate_info(args, conn, strainname):
    reads_query = """ SELECT "id","identifier","project_id" FROM "{}_isolate" WHERE "identifier" = '{}'; """.format(
        args.appname, strainname)
    res = sqlquery_to_outls(conn, reads_query)

    idno = res[0][0]
    projno = res[0][2]

    return idno, projno


def add_alleles(args, conn, uploads):
    first = True
    reader = csv.reader(open(args.inmeta, 'r'), delimiter='\t')
    all_lines = []
    for line in reader:
        if first:
            first = False
            continue
        print(line)
        strain_id = line[3]
        dbuser = line[0]

        allid = args.input + "/" + strain_id + "_alleles.fasta"

        idno, projno = get_isolate_info(args, conn, strain_id)

        albase = "/{}/{}/{}/{}/".format(args.appname, dbuser, projno, idno)

        if path.exists(allid):

            if not path.exists(uploads + albase):
                os.makedirs(uploads + albase)

            newal = "{}{}/{}_alleles.fasta".format(uploads, albase, idno)

            if not path.exists(newal):
                shutil.copy2(allid, newal)
            else:
                os.remove(newal)
                shutil.copy2(allid, newal)

            f1db = "{}{}_alleles.fasta".format(albase, idno)

            reads_query = """ UPDATE "{0}_isolate" SET "server_status" = 'V' WHERE "id" = '{1}';
                              UPDATE "{0}_isolate" SET "file_alleles" = '{2}' WHERE "id" = '{1}';""".format(
                args.appname, idno, f1db)
            print(strain_id, "allele paths added, status set to V")

            cur = conn.cursor()  # generate cursor with connection
            cur.execute(reads_query)
            cur.close()
        else:
            print("1 or more reads for isolate {} missing or not in correct format (name_1.fastq.gz)".format(strain_id))


def add_reads(args, conn, uploads):
    first = True
    reader = csv.reader(open(args.inmeta, 'r'), delimiter='\t')
    all_lines = []
    for line in reader:
        if first:
            first = False
            continue
        print(line)
        strain_id = line[3]
        dbuser = line[0]

        fq1 = args.input + "/" + strain_id + "_1.fastq.gz"
        fq2 = args.input + "/" + strain_id + "_2.fastq.gz"

        idno, projno = get_isolate_info(args, conn, strain_id)

        fqbase = "/{}/{}/{}/{}/".format(args.appname, dbuser, projno, idno)

        if path.exists(fq1) and path.exists(fq2):

            if not path.exists(uploads + fqbase):
                os.makedirs(uploads + fqbase)

            newf1 = "{}{}/{}_1.fastq.gz".format(uploads, fqbase, idno)
            newf2 = "{}{}/{}_2.fastq.gz".format(uploads, fqbase, idno)

            if not path.exists(newf1):
                shutil.copy2(fq1, newf1)
            else:
                os.remove(newf1)
                shutil.copy2(fq1, newf1)

            if not path.exists(newf2):
                shutil.copy2(fq2, newf2)
            else:
                os.remove(newf2)
                shutil.copy2(fq2, newf2)

            f1db = "{}{}_1.fastq.gz".format(fqbase, idno)
            f2db = "{}{}_2.fastq.gz".format(fqbase, idno)

            reads_query = """ UPDATE "{0}_isolate" SET "server_status" = 'U' WHERE "id" = '{1}';
                              UPDATE "{0}_isolate" SET "file_forward" = '{2}' WHERE "id" = '{1}';
                              UPDATE "{0}_isolate" SET "file_reverse" = '{3}' WHERE "id" = '{1}';""".format(
                args.appname, idno, f1db, f2db)
            print(strain_id, "read paths added, status set to U")

            cur = conn.cursor()  # generate cursor with connection
            cur.execute(reads_query)
            cur.close()
        else:
            print("1 or more reads for isolate {} missing or not in correct format (name_1.fastq.gz)".format(strain_id))


def set_to_X(args, conn, X):
    first = True
    reader = csv.reader(open(args.inmeta, 'r'), delimiter='\t')
    for line in reader:
        if first:
            first = False
            continue
        strain_id = line[3]
        idno, projno = get_isolate_info(args, conn, strain_id)

        reads_query = """ UPDATE "{0}_isolate" SET "server_status" = '{2}' WHERE "id" = '{1}';""".format(
            args.appname, idno, X)
        cur = conn.cursor()  # generate cursor with connection
        cur.execute(reads_query)
        cur.close()


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


def main():
    args = parseargs()
    settings = load_settings(args)

    uploads = settings.ABS_MEDIA_ROOT

    database = settings.APPS_DATABASE_MAPPING[args.appname]

    args.database = database

    psql_details = settings.DATABASES[database]

    args.psqldb = psql_details['NAME']

    DbConString = "dbname='{0}' host='{1}' port='{2}' user='{3}' password='{4}'".format(psql_details['NAME'],
                                                                                        psql_details['HOST'],
                                                                                        psql_details['PORT'],
                                                                                        psql_details['USER'],
                                                                                        psql_details[
                                                                                            'PASSWORD'])  ## connection info for Db - assign new user that can only do what is needed for script

    conn = psycopg2.connect(DbConString)
    conn.autocommit = True

    addInfo(args.projectPath, args.projectName, args.appname, args.inmeta, args.settings)

    if args.todownload:
        set_to_X(args, conn, "D")
    elif args.inreads:
        set_to_X(args, conn, "X")
        add_reads(args, conn, uploads)
    elif args.inalleles:
        add_alleles(args, conn, uploads)


if __name__ == '__main__':
    main()
