#!/usr/bin/python3
import sys
import os
import importlib
import django
from datetime import date
import argparse
import math
import re
import glob
# import shutil
# from subprocess import Popen, PIPE, STDOUT
##################################################### TOP_LVL
def createTheDump(mgtPath, settingModuleName, queryNumLimit):

    #print('Mgt path ' + mgtPath)
    #print('Django project name ' + settingModuleName)
    #print('Query limit ' + str(queryNumLimit))



    # Load the settings file
    sys.path.append(mgtPath)
    os.environ['DJANGO_SETTINGS_MODULE'] = settingModuleName
    django.setup()
    from django.conf import settings
    # print(settings.APPS_DATABASE_MAPPING)
    # print(settings.PU_DIR)

    dir_filesForDownload = settings.FILES_FOR_DOWNLOAD
    if re.match("^\.\/", dir_filesForDownload):
        dir_filesForDownload = re.sub('^\.\/', mgtPath, dir_filesForDownload)

    if not os.path.exists(dir_filesForDownload):
        sys.exit("Error: folder not found \'" + dir_filesForDownload + "\'")


    # Loop through each app
    for appName in settings.APPS_DATABASE_MAPPING:
        if (appName != 'ShigEiFinder'):

            # print (mgtPath + appName + "/" + settings.PU_DIR + "/")

            appClass = __import__(appName + ".models")


            tns_mgt9 = getLastMgtLvl(appClass)


            #filename =  puPath + appName + "_aps_" + str(date.today()) + ".txt"
            filename =  appName + "_aps_" + str(date.today()) + ".txt"

            print ("## " + filename);

            getAndPrint(appClass, queryNumLimit, tns_mgt9, filename)

            os.system('tar -cvzf ' + filename + ".tar.gz " + filename)
            # os.rename(filename + ".tar.gz",  puPath + filename + ".tar.gz")

            print('Moving: ' + './' + filename + ".tar.gz to " + dir_filesForDownload + filename + ".tar.gz")
            os.system('cp ' + filename+'.tar.gz ' + dir_filesForDownload + filename+'.tar.gz')
            os.system('rm ' + filename+'.tar.gz ')
            #subprocess.run('mv ' + filename + ".tar.gz " +  puPath + filename + ".tar.gz", shell=True)


            os.remove(filename)
            # subprocess.run('tar -cvzf ' + filename '')


            # Delete all other files in the folder
            apFiles = glob.glob(dir_filesForDownload + appName + '_aps_[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].txt.tar.gz')
            print(apFiles)

            for apFn in apFiles:
                if apFn != dir_filesForDownload + filename + '.tar.gz':
                    os.remove(apFn)
                    # print (apFiles)

##################################################### AUX - Table names
def getLastMgtLvl(appClass):
     mgt9Obj = appClass.models.Tables_ap.objects.filter(table_num=0).order_by('-display_order')[0]

     tns_mgt9 = appClass.models.Tables_ap.objects.filter(scheme=mgt9Obj.scheme).order_by('table_num').values('table_name')

     return tns_mgt9


##################################################### AUX - ap



def getAndPrint(appClass, queryNumLimit, tns_mgt9, filename):

    numPubIso = appClass.models.Isolate.objects.filter(privacy_status='PU', assignment_status='A').count()

    print ("## " + str(appClass), flush=True)

    totalNumQuerys = calcNumQuerys(numPubIso, queryNumLimit)

    print(str(numPubIso) + "\t" + str(totalNumQuerys), flush=True)


    fh = open(filename, 'w+')


    (dict_tableObjs, dict_colsToKeep, headerStr) = setupColumnsInMgt9Tables(tns_mgt9, appClass)


    headerStr = "Isolate" + headerStr
    fh.write(headerStr + "\n")

    zeroTn = tns_mgt9[0]['table_name']

    # Each query
    startCnt = 0; endCount=200
    for queryNum in range(0, totalNumQuerys):
        dict_tblAp9Vals = {} # dict_{ap9tn} = querySet

        if endCount > numPubIso:
            endCount = numPubIso


        print (str(queryNum) + "\t" + str(startCnt) + "\t" + str(endCount), flush=True)
        
        


        mgt9Ids = appClass.models.Isolate.objects.filter(privacy_status='PU', assignment_status='A').order_by('id').values_list('mgt__' + zeroTn, flat=True)[startCnt:endCount] # removed: **{'mgt__' + zeroTn+"__isnull": False}

        # mgt9Ids = appClass.models.Isolate.objects.filter(privacy_status='PU', assignment_status='A', **{'mgt__' + zeroTn+"__isnull": False}).order_by('id').values_list('mgt__' + zeroTn, flat=True)[startCnt:endCount]




        if len(mgt9Ids) > 0:
            # Each ap9 table.

            for tnObj in tns_mgt9:
                if tnObj['table_name'] == zeroTn:
                    mgt9Objs = dict_tableObjs[tnObj['table_name']].objects.filter(id__in=[mgt9Ids]).values(*dict_colsToKeep[tnObj['table_name']]) # .defer(*dict_colsToExcl[tnObj['table_name']])

                    dict_tblAp9Vals[tnObj['table_name']] = mgt9Objs
                else:
                    mgt9Objs = dict_tableObjs[tnObj['table_name']].objects.filter(main__id__in=[mgt9Ids]).values(*dict_colsToKeep[tnObj['table_name']]) #.defer(*dict_colsToExcl[tnObj['table_name']]).values()

                    dict_tblAp9Vals[tnObj['table_name']] = mgt9Objs

                # print (mgt9Objs);
            # print (isolate_objs)


        # print(iso_ap9Ids)

        iso_ap9Ids = appClass.models.Isolate.objects.filter(privacy_status='PU', assignment_status='A').order_by('id').values_list('identifier', 'mgt__' + zeroTn)[startCnt:endCount]
        # **{'mgt__' + zeroTn+"__isnull": False} Removed just now!

        print (iso_ap9Ids.query, flush=True)
        # Do the printing

        for (iso, ap9Id) in iso_ap9Ids:
            fh.write(iso) # + "\t" + str(ap9Id))

            for tnObj in tns_mgt9:
                if tnObj['table_name'] in dict_tblAp9Vals: # If value is present.
                    findAndGenString(dict_tblAp9Vals[tnObj['table_name']], dict_colsToKeep[tnObj['table_name']], ap9Id, fh)
                else: # If value is not present
                    printLineToFile(dict_colsToKeep[tnObj['table_name']], {}, fh)
                    pass
            fh.write("\n")
            #for tnObj in tns_mgt9:

        startCnt = startCnt + queryNumLimit
        endCount = endCount + queryNumLimit

