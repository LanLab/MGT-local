from django.shortcuts import render
# Create your views here.

from django.conf import settings
APPS_DATABASE_MAPPING = settings.APPS_DATABASE_MAPPING

# from Mgt.settings import APPS_DATABASE_MAPPING
import sys


def page(request):
    # list of databases... how to get
    app_db_mapping = APPS_DATABASE_MAPPING
    app_retrieval_freq = settings.NCBI_RETRIEVAL_FREQUENCY
    # read models statistics and pass to the templates.
    stats = getStatistics(app_db_mapping, app_retrieval_freq)
    print(stats)
    return render(request, 'Home/index.html', {"name_mapping": app_db_mapping, "stats": stats})


def getStatistics(app_db_mapping, app_retrieval_freq):
    dict_stats = dict()
    for appName in app_db_mapping:
        # dict['dbName'] = dict{orgnaismName => {val}, }
        dict_stats[appName] = dict()
        appClass = __import__(appName + ".models")
        try:
            ref = appClass.models.Reference.objects.get()
            # projects_public = appClass.models.Project.objects.filter(
            #     privacy_status="PU")
            #num_publicIsolates = appClass.models.Isolate.objects.filter(
            #    project__in=projects_public).count()
            num_publicIsolates = appClass.models.Isolate.objects.filter(privacy_status="PU").count()

            if appName in app_retrieval_freq: 
                retrievalFreq = app_retrieval_freq[appName]
            else: 
                retrievalFreq = None
        except Exception as e:
            sys.stderr.write("database: " + appName + " not set up")
            # sys.stderr.write("Error" + e)
        else:
            # addOrUpdateToDict(dict_stats[appName], 'organism', ref.identifier)
            dict_stats[appName] = dict()
            dict_stats[appName]['organism'] = ref.organism
            # get only the public isolate count!
            dict_stats[appName]['num_publicIsolates'] = num_publicIsolates
            dict_stats[appName]['retrievalFreq'] = retrievalFreq 

            # add counts of number of public isolates
            # how many are assigned, how many in queue etc
        finally:
            pass

    return dict_stats


"""

def addOrUpdateToDict(dict_stats, key, value):

    if key not in dict_stats:
        dict_stats[key] = value
"""
