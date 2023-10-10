from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
# from ..FuncsAuxAndDb import getHeaders
from itertools import *
from django.db import connections
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404, render
import importlib
from ..FuncsAuxAndDb import getHeaders
from ..FuncsAuxAndDb import dataExtractTransform as det
from ..FuncsAuxAndDb import constants as c
from ..FuncsAuxAndDb import constants_local as cl
from ..FuncsAuxAndDb import queryDb as q
# from Salmonella.models import View_apcc, Isolate, Location

import importlib

from django.db.models import Count

@csrf_exempt
def page(request, org):
	View_apcc, Isolate, Location = getModels(org)

	tn = request.POST['tn']
	# tn = tn + "_st"
	# print(tn)
	# print("here!!")
	# tableClass = None

	# all, top5 by continent

 	# for isolate, top 5 sts by continent

	# top5_overall = q.getTop5St(tn);


	# print(top5_overall)

	top5_byContinent = q.getTop5StByContinet(tn, org)
	Col_count = 1
	Col_continent = 2
	Col_st = 3

	list_forJs = list()
	for eachTup in top5_byContinent:
		list_forJs.append({'count': eachTup[Col_count], 'continent': eachTup[Col_continent], 'st': eachTup[Col_st]})

	continents = Location.objects.exclude(continent__isnull=True).values('continent').distinct()
	# continents = Location.objects.values('continent').distinct() # excluding unknown continents

	isoCountByLoc_expanded = Isolate.objects.filter(location__continent__in=continents).values('location__continent').annotate(Count('location'))

	isoCountByLocTot = dict()
	for qs in isoCountByLoc_expanded:
		# print(qs)
		isoCountByLocTot[qs['location__continent']] = qs['location__count']
		# print("here!")

	#continentCounts = Isolate.objects.values('')
	#isoCount = [{'isoCount': Isolate.objects.count()}]
	isoCountByLocTot = [[isoCountByLocTot]]

	isoCountByLocTot.append(list_forJs)

	# print(top5_byContinent)
	# top5_js = dict(top5_byContinent)

	# print(top5_js)
	############################

	# print(isoCountByLocTot)
	return JsonResponse(isoCountByLocTot, safe=False)

def getModels(org):
    models = importlib.import_module(f'{org}.models')
    View_apcc = models.View_apcc
    Isolate = models.Isolate
    Location = models.Location
    
    return View_apcc, Isolate, Location