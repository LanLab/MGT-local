from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from Blankdb.views.FuncsAuxAndDb import getHeaders, routeToRightRawQFn, mergeCcOdc
from Blankdb.models import View_apcc
from itertools import *
from django.db import connections
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from functools import reduce
import operator
from Blankdb.views.FuncsAuxAndDb import getHeaders
from Blankdb.views.FuncsAuxAndDb import dataExtractTransform as det
from Blankdb.views.FuncsAuxAndDb import constants as c
from Blankdb.views.FuncsAuxAndDb import constants_local as cl
from Blankdb.views.FuncsAuxAndDb import queryDb as q
from Blankdb.views.FuncsAuxAndDb.makeCsvString import makeCsv
from Blankdb.views.FuncsAuxAndDb import ownPaginator as ownPaginator
from Blankdb.views.FuncsAuxAndDb import sessionFns as ses
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from types import MethodType
from django.contrib.auth.decorators import login_required
from Blankdb.models import Project, User
from django.http import Http404
import re
from Blankdb.views.FuncsAuxAndDb import mgt9Aps
from Blankdb.views.FuncsAuxAndDb.makeCsvString_mr import makeCsv_andSendToMr


@csrf_exempt
@login_required
def page(request):
	# print("over here .... :)")
	# print(request.POST['isAp'])

	if not request.user.is_authenticated:
		raise Http404("You need to log in to view this page!")


	if request.user.is_authenticated:
		isoInfo = det.convertToJson(c.IsolateHeaderPv)
		apHeader = getHeaders.getApHeaderAsJson()
		ccHeader = getHeaders.getCcHeaderAsJson()
		mgtInfo = det.convertToJson(c.MgtColsPv)
		epiInfo = getHeaders.getEpiHeaderAsJson()
		locInfo = det.convertToJson(c.IsoMetaLocInfoPv)
		islnInfo = det.convertToJson(c.IsoMetaIslnInfoPv)

	sessionVar = list()

	# resent searchVar (only check if pageNumToGet or OrderBy is provided)
	pageNumToGet = 1
	orderBy = None
	dir = None
	projectId = None

	isCsv = False
	isMgt9Ap = False
	isGrapeTree = False
	maxIsolatesPerPage = c.TOTAL_ISO_PER_PAGE
	isMr = False

	searchType = 'and';

		# print("Come on over here.." + projectId)

	if (('orderBy' in request.POST and len(request.POST['orderBy']) > 0) or ('pageNumToGet' in request.POST and len(request.POST['pageNumToGet']) > 0)) or ('isCsv' in request.POST and request.POST['isCsv'] == 'true') or ('isMgt9Ap' in request.POST and request.POST['isMgt9Ap'] == 'true')  or ('isMr' in request.POST and request.POST['isMr'] == 'true'):

		# session var should be reused and updated
		sessionVar_json = request.session['sessionVar']
		sessionVar = json.loads(sessionVar_json)

		if sessionVar[0]['pageType'] != cl.InitialProjIsolates:
			raise Http404()

		projectId = sessionVar[0]['projectId']

		if 'orderBy' in request.POST and len(request.POST['orderBy']) > 0:
			orderBy = request.POST['orderBy']
			dir = request.POST['dir']

			print(orderBy + " . ... . " + dir)
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


	elif 'projectId' in request.POST:
		# session var is new.
		sessionVar.append(dict())

		projectId = json.loads(request.POST['projectId'])


		# update session
		sessionVar[0]['projectId'] = projectId
		sessionVar[0]['pageType'] = cl.InitialProjIsolates


	else:
		raise Http404()

	# CHECK! if use has the right access rights

	if not Project.objects.filter(id=int(projectId),user=User.objects.get(userId=request.user)).exists():
		return Http404("Error: you dont have permission to access this page!")


	json_sessionVar = json.dumps(sessionVar, cls=DjangoJSONEncoder)
	request.session['sessionVar'] = json_sessionVar


	# get the isolates
	(isoCount, isolates, dict_pageInfo, dict_mergedIds, list_colsInfo, list_tabAps, list_tabCcs, list_serverStatus, list_assignStatus, list_privStatus, boolChoices) = routeToRightRawQFn.getIsolatesFromRightFn([], [], [], [], [], [{'project': projectId}], pageNumToGet, maxIsolatesPerPage, request.user.username, True, orderBy, dir, isCsv,isMgt9Ap, searchType, isMr)
	isolates = mergeCcOdc.get_merges(list_colsInfo, isolates)



	if isMgt9Ap:
		# get the data
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



	mergedIds = det.convertToJson_dict(dict_mergedIds)


	if isMr:

		# theCsvBuf = makeCsvString.convertToCsv(list_colsInfo, isolates)
		# return theCsvBuf
		(outstring, resMr) = makeCsv_andSendToMr(isolates, request.user.is_authenticated, list_colsInfo)
		# outstring = makeCsv_microreact(isolates, request.user.is_authenticated, list_colsInfo)
		return JsonResponse({'outString': outstring, 'resMr': resMr})



	elif isCsv:
		outstring = makeCsv(isolates,request.user.is_authenticated, list_colsInfo)
		return HttpResponse(outstring)

		# theCsvRsp = makeCsvString.convertToCsv(list_colsInfo, isolates)
		# return theCsvRsp
	else:

		isolatesjson = det.convertToJson(isolates)

		return render(request, 'Blankdb/isolateTable.html', {"isolates": isolatesjson, "isoCount": isoCount, "pageInfo": dict_pageInfo, "isAp": isAp, 'isDst': isDst, 'isMgtColor': isMgtColor, "colsInfo": list_colsInfo, 'tabAps': list_tabAps, 'tabCcs': list_tabCcs, 'serverStatus': list_serverStatus, 'assignStatus': list_assignStatus, 'privStatus': list_privStatus, "mergedIds": mergedIds, 'boolChoices': boolChoices })
