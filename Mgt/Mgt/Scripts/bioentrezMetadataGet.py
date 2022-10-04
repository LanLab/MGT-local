from Bio import Entrez
import sys
# import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, date
from dateparser import parse as dateparse
import pycountry_convert
# import argparse
# import os
# import progressbar
# import pprint
# from time import sleep as sl
# import xmltodict
# import os.path


# pp = pprint.PrettyPrinter(indent=4)

# DEFAULT = datetime(1, 1, 1)

Entrez.email = "michael.payne@unsw.edu.au"

def parse_meta(instring):
    #### REWRITE 14-8-19 ####
    """
    1: Pathogen: environmental/food/other sample from Salmonella enterica
    Identifiers: BioSample: SAMN10440521; Sample name: FSIS21822761; SRA: SRS4056931
    Organism: Salmonella enterica
    Attributes:
        /strain="FSIS21822761"
        /collected by="USDA-FSIS"
        /collection date="2018"
        /geographic location="USA:WV"
        /isolation source="chicken carcass"
        /latitude and longitude="missing"
        /serovar="Typhimurium"
        /subgroup="enterica"
    """
    # print(instring)
    outd = {}
    inlines = instring.splitlines()
    for line in inlines:
        if "collected by=" in line:
            outd["NCBI_submitted"] = line.strip(" ").replace('/collected by="',"").replace('"',"")
        elif "collection date" in line:
            init_date = line.strip(" ").replace('/collection date="', "").replace('"', "")
            try:
                # print(init_date)
                strict_parsed = dateparse(init_date, settings={'STRICT_PARSING': True})
            except:
                strict_parsed = False
            # print(parsed)
            # parsed = dateparse(init_date)
            # print(parsed)
            if len(init_date) < 5:  # if only year then will be 2 or 4 chars i.e. 18 or 2018
                outd["collection_date"] = ""
                outd["collection_month"] = ""
                outd["collection_year"] = init_date
            elif not strict_parsed:  # no full date available just get year
                parsed = dateparse(init_date)
                # print(parsed)
                if parsed:
                    outd["collection_date"] = ""
                    outd["collection_month"] = parsed.strftime('%m')
                    outd["collection_year"] = parsed.strftime('%Y')
                else:
                    outd["collection_date"] = ""
                    outd["collection_month"] = ""
                    outd["collection_year"] = ""
            else:  # full date available
                # print(strict_parsed)
                outd["collection_date"] = strict_parsed.strftime('%d/%m/%Y')
                outd["collection_month"] = strict_parsed.strftime('%m')
                outd["collection_year"] = strict_parsed.strftime('%Y')

        elif "geographic location=" in line:
            inf = line.strip(" ").replace('/geographic location="', "").replace('"', "")
            outd["postcode"] = ""
            locinfo = inf.split(":")
            country = locinfo[0]
            outd["country"] = country
            if len(locinfo) > 1:
                outd["state"] = locinfo[1]

                if outd["country"].strip(" ") == outd["state"].strip(" "):
                    outd["state"] = ""
            else:
                outd["state"] = ""

            if country == "USA":
                country = "US"
                continent = pycountry_convert.country_alpha2_to_continent_code(country)
            else:
                try:
                    country_2_alpha2 = dict(pycountry_convert.map_country_name_to_country_alpha2())
                    alpha2 = country_2_alpha2[country]
                    continent = pycountry_convert.country_alpha2_to_continent_code(alpha2)
                except:
                    continent = ""
            if continent != "":
                continent = pycountry_convert.convert_continent_code_to_continent_name(continent)

            outd["continent"] = continent

        elif "isolation source" in line:
            outd["isolation_source"] = line.strip(" ").replace('/isolation source="', "").replace('"', "")
        elif "host=" in line:
            outd["host"] = line.strip(" ").replace('/host="', "").replace('"', "")
        elif "isolate=" in line:
            outd["original_id"] = line.strip(" ").replace('/isolate="', "").replace('"', "")
        elif "strain=" in line:
            if "original_id" not in outd:
                outd["original_id"] = line.strip(" ").replace('/strain="', "").replace('"', "")

        elif "Identifiers:" in line:
            inf = line.replace("Identifiers: ","")
            inf = inf.split(";")
            for i in inf:
                if "BioSample" in i:
                    outd["BioSample"] = i.strip(" ").replace("BioSample: ","")
    if "collection_date" not in outd:
        outd["collection_date"] = ""
    if "collection_year" not in outd:
        outd["collection_year"] = ""
    if "collection_month" not in outd:
        outd["collection_month"] = ""





    # print(outd)
    return outd

