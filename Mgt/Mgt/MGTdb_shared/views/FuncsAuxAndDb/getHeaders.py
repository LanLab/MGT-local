# from Salmonella.models import Isolate, View_apcc, Tables_ap, Tables_cc
import json
import importlib
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connections
from . import constants as c

def getApHeaderAsJson(org):
	Isolate, View_apcc, Tables_ap, Tables_cc = getModels(org)
	qs_tablesAp = Tables_ap.objects.filter(table_num=0).order_by('display_order').values('table_name', 'scheme__display_name')
	json_tablesAp = json.dumps(list(qs_tablesAp), cls=DjangoJSONEncoder)

	return json_tablesAp


def getCcHeaderAsJson(org):
	Isolate, View_apcc, Tables_ap, Tables_cc = getModels(org)
	qs_tablesCc = Tables_cc.objects.filter(display_table=1).values('table_name', 'display_name').order_by('display_order')
	json_tablesCc = json.dumps(list(qs_tablesCc), cls=DjangoJSONEncoder)

	return json_tablesCc


def getEpiHeaderAsJson(org):
	Isolate, View_apcc, Tables_ap, Tables_cc = getModels(org)
	qs_tablesEpi = Tables_cc.objects.filter(display_table=2).values('table_name', 'display_name').order_by('display_order')
	json_tablesEpi = json.dumps(list(qs_tablesEpi), cls=DjangoJSONEncoder)

	return json_tablesEpi


def getIsoHeaderAsJson():
	json_iso = json.dumps(c.IsolateHeaderPu, cls=DjangoJSONEncoder)
	return json_iso

def getIsoMLocHeaderAsJson():
	json_isoMLoc = json.dumps(c.IsoMetaLocInfo, cls=DjangoJSONEncoder)
	return json_isoMLoc

def getIsoMIslnHeaderAsJson():
	json_isoMIsln = json.dumps(c.IsoMetaIslnInfo, cls=DjangoJSONEncoder)

	return json_isoMIsln

def getModels(org):
    models = importlib.import_module(f'{org}.models')
    Isolate = models.Isolate
    View_apcc = models.View_apcc
    Tables_ap = models.Tables_ap
    Tables_cc = models.Tables_cc
    
    return Isolate, View_apcc, Tables_ap, Tables_cc