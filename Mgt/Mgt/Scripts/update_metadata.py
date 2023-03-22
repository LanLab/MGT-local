from time import sleep as sl
import argparse
import sys
from os import path

folder = path.dirname(path.abspath(__file__))
print(folder)
sys.path.append(folder)
#
# from Mgt.Mgt import settings

import readAppSettAndConnToDb
import addToTableInOrgDb
import addIsolates
import getFromTableInOrgDb
import re


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


def parseargs():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,usage="this must be run from Scripts folder within mgt project you want to edit")
    parser.add_argument("--appname", help="App name", default="Salmonella")
    parser.add_argument("--user", help="user name for files", default="Lanlab")
    parser.add_argument("--projectPath", help="Path to project folder ('/path/to/MGT/Mgt/Mgt')",
                        required=True)
    parser.add_argument("--projectName", help="Name of project",
                        default="Mgt")
    parser.add_argument("--mgt1", help="use toggle to update mgt1 (not updated by default)",
                        action='store_true')
    parser.add_argument("--isolation", help="use toggle to update isolation (not updated by default)",
                        action='store_true')
    parser.add_argument("--location", help="use toggle to update location (not updated by default)",
                        action='store_true')
    parser.add_argument("-i", "--infile", help="input metadata file")
    parser.add_argument("-s", "--settings", help="name of settings file to use (minus '.py')")

    args = parser.parse_args()

    if not args.mgt1 and not args.isolation and not args.location:
        sys.exit("None of mgt1, isolation or location set to be updated therefore nothing to update")

    return args


def handleTheFileUpdate(User, appClass, fn_isolateInfo,args):
    dict_username = dict()  # dict[username] = userObj
    dict_projectName = dict()  # dict[(username, projectName)] => projObj

    dict_md_location = dict()
    dict_md_isolation = dict()
    dict_md_extFks = dict()
    c = 0
    with open(fn_isolateInfo, 'r') as fh_:

        isHeader = True

        for line in fh_:

            if isHeader == True:
                isHeader = False
                continue

            line = re.sub('[\n\r]+$', '', line)
            line = line.replace("None", "")
            arr = line.split("\t")

            isolateName = arr[Col_isolateId]  # get isolate id

            userObj = getFromTableInOrgDb.getUser(appClass, User)  # get user id object

            dict_username[User] = userObj

            addIsolates.handleProject(appClass, dict_projectName, arr[Col_username], arr[Col_projectName],
                                      dict_username[arr[Col_username]])  # get project object and add to dict

            projObj = dict_projectName[(arr[Col_username], arr[Col_projectName])]

            isolate = appClass.models.Isolate.objects.filter(identifier=isolateName,
                                                             project=projObj)  # get isolate object that matches name and project
            # print(isolate)
            if isolate.exists():  # if the isolate exists - this will ignore isolates that do not match the project id
                # isoObj = isolate.get()

                # if new location then save and return new id obj otherwise return existing obj
                # locObj = addIsolates.handleLocation(appClass, dict_md_location, arr[Col_continent], arr[Col_country],
                #                                     arr[Col_state], arr[Col_postcode])

                # if new isolation then save and return new id obj return existing obj

                isolnObj = addIsolates.handleIsolation(appClass, dict_md_isolation, arr[Col_source], arr[Col_type],
                                                       arr[Col_host], arr[Col_hostDisease], arr[Col_date],
                                                       arr[Col_year],arr[Col_month])

                #(appClass, dict_md_location, continent, country, state, postcode):
                locationObj = addIsolates.handleLocation(appClass,dict_md_location,arr[Col_continent],arr[Col_country],arr[Col_state],arr[Col_postcode])

                # update current isolate with location and isolation

                # isoObj.update(location=locObj.id)
                # isoObj.update(isolation=isolnObj.id)

                # appClass.models.Isolate.objects.filter(identifier=isolateName, project=projObj).update(location=locObj)
                if args.isolation:
                    appClass.models.Isolate.objects.filter(identifier=isolateName, project=projObj).update(isolation=isolnObj)
                if args.location:
                    appClass.models.Isolate.objects.filter(identifier=isolateName, project=projObj).update(
                    location=locationObj)
                if args.mgt1:
                    if arr[Col_mgt1] == '':
                        mgt1=None
                    appClass.models.Isolate.objects.filter(identifier=isolateName, project=projObj).update(mgt1=arr[Col_mgt1])
                c += 1
                if c % 100 == 0:
                    print(c)

    print("{} strains with new metadata".format(c))


def update_7gene(appClass, infile):
    c = 0
    with open(infile, 'r') as inf:
        for line in inf:
            cols = line.split("\t")
            isolate = cols[0].split("/")[0]
            if cols[1] == "senterica" and cols[2].isdigit():
                st = cols[2]
                appClass.models.Isolate.objects.filter(identifier=isolate).update(mgt1=st)
                c += 1
                if c % 100 == 0:
                    print(c)


def main():
    args = parseargs()

    readAppSettAndConnToDb.setupEnvPath(args.projectPath, args.projectName, args.settings)

    appClass = readAppSettAndConnToDb.importAppClassModels(args.appname)

    handleTheFileUpdate(args.user, appClass, args.infile,args)

    # update_7gene(appClass,args.infile)


if __name__ == '__main__':
    main()
