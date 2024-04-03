from . import getPoolOfCcMergeIds, rawQueries
from time import sleep as sl
from collections import OrderedDict
import time


def get_merge_dict(list_colsInfo, org):
    merge_dicts = {}
    colnames = OrderedDict()

    for coldict in list_colsInfo:

        colname = coldict['table_name']
        colno = coldict['db_col']

        colnames[colname] = colno
        # for each cc get all cc and ccmerge columns
        if colname.startswith("cc") and "merge" not in colname and colname != "cc2_1":

            querystring = f"""SELECT "identifier","merge_id_id" FROM "{org}_{colname}"; """

            (data, columns) = rawQueries.executeQuery_table(querystring, org)

            # for each pair with a mergecc add to list of lists of merges
            # if one of a pair is already in a list add the other in the pair
            # if neither are in a merge list add new merge list with those two
            # merges list is a list of lists were each list is a set of ccs to be merged
            merges = []
            for pair in data:
                cc = pair[0]
                mergecc = pair[1]
                if mergecc:
                    nmerges = []
                    inexist = False
                    for existmerges in merges:
                        newmergels = list(existmerges)
                        if cc in existmerges and mergecc not in existmerges:
                            newmergels.append(mergecc)
                            nmerges.append(newmergels)
                            inexist = True
                        elif cc not in existmerges and mergecc in existmerges:
                            newmergels.append(cc)
                            nmerges.append(newmergels)
                            inexist = True
                        elif cc in existmerges and mergecc in existmerges:
                            inexist = True
                        else:
                            nmerges.append(newmergels)
                    if not inexist:
                        nmerges.append([cc, mergecc])
                    merges = list(nmerges)

            # ccminmerge is a dict where each value is the lowest cc in a merge list and each key is a cc that will
            # merge to it
            cc_minmerge = {}
            for mergels in merges:
                mincc = min(mergels)
                for cc in mergels:
                    cc_minmerge[cc] = mincc

            # each cc table has its own minmerge dictionary
            merge_dicts[colname] = cc_minmerge
    return merge_dicts

def replace_merged_ccs(list_colsInfo,isolates,merge_dicts):
    nisolates = []
    c = 0
    # for each isolate iterate over columns and swap out where the column header is in merge_dicts and the cc is in the
    # specific merge dictionary for that cc/odc level. Doe through constructing nisolate to replace isolate tuple and
    # nisolates to replace isolates list
    for isolate in isolates:
        nisolate = tuple()
        for col in list_colsInfo:
            colno = col['db_col']
            colname = col['table_name']
            if colname not in merge_dicts:
                nisolate += (isolate[colno],)
            else:
                oldcc = isolate[colno]
                if oldcc not in merge_dicts[colname]:
                    nisolate += (isolate[colno],)
                else:
                    newcc = merge_dicts[colname][oldcc]
                    nisolate += (newcc,)

        nisolates.append(nisolate)
        if nisolate != isolate:
            c += 1
    return nisolates,c

def get_merges(list_colsInfo, isolates, org):
    """
    take list of cc and odcs from search and get any merged using existing methods getPoolOfCcMergeIds.getAndOfOrQsAndMergedIds
    """
    start_time = time.time()

    merge_dicts = get_merge_dict(list_colsInfo, org)

    nisolates,c = replace_merged_ccs(list_colsInfo, isolates, merge_dicts)

    elapsed_time = time.time() - start_time

    print("{} isolates changed. cc,odc merging in: {}".format(c,elapsed_time))
    return nisolates