# #### OLD 14-8-19 ####
# def parse_meta(instring):
#     """
#     1: Pathogen: environmental/food/other sample from Salmonella enterica
#     Identifiers: BioSample: SAMN10440521; Sample name: FSIS21822761; SRA: SRS4056931
#     Organism: Salmonella enterica
#     Attributes:
#         /strain="FSIS21822761"
#         /collected by="USDA-FSIS"
#         /collection date="2018"
#         /geographic location="USA:WV"
#         /isolation source="chicken carcass"
#         /latitude and longitude="missing"
#         /serovar="Typhimurium"
#         /subgroup="enterica"
#     """
#     # print(instring)
#     outd = {}
#     inlines = instring.splitlines()
#     for line in inlines:
#         if "collected by=" in line:
#             outd["NCBI_submitted"] = line.strip(" ").replace('/collected by="',"").replace('"',"")
#         elif "collection date" in line:
#             init_date = line.strip(" ").replace('/collection date="', "").replace('"', "")
#             try:
#                 parsed = dateparse(init_date,settings={'STRICT_PARSING': True})
#                 if len(init_date) < 5: # if only year then will be 2 or 4 chars i.e. 18 or 2018
#                     outd["collection_date"] = ""
#                     outd["collection_year"] = init_date
#                 elif len(init_date) < 8: # if only year month will be 4,5 or 7 chars 9/18 or 09/18 or 09/2018
#                     outd["collection_date"] = parsed.strftime('')
#                     outd["collection_year"] = parsed.strftime('%Y')
#                 else:
#                     outd["collection_date"] = parsed.strftime('%d/%m/%Y')
#                     outd["collection_year"] = parsed.strftime('%Y')
#             except:
#                 outd["collection_date"] = ""
#                 outd["collection_year"] = ""
#
#         elif "geographic location=" in line:
#             inf = line.strip(" ").replace('/geographic location="', "").replace('"', "")
#             outd["postcode"] = ""
#             locinfo = inf.split(":")
#             country = locinfo[0]
#             outd["country"] = country
#             if len(locinfo) > 1:
#                 outd["state"] = locinfo[1]
#
#                 if outd["country"].strip(" ") == outd["state"].strip(" "):
#                     outd["state"] = ""
#
#
#             if country == "USA":
#                 country = "US"
#                 continent = pycountry_convert.country_alpha2_to_continent_code(country)
#             else:
#                 try:
#                     country_2_alpha2 = dict(pycountry_convert.map_country_name_to_country_alpha2())
#                     alpha2 = country_2_alpha2[country]
#                     continent = pycountry_convert.country_alpha2_to_continent_code(alpha2)
#                 except:
#                     continent = ""
#             if continent != "":
#                 continent = pycountry_convert.convert_continent_code_to_continent_name(continent)
#
#             outd["continent"] = continent
#
#         elif "isolation source" in line:
#             outd["isolation_source"] = line.strip(" ").replace('/isolation source="', "").replace('"', "")
#         elif "host=" in line:
#             outd["isolation_source"] = line.strip(" ").replace('/host="', "").replace('"', "")
#         elif "isolate=" in line:
#             outd["original_id"] = line.strip(" ").replace('/isolate="', "").replace('"', "")
#         elif "strain=" in line:
#             if "original_id" not in outd:
#                 outd["original_id"] = line.strip(" ").replace('/strain="', "").replace('"', "")
#
#         elif "Identifiers:" in line:
#             inf = line.replace("Identifiers: ","")
#             inf = inf.split(";")
#             for i in inf:
#                 if "BioSample" in i:
#                     outd["biosample"] = i.strip(" ").replace("BioSample: ","")
#
#
#
#
#
#     # print(outd)
#     return outd


