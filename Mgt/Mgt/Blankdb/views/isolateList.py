from django.views.generic import CreateView
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django import forms
from django.http import HttpResponse, HttpResponseServerError
from Blankdb.models import Isolate, View_apcc, Tables_ap
from django.forms.models import model_to_dict
# from . import hgt_db_functions
from operator import attrgetter
from itertools import chain
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
import json
from Blankdb.views.FuncsAuxAndDb import getHeaders
from Blankdb.views.FuncsAuxAndDb import dataExtractTransform as det
from Blankdb.views.FuncsAuxAndDb import constants as c
from Blankdb.views.FuncsAuxAndDb.routeToRightRawQFn import isolateChoices
from itertools import *
from django.db import connections
from Blankdb.views.FuncsAuxAndDb import columns



def page(request):

	if request.user.is_authenticated:
		isoInfo = det.convertToJson(c.IsolateHeaderPv)
		apHeader = getHeaders.getApHeaderAsJson()
		ccHeader = getHeaders.getCcHeaderAsJson()
		epiInfo = getHeaders.getEpiHeaderAsJson()
		locInfo = det.convertToJson(c.IsoMetaLocInfoPv)
		islnInfo = det.convertToJson(c.IsoMetaIslnInfoPv)
	else:
		isoInfo = det.convertToJson(c.IsolateHeaderPu)
		apHeader = getHeaders.getApHeaderAsJson()
		ccHeader = getHeaders.getCcHeaderAsJson()
		epiInfo = getHeaders.getEpiHeaderAsJson()
		locInfo = det.convertToJson(c.IsoMetaLocInfoPu)
		islnInfo = det.convertToJson(c.IsoMetaIslnInfoPu)

	(list_cols, list_tabAps, list_tabCcs) = columns.columns(request.user.is_authenticated)

	(list_serverStatus, list_assignStatus, list_privStatus, boolChoices) = isolateChoices()



	# context['countries'] = list(countries)

	# print ('This is the isoInfo')
	# print(list_cols)

	return render(request, 'Blankdb/isolateList.html', {"isoHeader": isoInfo, "apHeader": apHeader, "ccHeader": ccHeader, "epiHeader": epiInfo, "locHeader": locInfo, "islnHeader": islnInfo, "dirColsInfo": list_cols, "dirAps": list_tabAps, "dirCcs": list_tabCcs, "serverStatusChoices": list_serverStatus, "assignStatusChoices": list_assignStatus, "privStatusChoices": list_privStatus, 'boolChoices': boolChoices})
