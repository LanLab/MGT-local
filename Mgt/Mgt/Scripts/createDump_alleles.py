#!/usr/bin/python3

import argparse
from datetime import date
import glob
import sys
import os
import django
import re

##################################################### TOP_LVL
def createTheDump(mgtPath, settingModuleName):
    sys.path.append(mgtPath)
    os.environ['DJANGO_SETTINGS_MODULE'] = settingModuleName
    django.setup()
    from django.conf import settings

    # print(settings.APPS_DATABASE_MAPPING)
    alleleDirPath = settings.ABS_SUBDIR_ALLELES

    # if not alleleDirPath.startswith("/"):
    #     alleleDirPath = "/" + alleleDirPath
    #
    #
    # if re.match('^\.\/', settings.SUBDIR_ALLELES):
    #
    #     alleleDirPath = re.sub('\.\/', mgtPath, alleleDirPath )

    if not os.path.exists(alleleDirPath):
        sys.exit("Error: unable to find the allele directory \'"  + alleleDirPath + "\'.")

    # print (alleleDirPath)

    dir_filesForDownload = settings.FILES_FOR_DOWNLOAD
    if re.match("^\.\/", dir_filesForDownload):
        dir_filesForDownload = re.sub('^\.\/', mgtPath, dir_filesForDownload)

    if not os.path.exists(dir_filesForDownload):
        sys.exit("Error: folder not found \'" + dir_filesForDownload + "\'")

    for appName in settings.APPS_DATABASE_MAPPING:
        if (appName != 'ShigEiFinder'):

            # puPath = mgtPath + appName + "/" + settings.PU_DIR + "/"


            allelesAppPath = alleleDirPath + appName + "/"
            fn = appName + "_alleles_" + str(date.today())
            allelesAppGz = fn + ".tar.gz"

            print (allelesAppGz)
            if os.path.exists(allelesAppPath):
                # os.mkdir(allelesAppPath + fn)
                os.system('cd ' + alleleDirPath + ' && tar -cvzf ' + allelesAppGz + " " + appName)
                os.system('mv ' + alleleDirPath + allelesAppGz + " " + dir_filesForDownload + allelesAppGz)


            alleleFiles = glob.glob(dir_filesForDownload + appName + '_alleles_[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].tar.gz')

            for apFn in alleleFiles:
                if apFn != dir_filesForDownload + allelesAppGz:
                    os.remove(apFn)
            # print (allelesAppPath)

##################################################### AUX


##################################################### MAIN
def main():

    parser = argparse.ArgumentParser(description="Script to zip allele files for all apps and move to puFiles for download.")

    parser.add_argument("--mgtBasePath", help="Base path to the Mgt database.", required=True)
    parser.add_argument("--settingFn", help="Setting file name with (Mgt.) prepended.", required=True)

    # parser.add_argument("--numInQuery", help="Number of allelic profiles to get in one query.", required=False, default=[200], type=int)


    args = parser.parse_args()

    createTheDump(args.mgtBasePath, args.settingFn)

if __name__ == '__main__':
    main()