def get_reads_and_meta_frm_ncbi(ignore,args):


    if args.days:
        d = datetime.today() - timedelta(days=int(args.days))

        dfrom = d.strftime('%Y/%m/%d')
        dto = datetime.today().strftime('%Y/%m/%d')

    elif args.range:
        dates = args.range.split(",")
        dstart = datetime.strptime(dates[0], '%d-%m-%Y')
        dend = datetime.strptime(dates[1], '%d-%m-%Y')
        # print(dstart)
        # print(dend)

        dfrom = dstart.strftime('%Y/%m/%d')
        dto = dend.strftime('%Y/%m/%d')

    # if args.onlycount:
    #     print("Searching with following parameters:\nSpecies: {}\nSerotype: {}\nFrom {} to {}".format(args.species,
    #         args.serotype, dfrom, dto))
    # else:
    #     print("Searching with following parameters:\nSpecies: {}\nSerotype: {}\nNumber of days: {}\nOutput file: {}".format(args.species,args.serotype,args.days,args.outpath))

    # if args.ignorelist:
    #     ignore = open(args.ignorelist,"r").read().splitlines()
    # else:
    #     ignore = []


    if args.species == "" and args.serovar == "":
        sys.exit("At least one of -y (serovar) or -s (species) must be set")
    elif args.species == "":
        searchterm = """({}) AND biomol dna[Properties] AND cluster_public[prop] AND "strategy wgs"[Properties] AND ("{}"[PDAT] : "{}"[PDAT]) AND "platform illumina"[Filter] """.format(
            args.serotype, dfrom, dto)
    elif args.serotype == "":
        searchterm = """ "{}"[Organism] AND biomol dna[Properties] AND cluster_public[prop] AND "strategy wgs"[Properties] AND ("{}"[PDAT] : "{}"[PDAT]) AND "platform illumina"[Filter] """.format(
            args.species, dfrom, dto)
    else:
        searchterm = """({}) AND "{}"[Organism] AND biomol dna[Properties] AND cluster_public[prop] AND "strategy wgs"[Properties] AND ("{}"[PDAT] : "{}"[PDAT]) AND "platform illumina"[Filter] """.format(args.serotype,args.species,dfrom,dto)


    #### REWRITE 14-8-19 ####

    handle = Entrez.esearch(db="sra", term=searchterm, RetMax=100000, idtype="Identifier", retmode="txt")

    record = Entrez.read(handle)

    isolatenos = len(list(record['IdList']))

    print("Found {} isolates".format(isolatenos))

    splitno = 200

    if len(record["IdList"]) > splitno:
        idlists = list(chunks(record["IdList"],splitno))
    else:
        idlists = [record["IdList"]]

    overall_comp = []
    overall_err = []

    if idlists == [[]]:
        print(record)
        sys.exit("No isolates matching current parameters were found")
    c=0
    for idlist in idlists:
        handle = Entrez.efetch(db="sra", id=idlist, rettype="runinfo", retmode="text",RetMax=100000)
        # tree = ET.parse(handle).getroot()
        inp = handle.read().splitlines()

        print("sra info",len(inp))

        h = 0
        ressrr = {}
        for i in inp:
            if i != "":
                cols = i.split(",")
                if h == 0:
                    heads = cols
                    # print(heads)
                    h = 1
                else:
                    srr = cols[0]
                    # print(heads)
                    # print(cols)
                    ressrr[srr] = dict(zip(heads[1:], cols[1:]))
        # print(ressrr)
        ressrr = {srr:ressrr[srr] for srr in ressrr if srr not in ignore}
        # print(ressrr)
        ressrr = {srr: ressrr[srr] for srr in ressrr if srr != "Run"}
        # print(ressrr)
        if len(ressrr.keys()) == 0:
            continue
        biosampletosrr = {ressrr[x]["BioSample"]: x for x in ressrr.keys()}
        srrtobiosample = {x: ressrr[x]["BioSample"] for x in ressrr.keys()}
        # print(biosampletosrr.keys())
        # print(biosampletosrr.values())
        biosampleids = [x for x in biosampletosrr.keys() if x != "BioSample"]
        biosamplels = "("+" OR ".join(biosampleids)+")"

        #print(biosamplels)

        handle = Entrez.esearch(db="BioSample", term=biosamplels, RetMax=100000, retmode="txt")

        record = Entrez.read(handle)

        # print(len(record['IdList']))

        idlis = ",".join(record['IdList'])


        handle = Entrez.efetch(db="BioSample", id=idlis, rettype="native", retmode="text")
        # tree = ET.parse(handle).getroot()
        inp = handle.read()

        metadata = inp.split("\n\n")
        # print(len(metadata))
        ressam = {}
        for i in metadata:
            #print(i)
            if len(i) > 10:
                # print(i)
                tmpres = parse_meta(i)
                if "BioSample" in tmpres:
                    biosample = tmpres["BioSample"]
                    # print(biosample)
                    ressam[biosample] = dict(tmpres)
                    c+=1

            # print(res["collection_date"],res["collection_year"])
            # for i in tmpres:
            #     print(i, tmpres[i])

        compsrr,errsrr = writeout(ressrr, ressam, srrtobiosample, args)
        overall_comp += compsrr
        overall_err += errsrr
        if c % 100 == 0:
            print("{} isolates dl".format(c))
    return overall_comp,overall_err
    #############

    ### OLD PRE REWRITE
    #
    #
    #
    #
    # handle = Entrez.esearch(db="sra", term=searchterm , RetMax=100000,idtype="Identifier", retmode="xml")
    #
    # record = Entrez.read(handle)
    #
    # no_isolates = record['Count']
    # # if args.onlycount:
    # #     print("\n{} isolates found".format(record['Count']))
    # # else:
    # # print("\nRetrieving {} isolates".format(record['Count']))
    #
    # donels = []
    # outf = open(args.outpath, "w")
    # outf.write(
    #     "User	NCBI	Public	MGT_acc	Run (NCBI)	MLST	Collection Date	Collection Year	Location Postcode	Location state	Location (Corrected - Country)	Location (Corrected - Continent)	Isolation Source	Isolation Source (Corrected)	Isolation type	Host	Host Disease	original_experiment_id	Biosample_id	srs_id	BioProject	Study_accession	total_bases\n")
    # outf.close()
    #
    #
    # outdict = {}
    #
    # # print(record)
    # # sl(100)
    #
    # splitno = 200
    #
    #
    #
    # if len(record["IdList"]) > splitno:
    #     idlists = list(chunks(record["IdList"],splitno))
    # else:
    #     idlists = [record["IdList"]]
    #
    # # print("{} isolates in {} sets of {}\n".format(len(record["IdList"]), len(idlists),splitno))
    # # bar = progressbar.ProgressBar(max_value=len(idlists))
    #
    #
    # # idlists = [["ERS008706"]]
    #
    # c = 0
    # full_srrs = []
    #
    # overall_comp = []
    # overall_err = []
    # if idlists == [[]]:
    #     print(record)
    #     sys.exit("No isolates matching current parameters were found")
    # for idlist in idlists:
    #     sraids = []
    #     srrs = []
    #     srss = []
    #     srstosrr = {}
    #     srstobioprj = {}
    #     srstostudyacc = {}
    #     srstobases = {}
    #     od = {}
    #
    #     for i in idlist:
    #         sraids.append(i)
    #
    #     multiquery = ",".join(sraids)
    #     # print(multiquery)
    #
    #     # multiquery = "SRS2207872,SRS2207867"
    #     # print(multiquery)
    #     h2 = Entrez.efetch(db="sra", id=multiquery, retmode="xml")
    #
    #
    #
    #     tree = ET.parse(h2)
    #
    #     # for i in tree.iter():
    #     #     for j in i.iter():
    #     #         print(j.tag)
    #     #         print(j)
    #     #         sl(1)
    #     tmpxml = "testxml_{}.txt".format(str(c + 1))
    #     tree.write(tmpxml)
    #     inxml = open(tmpxml,"r").read()
    #     inputxml = xmltodict.parse(inxml)
    #
    #     os.remove(tmpxml)
    #     c1 = 0
    #     c2 = 0
    #     z = 0
    #     for i in inputxml:
    #         for j in inputxml[i]:
    #             for k in inputxml[i][j]:
    #                 if isinstance(k,dict):
    #                     z+=1
    #                     # print(z)
    #                     srsloc = k["SAMPLE"]
    #                     if isinstance(srsloc,list):
    #                         srsid = srsloc[0]["IDENTIFIERS"]["PRIMARY_ID"]
    #                     else:
    #                         srsid = srsloc["IDENTIFIERS"]["PRIMARY_ID"]
    #                     runset = k["RUN_SET"]["RUN"]
    #                     if isinstance(runset,list):
    #                         srrid = runset[0]["@accession"]
    #                     else:
    #                         srrid = runset["@accession"]
    #                     # print(k["STUDY"]["IDENTIFIERS"]["EXTERNAL_ID"])
    #                     if "EXTERNAL_ID" in k["STUDY"]["IDENTIFIERS"]:
    #                         bioloc = k["STUDY"]["IDENTIFIERS"]["EXTERNAL_ID"]
    #                         try:
    #                             if isinstance(bioloc,list):
    #                                 bioprj = []
    #                                 for i in bioloc:
    #                                     if "@label" in i:
    #                                         bioprj = i["#text"]
    #                                 #     print(i)
    #                                 #     bioprj.append(i["#text"])
    #                                 # bioprj = ",".join(bioprj)
    #                             else:
    #                                 bioprj = k["STUDY"]["IDENTIFIERS"]["EXTERNAL_ID"]["#text"]
    #                         except Exception as x:
    #                             print(bioloc)
    #                             sys.exit(x)
    #                     else:
    #                         bioprj = ""
    #
    #                     studyacc = k["STUDY"]["@accession"]
    #                     if "@total_bases" in k["RUN_SET"]["RUN"]:
    #                         bases = k["RUN_SET"]["RUN"]["@total_bases"]
    #                     else:
    #                         bases = ""
    #
    #                     # print(isinstance(bases, str))
    #                     if isinstance(srsid,str) and isinstance(srrid,str) and isinstance(bioprj,str) and isinstance(studyacc,str) and isinstance(bases,str):
    #                         if srrid not in ignore:
    #                             srstosrr[srsid] = srrid
    #                             srstobioprj[srsid] = bioprj
    #                             srstostudyacc[srsid] = studyacc
    #                             srstobases[srsid] = bases
    #                             srrs.append(srrid)
    #                             full_srrs.append(srrid)
    #                             srss.append(srsid)
    #                         # elif srsid in donels:
    #                         #     c1+=1
    #                         elif srrid in ignore:
    #                             c2+=1
    #                 else:
    #                     sys.exit("object not dict:\n",k)
    #
    #     # if c1 > 0:
    #     #     print("\n{} isolates already in file\n".format(c1))
    #     # if c2 > 0:
    #     #     print("\n{} isolates in ignore list\n".format(c2))
    #
    #     if len(srss) == 0:
    #         c+=1
    #     #     bar.update(c)
    #         continue
    #
    #     catterm = " OR ".join(srss)
    #
    #     b2 = Entrez.esearch(db="biosample", term=catterm, idtype="Identifiers", RetMax=10000)
    #
    #     records = Entrez.read(b2)
    #
    #     biosample_id = ",".join(records['IdList'])
    #
    #
    #     b3 = Entrez.efetch(db="biosample", id=biosample_id, retmode="text")
    #     b4 = b3.read()
    #     infols = b4.strip("\n").split("\n\n")
    #
    #     for i in infols:
    #         id = ""
    #         for line in i.split("\n"):
    #             if line.startswith("Identifiers:"):
    #                 for idstring in line.split(";"):
    #                     if "SRA:" in idstring:
    #                         id = idstring.replace(" SRA: ","")
    #         # print(i)
    #         # sl(1)
    #
    #
    #         # if id=="":
    #         #     print(i)
    #         #     sys.exit()
    #         if id == "":
    #             continue
    #         elif id not in srstosrr:
    #             continue
    #         srr = srstosrr[id]
    #         # print(id,srr)
    #         od[srr] = parse_meta(i)
    #     # print("{} sets done".format(c))
    #     c += 1
    #     # bar.update(c)
    #
    #     compsrr,errsrr = writeout(srrs,srstosrr,od,args,srstobioprj,srstostudyacc,srstobases)
    #
    #     overall_comp += compsrr
    #     overall_err += errsrr
    #
    # return overall_comp,overall_err


