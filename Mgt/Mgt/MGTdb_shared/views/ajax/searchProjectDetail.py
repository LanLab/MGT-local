from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import json
import importlib
from ..FuncsAuxAndDb import getHeaders, routeToRightRawQFn, mergeCcOdc
# from Salmonella.models import View_apcc, Project, User
from itertools import *
from django.db import connections
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404, render
from ..FuncsAuxAndDb import dataExtractTransform as det
from ..FuncsAuxAndDb import constants as c
from ..FuncsAuxAndDb import constants_local as cl
from ..FuncsAuxAndDb import sessionFns as ses
from ..FuncsAuxAndDb.makeCsvString import makeCsv
from ..FuncsAuxAndDb import queryDb as q
from ..FuncsAuxAndDb import getPoolOfCcMergeIds as getCcMergeIdsList
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from types import MethodType
from django.db.models import Q
import re
from ..FuncsAuxAndDb import mgt9Aps
from ..FuncsAuxAndDb.makeCsvString_mr import makeCsv_andSendToMr

@csrf_exempt
def page(request, org):
	View_apcc, Project, User = getModels(org)
	print(org)
	if not request.user.is_authenticated:
		raise Http404("You need to log in to view this page!")

	else:
		isoInfo = det.convertToJson(c.IsolateHeaderPv)
		apHeader = getHeaders.getApHeaderAsJson(org)
		ccHeader = getHeaders.getCcHeaderAsJson(org)
		mgtInfo = det.convertToJson(c.MgtColsPv)
		epiInfo = getHeaders.getEpiHeaderAsJson(org)
		locInfo = det.convertToJson(c.IsoMetaLocInfoPv)
		islnInfo = det.convertToJson(c.IsoMetaIslnInfoPv)

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
		# get variables from session
		sessionVar_json = request.session['sessionVar']
		sessionVar = json.loads(sessionVar_json)

		if sessionVar[0]['pageType'] != cl.SearchProjectDetail:
			raise Http404()


		(arr_ap, arr_cc, arr_epi, arr_iso, arr_isln, arr_loc, searchType) = ses.loadSessionSearchVars(sessionVar)
		projectId = sessionVar[0]['projectId']

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

		if ('isMgt9Ap' in request.POST and request.POST['isMgt9Ap'] == 'true'):
			# print("Over here...? 33333333333333")
			isMgt9Ap = True
			maxIsolatesPerPage = c.TOTAL_MGT9_ISO_DOWNLOAD

			if ('isGrapeTree' in request.POST and request.POST['isGrapeTree'] == 'true'):
				isGrapeTree = True

		if ('isMr' in request.POST and request.POST['isMr'] == 'true'):
			isMr = True;


	elif 'projectId' in request.POST and len(request.POST['projectId']) > 0  and ses.isASearchPresent(request.POST):
		# a new search has been initiated
		sessionVar.append(dict())

		(arr_ap, arr_cc, arr_epi, arr_iso, arr_isln, arr_loc, projectId, searchType) = ses.loadRequestSearchVars_proj(request.POST) # adds project id to arr_iso

		sessionVar[0]['arrAp'] = arr_ap
		sessionVar[0]['arrCc'] = arr_cc
		sessionVar[0]['arrEpi'] = arr_epi
		sessionVar[0]['arrIso'] = arr_iso
		sessionVar[0]['arrIsln'] = arr_isln
		sessionVar[0]['arrLoc'] = arr_loc
		sessionVar[0]['projectId'] = projectId
		sessionVar[0]['searchType'] = searchType


		sessionVar[0]['pageType'] = cl.SearchProjectDetail

	else:
	 	raise Http404("Desired vars not in search")

	# CHECK! if use has the right access rights

	if not Project.objects.filter(id=int(projectId),user=User.objects.get(userId=request.user)).exists():
		return Http404("Error: you dont have permission to access this page!")



	json_sessionVar = json.dumps(sessionVar, cls=DjangoJSONEncoder)
	request.session['sessionVar'] = json_sessionVar

	#########################

	isAp = True; isDst = False; isMgtColor = True;
	if 'isAp' in request.POST and request.POST['isAp'] == "false":
		isAp = False
	if 'isDst' in request.POST and request.POST['isDst'] == 'true':
		isDst = True
	if 'isMgtColor' in request.POST and request.POST['isMgtColor'] == 'false':
		isMgtColor = False


	(isoCount, isolates, dict_pageInfo, dict_mergedIds, list_colsInfo, list_tabAps, list_tabCcs, list_serverStatus, list_assignStatus, list_privStatus, boolChoices) = routeToRightRawQFn.getIsolatesFromRightFn(arr_ap, arr_cc, arr_epi, arr_loc, arr_isln, arr_iso, pageNumToGet, maxIsolatesPerPage, request.user.username, True, orderBy, dir, isCsv,isMgt9Ap, searchType, isMr, org)
	isolates = mergeCcOdc.get_merges(list_colsInfo, isolates, org)


	if isMgt9Ap:
		# get the data
		(mgtId_ap9Id, dict_tabRows_byAp9Id, colNamesCombined) = mgt9Aps.getTheDataMgt9Aps(isolates, list_colsInfo, isGrapeTree, org)

		outstring = mgt9Aps.convertToCsv_ap9(isolates, mgtId_ap9Id, dict_tabRows_byAp9Id, colNamesCombined, isGrapeTree, org)

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


	if isMr:

		# theCsvBuf = makeCsvString.convertToCsv(list_colsInfo, isolates)
		# return theCsvBuf
		(outstring, resMr) = makeCsv_andSendToMr(isolates, request.user.is_authenticated, list_colsInfo, org)
		# outstring = makeCsv_microreact(isolates, request.user.is_authenticated, list_colsInfo)
		return JsonResponse({'outString': outstring, 'resMr': resMr})


	elif isCsv:
		# theCsvBuf = makeCsvString.convertToCsv(list_colsInfo, isolates)

		# return theCsvBuf

		outstring = makeCsv(isolates,request.user.is_authenticated, list_colsInfo, org)
		return HttpResponse(outstring)
	else:
		jsonIso = det.convertToJson(isolates)

		return render(request, 'Templates/isolateTable.html', {"isolates": jsonIso, "IsolateId": c.IsolateId, "isAp": isAp, 'isDst': isDst, 'isMgtColor': isMgtColor, "isoCount": isoCount,  "pageInfo": dict_pageInfo, "mergedIds": mergedIds,  "colsInfo": list_colsInfo, 'tabAps': list_tabAps, 'tabCcs': list_tabCcs, 'serverStatus': list_serverStatus, 'assignStatus': list_assignStatus, 'privStatus': list_privStatus, "boolChoices": boolChoices, 'organism': org})

#################
def getModels(org):
    models = importlib.import_module(f'{org}.models')
    View_apcc = models.View_apcc 
    Project = models.Project 
    User = models.User
    
    return View_apcc, Project, User