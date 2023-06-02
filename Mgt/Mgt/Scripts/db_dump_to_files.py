from time import sleep as sl

import argparse
import sys
from os import path
import psycopg2
import importlib.util

"""
1 - all SNPs as (locus:allele g.123C>T)
2 - all alleles (as fasta files, header >locus:allele)
3 - all CCs (as ccfile and ccmerges)
    a - MGT2_cc.txt = (st    dst original_MGT2_CC    current_MGT2_CC)
    b - MGT2_cc_merges.txt = (Original cc   Merged with)
4 - all allele profiles (st  dst locusA  locusB.......)
5 - all isolates (Username  Project privacy_status  Isolatename blank   blank   date    year    month   postcode    state   country continent   source  type    host    hostdisease blank   7geneMLST   serovar) - only public
6 - all mgt assignments (Username Project   Isolatename AssignmentStatus    MGT2    MGT3    MGT4    MGT5    MGT6    MGT7    MGT8    MGT9) - only public
"""

def get_conn(args):
    database = settings.APPS_DATABASE_MAPPING[args.appname]

    args.database = database

    psql_details = settings.DATABASES[database]

    args.psqldb = psql_details['NAME']

    DbConString = "dbname='{0}' host='{1}' port='{2}' user='{3}' password='{4}'".format(psql_details['NAME'],psql_details['HOST'],psql_details['PORT'],psql_details['USER'],psql_details['PASSWORD'])  ## connection info for Db - assign new user that can only do what is needed for script


    conn = psycopg2.connect(DbConString)
    conn.autocommit = True
    return conn

def getsnps(args,con):
    sqlq = """SELECT """
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

def get_st(args):

    hgtquery1 = """ SELECT "{appname}_isolate".identifier,"ap{lev}_0","ap{lev}_0_st","ap{lev}_0_dst" FROM "{appname}_isolate" JOIN "{appname}_view_apcc" ON "{appname}_isolate".mgt_id = "{appname}_view_apcc".mgt_id; """.format(
                lev=args.lev, appname=args.appname)


    res = sqlquery_to_outls(conn, hgtquery1)

    return res

def get_ap(args,conn,apidlist,ap_tables,maxlevel):
    """
    get allele profiles as dict for each locus (key = st.dst)
    :param args:
    :return:
    """

    aplis = []
    locusnames = []
    aplisdict = {}

    apidlist = list(map(str,apidlist))
    #### TODO the below "X" in table is the largest scheme number
    for table in ap_tables:
        if maxlevel in table:
            last = -6
        else:
            last = -3
        # print(table)
        loci_query = """
        SELECT *
        FROM
        information_schema.columns
        WHERE
        table_name = '{}_{}'
        """.format(args.appname,table)
        locils = sqlquery_to_outls(conn,loci_query)
        locils = [x[3] for x in locils]
        if 'dst' in locils:
            loci = locils[3:last]
        else:
            loci = locils[1:-2]
        # print(loci[0],loci[-1])

        locusnames += loci
        if "_0" in table:
            allele_query = """
                    SELECT *
                    FROM
                    "{0}_{1}"
                    WHERE "id" in ('{2}');
                    """.format(args.appname, table,"','".join(apidlist))

            allelels = sqlquery_to_outls(conn, allele_query)
            for res in allelels:
                res_ap = res[3:last]
                resid = res[0]
                aplisdict[resid] = list(res_ap)

                # alleles = allelels[0][3:last]
            # print(alleles)
            # aplis += alleles
        else:
            allele_query = """
                                SELECT *
                                FROM
                                "{0}_{1}"
                                WHERE "main_id" in ('{2}');
                                """.format(args.appname, table, "','".join(apidlist))

            allelels = sqlquery_to_outls(conn, allele_query)
            for res in allelels:
                res_ap = list(res[1:-2])
                resid = res[0]
                aplisdict[resid]+=res_ap

    # print(len(locusnames),len(aplis))
    apdict = {}
    for id in aplisdict:

        apdict[id] = dict(zip(locusnames, aplisdict[id]))

    # apdict = dict(zip(locusnames, aplis))

    # for i in apdict:
    #     print(i,apdict[i])
    #     sl(0.5)

    return apdict,locusnames


def parseargs():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-s", "--strain", help="strain name")
    parser.add_argument("-l", "--strainlist", help="list of strain names one per line")
    parser.add_argument("-d", "--appname", help="App name", default="Salmonella")
    parser.add_argument("-o", "--outprefix", help="output file will be {outprefix}{strainname}.vcf")
    parser.add_argument("--settings", help="settings suffix (i.e. mgtcron)", required=True)


    args = parser.parse_args()

    return args

def load_settings(args):
    # folder = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
    #
    # settingsfile = folder + "/Mgt/settings_" + args.settings + ".py"
    settingsfile = args.settings
    # print(args.settings)
    spec = importlib.util.spec_from_file_location("settings", settingsfile)
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)

    return settings

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

def main():
    sys.exit("Work in progress, please come back later :)")
    # args = parseargs()

    # global settings
    #
    # settings = load_settings(args)
    #
    # conn = get_conn(args)
    #
    # args.maxscheme = get_max_scheme(conn,args)
    #
    # getsnps(args,conn)


if __name__ == '__main__':
    main()