def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

def fixbiores(biores,key):
    if key not in biores:
        biores[key] = ""


def writeout(srr_res, biosample_res,srr2bio, args):
    ### REWRITE 14-8-19 ###
    completedsrr = []
    for srr in srr_res:
        bios = srr2bio[srr]
        if bios in biosample_res:
            biores = biosample_res[bios]
            fixbiores(biores,'postcode')
            fixbiores(biores, 'state')
            fixbiores(biores, 'country')
            fixbiores(biores, 'isolation_source')
            fixbiores(biores, 'original_id')
            fixbiores(biores, 'continent')
            fixbiores(biores, 'host')
            outls = [args.dbuser,
                     args.dbproject,
                     args.privacy,
                     srr,
                     "",
                     "",
                     biores["collection_date"],
                     biores["collection_year"],
                     biores["collection_month"],
                     biores['postcode'],
                     biores['state'],
                     biores['country'],
                     biores['continent'],
                     biores['isolation_source'],
                     "",
                     biores["host"],
                     "",
                     "",
                     "",
                     "",
                     biores["original_id"],
                     biores["BioSample"],
                     srr,
                     srr_res[srr]["BioProject"],
                     srr_res[srr]["SampleName"],
                     srr_res[srr]["bases"]]
            # print(outls)
            outf = open(args.outpath, "a+")
            outf.write("\t".join(outls) + "\n")
            outf.close()
            completedsrr.append(srr)
    errlist = []
    return completedsrr,errlist

