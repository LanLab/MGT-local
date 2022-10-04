from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from django.conf import settings
APPS_DATABASE_MAPPING = settings.APPS_DATABASE_MAPPING

# from Mgt.settings import APPS_DATABASE_MAPPING
import sys

def page(request):
# return HttpResponse('a users project management page')
#return render()
	app_db_mapping = APPS_DATABASE_MAPPING

	userStats = getUserStatistics(request.user, app_db_mapping)

	return render(request, 'Home/home.html', {'userStats': userStats})



def getUserStatistics(userId, app_db_mapping):
	dict_userStats = dict()

	for appName in app_db_mapping:
		appClass = __import__(appName + ".models")


		key = appName
		try:
			key = appClass.models.Reference.objects.get().organism
			pass
		except:
			pass

		dict_userStats[key] = dict()
		dict_userStats[key] = {'appName': appName}
		try:
			if appClass.models.User.objects.filter(userId=userId).count() > 0:
				userObj = appClass.models.User.objects.get(userId=userId)
				projObjs = appClass.models.Project.objects.filter(user=userObj)
				dict_userStats[key]['numProjects'] = projObjs.count()
				dict_userStats[key]['numIsolates'] = appClass.models.Isolate.objects.filter(
                project__in=projObjs).count()
		except Exception as e:
			dict_userStats[key]['numProjects'] = 0
			dict_userStats[key]['numIsolates'] = 0
			sys.stderr.write(str(e))
		else:
			pass
		finally:
			pass

	print(dict_userStats)
	return dict_userStats
