from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json
from Blankdb.views.FuncsAuxAndDb import getHeaders, routeToRightRawQFn, mergeCcOdc
from Blankdb.models import View_apcc, Project
from itertools import *
from django.db import connections
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404, render
from Blankdb.views.FuncsAuxAndDb import dataExtractTransform as det
from Blankdb.views.FuncsAuxAndDb import queryDb
from Blankdb.views.FuncsAuxAndDb.makeCsvString import makeCsv
from Blankdb.views.FuncsAuxAndDb import constants as c
from Blankdb.views.FuncsAuxAndDb import constants_local as cl
from Blankdb.views.FuncsAuxAndDb import queryDb as q
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from types import MethodType
from Blankdb.views.FuncsAuxAndDb import getPoolOfCcMergeIds as getCcMergeIdsList
from django.db.models import Q
from Blankdb.views.FuncsAuxAndDb import sessionFns as ses
from Blankdb.views.FuncsAuxAndDb import mgt9Aps
from Blankdb.views.FuncsAuxAndDb.makeCsvString_mr import makeCsv_andSendToMr

@csrf_exempt
def page(request):
	# print("yes in this page...")
	if request.user.is_authenticated:
		isoInfo = det.convertToJson(c.IsolateHeaderPv)
		apHeader = getHeaders.getApHeaderAsJson()
		ccHeader = getHeaders.getCcHeaderAsJson()
		mgtInfo = det.convertToJson(c.MgtColsPv)
		epiInfo = getHeaders.getEpiHeaderAsJson()
		locInfo = det.convertToJson(c.IsoMetaLocInfoPv)
		islnInfo = det.convertToJson(c.IsoMetaIslnInfoPv)

	else:
		isoInfo = det.convertToJson(c.IsolateHeaderPu)
		apHeader = getHeaders.getApHeaderAsJson()
		ccHeader = getHeaders.getCcHeaderAsJson()
		mgtInfo = det.convertToJson(c.MgtColsPu)
		epiInfo = getHeaders.getEpiHeaderAsJson()
		locInfo = det.convertToJson(c.IsoMetaLocInfoPu)
		islnInfo = det.convertToJson(c.IsoMetaIslnInfoPu)





	sessionVar = list()

	pageNumToGet = 1
	orderBy = None
	dir = None

	isCsv = False
	isMgt9Ap = False
	maxIsolatesPerPage = c.TOTAL_ISO_PER_PAGE
	isGrapeTree = False
	isMr = False

	searchType = 'and';

	searchAp = []; searchCcEpi = []; searchLocs = []; searchIsln = []; searchProj = []; searchIso = [];


	if (('orderBy' in request.POST and len(request.POST['orderBy']) > 0) or ('pageNumToGet' in request.POST and len(request.POST['pageNumToGet']) > 0)) or ('isCsv' in request.POST and request.POST['isCsv'] == 'true') or ('isMgt9Ap' in request.POST and request.POST['isMgt9Ap'] == 'true') or ('isMr' in request.POST and request.POST['isMr'] == 'true'):

		sessionVar_json = request.session['sessionVar']
		sessionVar = json.loads(sessionVar_json)

		if sessionVar[0]['pageType'] != cl.SearchIsolateDetail:
			raise Http404()

		(searchAp, searchCcEpi, searchLocs, searchIsln, searchProj, searchIso) = ses.loadSessionSearchVars_detail(sessionVar)



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
			# print("Over here...? 33333333333333")
			# print (request.POST)
			isMgt9Ap = True
			maxIsolatesPerPage = c.TOTAL_MGT9_ISO_DOWNLOAD

			if ('isGrapeTree' in request.POST and request.POST['isGrapeTree'] == 'true'):
				isGrapeTree = True


	elif ses.isASearchPresent_detail(request.POST):
		# a new search has been initiated
		sessionVar.append(dict())

		(searchAp, searchCcEpi, searchLocs, searchIsln, searchProj, searchIso) = loadRequestSearchVars_detail(request.POST)

		sessionVar[0]['json_apSearchTerms'] = searchAp
		sessionVar[0]['json_ccEpiSearchTerms'] = searchCcEpi
		sessionVar[0]['json_location'] = searchLocs
		sessionVar[0]['json_isolation'] = searchIsln
		sessionVar[0]['json_project'] = searchProj
		sessionVar[0]['json_iso'] = searchIso
		sessionVar[0]['pageType'] = cl.SearchIsolateDetail

	else:
		raise Http404('Search variables not found!')

	json_sessionVar = json.dumps(sessionVar, cls=DjangoJSONEncoder)
	request.session['sessionVar'] = json_sessionVar


	# print("updated version")
	# print (searchVar)
	###########################




	# print("arr loc is!")
	# print(arr_loc)


	if request.user.is_authenticated:
		(arr_ap, arr_ccEpi, arr_loc, arr_isln, arr_iso) = ses.convertToArrs_searchIsoDetail(searchAp, searchCcEpi, searchLocs, searchIsln, searchProj, searchIso, request.user.username)

		(isoCount, isolates, dict_pageInfo, dict_mergedIds, list_colsInfo, list_tabAps, list_tabCcs, list_serverStatus, list_assignStatus, list_privStatus, boolChoices) = routeToRightRawQFn.getIsolatesFromRightFn(arr_ap, arr_ccEpi, [], arr_loc, arr_isln, arr_iso, pageNumToGet, maxIsolatesPerPage, request.user.username, True, orderBy, dir, isCsv,isMgt9Ap, searchType, isMr)
		isolates = mergeCcOdc.get_merges(list_colsInfo, isolates)
	else:
		(arr_ap, arr_ccEpi, arr_loc, arr_isln, arr_iso) = ses.convertToArrs_searchIsoDetail(searchAp, searchCcEpi, searchLocs, searchIsln, searchProj, searchIso, None)

		(isoCount, isolates, dict_pageInfo, dict_mergedIds, list_colsInfo, list_tabAps, list_tabCcs, list_serverStatus, list_assignStatus, list_privStatus, boolChoices) = routeToRightRawQFn.getIsolatesFromRightFn([searchAp], [searchCcEpi], [], [searchLocs], [searchIsln], [searchIso], pageNumToGet, maxIsolatesPerPage, None, None, orderBy, dir, isCsv,isMgt9Ap, searchType, isMr)
		isolates = mergeCcOdc.get_merges(list_colsInfo, isolates)

	if isMgt9Ap:
		# get the data
		print("The isGrapeTree is " + str(isGrapeTree))
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


	mergedIds = det.convertToJson_dict(dict_mergedIds)



	isAp = True; isDst = False; isMgtColor = True;
	if 'isAp' in request.POST and request.POST['isAp'] == "false":
		isAp = False
	if 'isDst' in request.POST and request.POST['isDst'] == 'true':
		isDst = True
	if 'isMgtColor' in request.POST and request.POST['isMgtColor'] == 'false':
		isMgtColor = False

	if isMr:

		# theCsvBuf = makeCsvString.convertToCsv(list_colsInfo, isolates)
		# return theCsvBuf
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

		outdata = {"isolates": jsonIso, "isoCount": isoCount, "pageInfo": dict_pageInfo, "isAp": isAp, 'isDst':isDst, 'isMgtColor': isMgtColor, "mergedIds": mergedIds, "colsInfo": list_colsInfo, 'tabAps': list_tabAps, 'tabCcs': list_tabCcs, 'serverStatus': list_serverStatus, 'assignStatus': list_assignStatus, 'privStatus': list_privStatus, "mergedIds": mergedIds, "boolChoices": boolChoices}

		#  "colIsoId": c.IsolateId, "isoInfo": isoInfo, "apInfo": apHeader, "ccInfo": ccHeader, "mgtInfo": mgtInfo, "epiInfo": epiInfo, "locInfo": locInfo, "islnInfo": islnInfo,
		return render(request, 'Blankdb/isolateTable.html', outdata)


def loadRequestSearchVars_detail(requestVar):
	searchAp = json.loads(requestVar['json_apSearchTerms'])
	searchCcEpi = json.loads(requestVar['json_ccEpiSearchTerms'])
	searchLocs = json.loads(requestVar['json_location'])
	searchIsln = json.loads(requestVar['json_isolation'])
	searchProj = json.loads(requestVar['json_project'])
	searchIso = json.loads(requestVar['json_iso'])


	return (searchAp, searchCcEpi, searchLocs, searchIsln, searchProj, searchIso)
