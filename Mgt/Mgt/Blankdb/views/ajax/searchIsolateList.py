from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json
from Blankdb.views.FuncsAuxAndDb import getHeaders, routeToRightRawQFn, getPoolOfCcMergeIds, mergeCcOdc
from Blankdb.models import View_apcc
from itertools import *
from django.db import connections
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404, render
from Blankdb.views.FuncsAuxAndDb import dataExtractTransform as det
from Blankdb.views.FuncsAuxAndDb import queryDb
from Blankdb.views.FuncsAuxAndDb.makeCsvString import makeCsv
from Blankdb.views.FuncsAuxAndDb.makeCsvString_mr import makeCsv_andSendToMr
from Blankdb.views.FuncsAuxAndDb import constants as c
from Blankdb.views.FuncsAuxAndDb import constants_local as cl
from Blankdb.views.FuncsAuxAndDb import getPoolOfCcMergeIds as getCcMergeIdsList
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from types import MethodType
from django.db.models import Q
import re
from Blankdb.views.FuncsAuxAndDb import sessionFns as ses
from Blankdb.views.FuncsAuxAndDb import mgt9Aps
@csrf_exempt
def page(request):

	sessionVar = list()

	pageNumToGet = 1
	orderBy = None
	dir = None

	isCsv = False
	isMgt9Ap = False
	maxIsolatesPerPage = c.TOTAL_ISO_PER_PAGE
	isGrapeTree = False
	isMr = False

	arr_ap = []; arr_cc = []; arr_epi = []; arr_iso = []; arr_isln = []; arr_loc = [];
	searchType = 'and';

	if (('orderBy' in request.POST and len(request.POST['orderBy']) > 0) or ('pageNumToGet' in request.POST and len(request.POST['pageNumToGet']) > 0)) or ('isCsv' in request.POST and request.POST['isCsv'] == 'true') or ('isMgt9Ap' in request.POST and request.POST['isMgt9Ap'] == 'true') or ('isMr' in request.POST and request.POST['isMr'] == 'true'):

		# session var should be reused and updated
		sessionVar_json = request.session['sessionVar']
		sessionVar = json.loads(sessionVar_json)

		if sessionVar[0]['pageType'] != cl.SearchIsolateList:
			raise Http404()

		(arr_ap, arr_cc, arr_epi, arr_iso, arr_isln, arr_loc, searchType) = ses.loadSessionSearchVars(sessionVar)

		print(sessionVar);
		if 'orderBy' in request.POST and len(request.POST['orderBy']) > 0:
			orderBy = request.POST['orderBy']
			dir = request.POST['dir']

			# update session with posted values
			sessionVar[0]['orderBy'] = orderBy
			sessionVar[0]['dir'] = dir

			pageNumToGet = ses.loadIfInSession(sessionVar, 'pageNumToGet', 1)


		if 'pageNumToGet' in request.POST and len(request.POST['pageNumToGet']) > 0:
			pageNumToGet = int(request.POST['pageNumToGet'])

			# update session with posted values
			sessionVar[0]['pageNumToGet'] = pageNumToGet

			orderBy = ses.loadIfInSession(sessionVar, 'orderBy', None)
			dir = ses.loadIfInSession(sessionVar, 'dir', None)

		if ('isCsv' in request.POST and request.POST['isCsv'] == 'true'):
			isCsv = True;
			maxIsolatesPerPage = c.TOTAL_ISO_PER_DOWNLOAD

		if ('isMr' in request.POST and request.POST['isMr'] == 'true'):
			isMr = True;

		if ('isMgt9Ap' in request.POST and request.POST['isMgt9Ap'] == 'true'):
			isMgt9Ap = True
			maxIsolatesPerPage = c.TOTAL_MGT9_ISO_DOWNLOAD

			if ('isGrapeTree' in request.POST and request.POST['isGrapeTree'] == 'true'):
				isGrapeTree = True


	elif ses.isASearchPresent(request.POST):
		print ('Lord snow 2 ' + str(ses.isASearchPresent(request.POST)))
		print (request.POST)

		sessionVar.append(dict())

		(arr_ap, arr_cc, arr_epi, arr_iso, arr_isln, arr_loc, searchType) = ses.loadRequestSearchVars(request.POST)

		sessionVar[0]['arrAp'] = arr_ap
		sessionVar[0]['arrCc'] = arr_cc
		sessionVar[0]['arrEpi'] = arr_epi
		sessionVar[0]['arrIso'] = arr_iso
		sessionVar[0]['arrIsln'] = arr_isln
		sessionVar[0]['arrLoc'] = arr_loc
		sessionVar[0]['searchType'] = searchType

		sessionVar[0]['pageType'] = cl.SearchIsolateList


	else:
		print("No search variables found")
		raise Http404('No search variables found')


	print('orderBy ' + str(orderBy))
	print('dir ' + str(dir))
	print('searchType ' + str(searchType))


	json_sessionVar = json.dumps(sessionVar, cls=DjangoJSONEncoder)
	request.session['sessionVar'] = json_sessionVar

	print(json_sessionVar)

	########################



	# HEADERS
	if request.user.is_authenticated:


		(isoCount, isolates, dict_pageInfo, dict_mergedIds, list_colsInfo, list_tabAps, list_tabCcs, list_serverStatus, list_assignStatus, list_privStatus, boolChoices) = routeToRightRawQFn.getIsolatesFromRightFn(arr_ap, arr_cc, arr_epi, arr_loc, arr_isln, arr_iso, pageNumToGet, maxIsolatesPerPage, request.user.username, False, orderBy, dir, isCsv, isMgt9Ap, searchType, isMr)
		isolates = mergeCcOdc.get_merges(list_colsInfo, isolates)
	else:

		# print("is not authenticated")


		(isoCount, isolates, dict_pageInfo, dict_mergedIds, list_colsInfo, list_tabAps, list_tabCcs, list_serverStatus, list_assignStatus, list_privStatus, boolChoices) = routeToRightRawQFn.getIsolatesFromRightFn(arr_ap, arr_cc, arr_epi, arr_loc, arr_isln, arr_iso, pageNumToGet, maxIsolatesPerPage, None, False, orderBy, dir, isCsv, isMgt9Ap, searchType, isMr)
		isolates = mergeCcOdc.get_merges(list_colsInfo, isolates)


	if isMgt9Ap:
		print(len(isolates));
		(mgtId_ap9Id, dict_tabRows_byAp9Id, colNamesCombined) = mgt9Aps.getTheDataMgt9Aps(isolates, list_colsInfo, isGrapeTree)

		outstring = mgt9Aps.convertToCsv_ap9(isolates, mgtId_ap9Id, dict_tabRows_byAp9Id, colNamesCombined, isGrapeTree)

		#dict_ = dict()
		#dict_['isolates'] =  det.convertToJson(isolates)
		#dict_['list_colsInfo'] = list_colsInfo
		#dict_['mgtId_ap9Id'] = det.convertToJson(mgtId_ap9Id)
		#dict_['list_tabRows_byAp9Id'] = list_tabRows_byAp9Id
		# outstring = makeCsv(isolates,request.user.is_authenticated)
		# print(dict_)
		# return JsonResponse(dict_, safe=False)
		# print(outstring)
		return HttpResponse(outstring)


	isAp = True; isDst = False; isMgtColor = True;
	if 'isAp' in request.POST and request.POST['isAp'] == "false":
		isAp = False
	if 'isDst' in request.POST and request.POST['isDst'] == 'true':
		isDst = True
	if 'isMgtColor' in request.POST and request.POST['isMgtColor'] == 'false':
		isMgtColor = False

	# print("Value of isAp is " + str(isAp))

	mergedIds = det.convertToJson_dict(dict_mergedIds)

	# print(dict_mergedIds)

	if isMr:
		(outstring, resMr) = makeCsv_andSendToMr(isolates, request.user.is_authenticated, list_colsInfo)
		# outstring = makeCsv_microreact(isolates, request.user.is_authenticated, list_colsInfo)
		return JsonResponse({'outString': outstring, 'resMr': resMr})

	elif isCsv:
		# theCsvBuf = makeCsvString.convertToCsv(list_colsInfo, isolates)

		# return theCsvBuf

		outstring = makeCsv(isolates,request.user.is_authenticated, list_colsInfo)
		return HttpResponse(outstring)

	else:
		jsonIso = det.convertToJson(isolates)

		return render(request, 'Blankdb/isolateTable.html', {"isolates": jsonIso, "isoCount": isoCount, "pageInfo": dict_pageInfo, "isAp": isAp, 'isDst': isDst, 'isMgtColor': isMgtColor, "colsInfo": list_colsInfo, 'tabAps': list_tabAps, 'tabCcs': list_tabCcs, 'serverStatus': list_serverStatus, 'assignStatus': list_assignStatus, 'privStatus': list_privStatus, "mergedIds": mergedIds, "searchType": searchType, "boolChoices": boolChoices})