def findAndGenString(qsets, list_colsToKeep, ap9Id, fh):
    # print ("Printing the QS")
    for qs in qsets:
        if 'id' in qs and ap9Id == qs['id']:
            #print ("Found id " + str(qs['id']));
            printLineToFile(list_colsToKeep, qs, fh)
        elif 'main_id' in qs and ap9Id == qs['main_id']:
            # print ("Found main " + str(qs.main))
            printLineToFile(list_colsToKeep, qs, fh)

def printLineToFile(list_colsToKeep, qs, fh):

    for key in list_colsToKeep:

        if (key != 'id' and key !='main_id'):
            fh.write('\t')

            if key in qs:
                fh.write(str(qs[key]))




def setupColumnsInMgt9Tables(tns_mgt9, appClass):
    dict_tableObjs = {} # dict_{table_name} = anTableObj
    dict_colsToKeep = {} # dict_{table_name} = list[col1, col2, col3, ...]
    # dict_numCols = {} # dict_{table_name} = #numCols
    # dict_idCols = {} # dict_{table_name} = idCol

    headerStr = ""

    for tn in tns_mgt9:

        anTableObj = getattr(appClass.models, tn['table_name'])
        dict_tableObjs[tn['table_name']] = anTableObj
        dict_colsToKeep[tn['table_name']] = []

        # dict_numCols[tn['table_name']] = len(anTableObj._meta.fields)

        idColNum = 0
        for fieldObj in anTableObj._meta.fields:


            fieldName = fieldObj.get_attname()
            if re.match('^id$', fieldName) or re.match('^main_id$', fieldName):
                # dict_idCols[tn['table_name']] = idColNum
                dict_colsToKeep[tn['table_name']].append(fieldName)
            elif re.match('^cc[0-9]+\_[0-9]+\_id$', fieldName) or re.match('^date\_', fieldName):
                # dict_numCols[tn['table_name']] = dict_numCols[tn['table_name']]  - 1
                pass
            else:
                headerStr = headerStr + "\t" + fieldName
                dict_colsToKeep[tn['table_name']].append(fieldName)
            # print ()

            idColNum = idColNum + 1
    # print (dict_colsToKeep)
    return (dict_tableObjs, dict_colsToKeep, headerStr)

def calcNumQuerys(numPubIso, queryNumLimit):

    totalNumQuerys = math.ceil(numPubIso/queryNumLimit)

    return totalNumQuerys


##################################################### GETTING THE APS
def getMgtIdColNum(list_colsInfo):

	for d_ in list_colsInfo:
		if d_['table_name'] == 'mgt_id':
			return d_['db_col']



##################################################### MAIN
def main():


    parser = argparse.ArgumentParser(description="Script to generate allelic profiles in a cron.")

    parser.add_argument("--mgtBasePath", help="Base path to the Mgt database.", required=True)
    parser.add_argument("--settingFn", help="Setting file name with (Mgt.) prepended.", required=True)

    parser.add_argument("--numInQuery", help="Number of allelic profiles to get in one query.", required=False, default=[200], type=int)


    args = parser.parse_args()

    createTheDump(args.mgtBasePath, args.settingFn, int(args.numInQuery[0]))

if __name__ == '__main__':
    main()
