from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import importlib
from ..FuncsAuxAndDb import sessionFns as ses
from ..FuncsAuxAndDb import routeToRightRawQFn_graph as routerGraph
from ..FuncsAuxAndDb import constants_local as cl
from ..FuncsAuxAndDb import dataExtractTransform as det
# from Salmonella.models import Project, User
from django.http import Http404

@csrf_exempt
def page(request, org):
	Project, User = getModels(org)
	# print(request.session['sessionVar'])
	print(org)

	if 'sessionVar' in request.session:


		sessionVar_json = request.session['sessionVar'];
		sessionVar = json.loads(sessionVar_json)

        print("In the mgtbreakdown page");
		print(sessionVar);

		# print(sessionVar[0]['pageType'])


		if (sessionVar[0]['pageType'] == cl.InitialIsolates or sessionVar[0]['pageType'] == cl.InitialProjIsolates or sessionVar[0]['pageType'] == cl.SearchIsolateDetail or sessionVar[0]['pageType'] == cl.SearchIsolateList or sessionVar[0]['pageType'] == cl.SearchProjectDetail):



			# if isAuth.

			isolates_bg = None; columns_bg = None;


			if request.user.is_authenticated and (sessionVar[0]['pageType'] == cl.InitialIsolates or sessionVar[0]['pageType'] == cl.SearchIsolateList or sessionVar[0]['pageType'] == cl.SearchIsolateDetail): # include user isolates (no bg strains)

				print ("no bg strains, do a union " );

				if (sessionVar[0]['pageType'] == cl.SearchIsolateDetail):
					(searchAp, searchCcEpi, searchLocs, searchIsln, searchProj, searchIso) = ses.loadSessionSearchVars_detail(sessionVar)

					(arr_ap, arr_cc, arr_loc, arr_isln, arr_iso) = ses.convertToArrs_searchIsoDetail(searchAp, searchCcEpi, searchLocs, searchIsln, searchProj, searchIso, request.user.username, org)
					print('Over here!');
					print(arr_loc);

					arr_epi = []

				else:
					(arr_ap, arr_cc, arr_epi, arr_iso, arr_isln, arr_loc, searchType) = ses.loadSessionSearchVars(sessionVar)

				# print(arr_loc);


				(isolates, columns) = routerGraph.getDataFromRightFn(arr_ap, arr_cc, arr_epi, arr_loc, arr_isln, arr_iso, request.user.username, False, None, searchType, org)


			elif request.user.is_authenticated or sessionVar[0]['pageType'] == cl.InitialProjIsolates or sessionVar[0]['pageType'] == cl.SearchProjectDetail: # show/hide bg strains
				print("Is auth && bg strains ")

				projectId = None;

				(arr_ap, arr_cc, arr_epi, arr_iso, arr_isln, arr_loc, projectId, searchType) = ses.loadSessionSearchVars_proj(sessionVar)

				if (sessionVar[0]['pageType'] == cl.InitialProjIsolates or sessionVar[0]['pageType'] == cl.SearchProjectDetail) and (not projectId or not  Project.objects.filter(id=int(projectId),user=User.objects.get(userId=request.user)).exists()):
					print("This error here??");
					raise Http404("Error: you dont have permission to access this page!")
				dict_ = dict();
				dict_['project'] = projectId
				arr_iso.append(dict_)

				# print("The project id " + str(projectId))
				(isolates, columns) = routerGraph.getDataFromRightFn(arr_ap, arr_cc, arr_epi, arr_loc, arr_isln, arr_iso, request.user.username, True, None, searchType, org)

				(arr_iso_noProj, projIds) = rmProjFromArrIso(arr_iso); print(projIds[0]);
				print("The proj ids are: ")
				print(projIds);

				(isolates_bg, columns_bg) = routerGraph.getDataFromRightFn(arr_ap, arr_cc, arr_epi, arr_loc, arr_isln, arr_iso_noProj, None, False, projIds, searchType, org)

				print ("The bg strains are: ")
				print (isolates_bg)
				print(columns_bg)


			# else: not logged in
			else:

				if (sessionVar[0]['pageType'] == cl.SearchIsolateDetail):
					searchType = 'and'
					(searchAp, searchCcEpi, searchLocs, searchIsln, searchProj, searchIso) = ses.loadSessionSearchVars_detail(sessionVar)

					(arr_ap, arr_cc, arr_loc, arr_isln, arr_iso) = ses.convertToArrs_searchIsoDetail(searchAp, searchCcEpi, searchLocs, searchIsln, searchProj, searchIso, None, org)

					arr_epi = []
				else:
					(arr_ap, arr_cc, arr_epi, arr_iso, arr_isln, arr_loc, searchType) = ses.loadSessionSearchVars(sessionVar)

				# print("The project id " + str(projectId))
				(isolates, columns) = routerGraph.getDataFromRightFn(arr_ap, arr_cc, arr_epi, arr_loc, arr_isln, arr_iso, None, False, None, searchType, org)

			print(columns)
			isolates.insert(0, columns);
			dataToSend = {'data': isolates}

			if columns_bg or isolates_bg:
				isolates_bg.insert(0, columns_bg);
				dataToSend['background'] = isolates_bg;

			jsonIso = det.convertToJson_dict(dataToSend)
			# print(jsonIso);
	return JsonResponse(jsonIso, safe=False);


def rmProjFromArrIso(arr_iso):

	arr_iso_noProj = [];
	projIds = [];
	for anObj in arr_iso:
		print (anObj);

		if 'project' not in anObj:
			arr_iso_noProj.append(anObj);
		else:
			projIds.append(anObj['project'])

	return (arr_iso_noProj, projIds);

def getModels(organism):
    models = importlib.import_module(f'{organism}.models') 
	Project = models.Project
	User = models.User

	return Project, User