# ### OLD PRE REWRITE
# def writeout(srrls,srs_to_srr,outd,args,srstobioprj,srstostudyacc,srstobases):
#     # print(len(outd.keys()))
#     errors = args.outpath+".err"
#     new = args.outpath+".new"
#     completedsrr = []
#     errlist = []
#     for srs in srs_to_srr:
#         srr = srs_to_srr[srs]
#         if srr in outd:
#             od = outd[srr]
#             keyls = ["collection_date",
#                      "collection_year", 'postcode', 'state', 'country', 'continent',
#                      'isolation_source', "original_id", "biosample"]
#
#             for key in keyls:
#                 if key not in od.keys():
#                     od[key] = ""
#
#             outls = [args.dbuser, args.dbproject, args.privacy, srr, srr, "", od["collection_date"],
#                      od["collection_year"], od['postcode'], od['state'], od['country'], od['continent'],
#                      od['isolation_source'], "", "", "", "", od["original_id"], od["biosample"],srs,srstobioprj[srs],srstostudyacc[srs],srstobases[srs]]
#             outf = open(args.outpath, "a+")
#             outf.write("\t".join(outls) + "\n")
#             outf.close()
#             completedsrr.append(srr)
#         else:
#
#             errlist.append(srr)
#
#     er = open(errors, "a+")
#     er.write("\n".join(errlist))
#     er.close()
#     newf = open(new,"w")
#     newf.write("\n".join(completedsrr))
#     newf.close()
#     return completedsrr,errlist



def metadl_main(ignore,args):


    completedsrr,errlist = get_reads_and_meta_frm_ncbi(ignore,args)

    return completedsrr,errlist


