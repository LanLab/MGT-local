from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponseNotFound
from Blankdb.models import Isolate, Location, Isolation, View_apcc, Project
from Blankdb.views.FuncsAuxAndDb import getHeaders
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from Blankdb.views.FuncsAuxAndDb import dataExtractTransform as det
from Blankdb.views.FuncsAuxAndDb import constants as c
from Blankdb.views.FuncsAuxAndDb import queryDb as q
from Blankdb.views.FuncsAuxAndDb import routeToRightRawQFn as routeToFnAuth


def page(request, pk):



	userProjIds = list()

	if request.user.is_authenticated:
		isoInfo = det.convertToJson(c.IsolateHeaderPv)
		apHeader = getHeaders.getApHeaderAsJson()
		ccHeader = getHeaders.getCcHeaderAsJson()
		epiInfo = getHeaders.getEpiHeaderAsJson()
		locInfo = det.convertToJson(c.IsoMetaLocInfoPv)
		islnInfo = det.convertToJson(c.IsoMetaIslnInfoPv)
		projHeader = det.convertToJson(c.ProjHeaderPv)
		userProjIds = q.getUserProjectIds(request.user.username)

	else:
		isoInfo = det.convertToJson(c.IsolateHeaderPu)
		apHeader = getHeaders.getApHeaderAsJson()
		ccHeader = getHeaders.getCcHeaderAsJson()
		epiInfo = getHeaders.getEpiHeaderAsJson()
		locInfo = det.convertToJson(c.IsoMetaLocInfoPu)
		islnInfo = det.convertToJson(c.IsoMetaIslnInfoPu)
		projHeader = []

	# check pk refers to public strain, then return.

	isolate = None
	isoMgt = None
	json_isoMgt = {}
	isUserIso = False

	try:
		isolate = Isolate.objects.get(pk=pk)
	except Isolate.DoesNotExist:
		raise Http404("Isolate does not exist")

	theIsolate = None
	list_colsInfo = None
	list_tabAps = None
	list_tabCcs = None
	list_serverStatus = None
	list_assignStatus = None
	list_privStatus = None

	# if isolate.server_status == 'C' and isolate.assignment_status == 'A':
		# print(str(isolate) + " !!")
		# isoMgt = View_apcc.objects.get(mgt_id=isolate.mgt)
		# calling a subfunction of routeToRightFnAuth in hacky way ...
	(isoCount, theIsolate, dict_pageInfo, dict_mergedIds, list_colsInfo, list_tabAps, list_tabCcs, list_serverStatus, list_assignStatus, list_privStatus, boolChoices) = routeToFnAuth.getIsolatesFromRightFn([], [], [], [], [], [{'id': str(isolate.id)}], 1, 20, request.user.username, False, '', '', False, False, 'and', False)
		# print(" the information identified here is ... ")
		# print(request.user.username)
		# print(isoCount)
		# print(isolates)
	if isoMgt:
		json_isoMgt = serializers.serialize('json', [isoMgt], default=json_util.default)



	project = None
	if len(userProjIds) > 0:
		if isolate.project_id in userProjIds:
			isUserIso = True
			project = Project.objects.get(pk=isolate.project_id)


	# locFields = [f.name for f in Location._meta.get_fields()]
	# islnFields = [f.name for f in Isolation._meta.get_fields()]




	return render(request, 'Blankdb/isolateDetail.html', {"isolate": isolate, "projHeader": projHeader, "isUserIso": isUserIso, 'project': project, 'theIsolateJson': json.dumps(theIsolate, cls=DjangoJSONEncoder), 'colsInfo': list_colsInfo, "tabAps": list_tabAps, "tabCcs": list_tabCcs, "serverStatusChoices": list_serverStatus, 'assignStatusChoices': list_assignStatus, 'privStatusChoices': list_privStatus, 'boolChoices': boolChoices}) # {"isolate": isolate, "json_isoHgt": json_isoMgt }) # }) #  "similar_strains": qs_similarAps},)
