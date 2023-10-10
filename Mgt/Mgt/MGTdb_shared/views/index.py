from django.shortcuts import render
import importlib
# from Salmonella.models import Isolate, Reference, Tables_ap
from .FuncsAuxAndDb import getHeaders
from django.conf import settings
import glob
# Create your views here.

def page(request, org):
	Isolate, Reference, Tables_ap = getModels(org)
	print('THIS HAS TO BE THE ORG: ', org)

	# print(Isolate, Reference)
	print('this is the organism:', org)
 
	try:
		isoCount = Isolate.objects.filter(privacy_status="PU").count()
	except:
		isoCount = 0

	try:
		isoCount_assigned = Isolate.objects.filter(privacy_status="PU", server_status="C", assignment_status="A").count()
	except:
		isoCount_assigned = 0

	try:
		organism = Reference.objects.all()[0].organism # getting the first one's name
		request.session['organism'] = organism
	except:
		request.session['organism'] = "Organism"

	try:
		mgts = getHeaders.getApHeaderAsJson(org)
	except:
		mgts = None

	dict_fns = getPuFnsForDwnld(org)

	return render(request, f"Templates/index.html", {"isoCount": isoCount, "isoCount_assigned": isoCount_assigned, "mgts": mgts, "downloadFns": dict_fns, "organism": org})

    
def getPuFnsForDwnld(org): 
	Isolate, Reference, Tables_ap = getModels(org)
	dir_filesForDownload = getattr(settings,'FILES_FOR_DOWNLOAD')

	dict_fns = {} # dict_{aps|alleles} => [fn1, fn2, fn3, ... fnN]

	appName = Isolate._meta.app_label # + "/" +

	dict_fns['aps'] = glob.glob(dir_filesForDownload + appName + "_aps_[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].txt.tar.gz")
	dict_fns['alleles'] = glob.glob(dir_filesForDownload +  appName + "*_alleles_*")

	# print(dir_filesForDownload)
	# print (dict_fns)


	return dict_fns

# Get models from species 
def getModels(organism):
    models = importlib.import_module(f'{organism}.models')
    Isolate = models.Isolate
    Reference = models.Reference 
    Tables_ap = models.Tables_ap
    
    return Isolate, Reference, Tables_ap
