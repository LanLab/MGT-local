from django.shortcuts import render
from Blankdb.models import Isolate, Reference, Tables_ap
from Blankdb.views.FuncsAuxAndDb import getHeaders
from django.conf import settings
import glob
# Create your views here.


def page(request):

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
		mgts = getHeaders.getApHeaderAsJson()
	except:
		mgts = None


	dict_fns = getPuFnsForDwnld()

	return render(request, "Blankdb/index.html", {"isoCount": isoCount, "isoCount_assigned": isoCount_assigned, "mgts": mgts, "downloadFns": dict_fns})


def getPuFnsForDwnld():
	dir_filesForDownload = getattr(settings,'FILES_FOR_DOWNLOAD')

	dict_fns = {} # dict_{aps|alleles} => [fn1, fn2, fn3, ... fnN]

	appName = Isolate._meta.app_label # + "/" +

	dict_fns['aps'] = glob.glob(dir_filesForDownload + appName + "_aps_[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].txt.tar.gz")
	dict_fns['alleles'] = glob.glob(dir_filesForDownload +  appName + "*_alleles_*")

	# print(dir_filesForDownload)
	# print (dict_fns)


	return dict_fns
