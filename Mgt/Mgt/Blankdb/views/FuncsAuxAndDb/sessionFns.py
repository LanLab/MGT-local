import json
from Blankdb.models import Project
from Blankdb.views.FuncsAuxAndDb import routeToRightRawQFn
from django.http import Http404

def loadIfInSession(sessionVar, key, default):
	if key in sessionVar[0]:
		return (sessionVar[0][key])

	return default

def loadSessionSearchVars_proj(sessionVar):
	arr_ap = []; arr_cc = []; arr_epi = []; arr_iso = []; arr_isln = []; arr_loc = []; projectId = None;

	if 'projectId' in sessionVar[0]:
		projectId = sessionVar[0]['projectId']

	(arr_ap, arr_cc, arr_epi, arr_iso, arr_isln, arr_loc, searchType) = loadSessionSearchVars(sessionVar);

	return (arr_ap, arr_cc, arr_epi, arr_iso, arr_isln, arr_loc, projectId, searchType)



def loadSessionSearchVars(sessionVar):
	arr_ap = []; arr_cc = []; arr_epi = []; arr_iso = []; arr_isln = []; arr_loc = []; searchType = 'and'

	if len(sessionVar) > 0:
		if 'arrAp' in sessionVar[0]:
			arr_ap = sessionVar[0]['arrAp']
		if 'arrCc' in sessionVar[0]:
			arr_cc = sessionVar[0]['arrCc']
		if 'arrEpi' in sessionVar[0]:
			arr_epi = sessionVar[0]['arrEpi']
		if 'arrIso' in sessionVar[0]:
			arr_iso = sessionVar[0]['arrIso']
		if 'arrIsln' in sessionVar[0]:
			arr_isln = sessionVar[0]['arrIsln']
		if 'arrLoc' in sessionVar[0]:
			arr_loc = sessionVar[0]['arrLoc']

		if 'searchType' in sessionVar[0]:
			searchType = sessionVar[0]['searchType']


	return (arr_ap, arr_cc, arr_epi, arr_iso, arr_isln, arr_loc, searchType)

def loadSessionSearchVars_detail(sessionVar):
	searchAp = sessionVar[0]['json_apSearchTerms']
	searchCcEpi = sessionVar[0]['json_ccEpiSearchTerms']
	searchLocs = sessionVar[0]['json_location']
	searchIsln = sessionVar[0]['json_isolation']
	searchProj = sessionVar[0]['json_project']
	searchIso = sessionVar[0]['json_iso']

	# print("in function _detail")
	# print(sessionVar[0]['json_iso'])
	return (searchAp, searchCcEpi, searchLocs, searchIsln, searchProj, searchIso)


def convertToArrs_searchIsoDetail(searchAp, searchCcEpi, searchLocs, searchIsln, searchProj, searchIso, username):

	arr_ap = []; arr_ccEpi = []; arr_iso = []; arr_isln = []; arr_loc = [];
	if searchAp:
		arr_ap = [searchAp]
	if searchCcEpi:
		arr_ccEpi = [searchCcEpi]
	if searchLocs:
		arr_loc = [searchLocs]
	if searchIsln:
		arr_isln = [searchIsln]
	if searchProj:
		try:
			projectId = Project.objects.get(identifier=searchProj['project'], user__userId=username).id

			routeToRightRawQFn.isProjectByUser(projectId, username)
		except:
			# print("Does it come here...?");
			raise Http404("Error you dont have access to page. Go back.")

		searchProj['project'] = projectId
		arr_iso = [searchProj]
		print("over here...??")
	if searchIso:
		arr_iso.append(searchIso)


	return (arr_ap, arr_ccEpi, arr_loc, arr_isln, arr_iso)


def isASearchPresent_detail(requestVar):
	if ('json_apSearchTerms' in requestVar and len(requestVar['json_apSearchTerms']) > 0) or  ('json_ccEpiSearchTerms' in requestVar and len(requestVar['json_ccEpiSearchTerms']) > 0) or  ('json_location' in requestVar and len(requestVar['json_location']) > 0) or ('json_isolation' in requestVar and len(requestVar['json_isolation']) > 0) or ('json_project' in requestVar and len(requestVar['json_project']) > 0):
	 	return True

	return False


def isASearchPresent(sessionVar):
	if ('arrAp' in sessionVar and json.loads(sessionVar['arrAp']) and len(json.loads(sessionVar['arrAp'])) > 0) or ('arrCc' in sessionVar and json.loads(sessionVar['arrCc']) and len(json.loads(sessionVar['arrCc'])) > 0) or ('arrEpi' in sessionVar and json.loads(sessionVar['arrEpi']) and  len(json.loads(sessionVar['arrEpi'])) > 0) or ('arrIso' in sessionVar and json.loads(sessionVar['arrIso']) and  len(json.loads(sessionVar['arrIso'])) > 0) or ('arrIsln' in sessionVar and json.loads(sessionVar['arrIsln']) and  len(json.loads(sessionVar['arrIsln'])) > 0) or ('arrLoc' in sessionVar and json.loads(sessionVar['arrLoc']) and len(json.loads(sessionVar['arrLoc'])) > 0):
		return True

	return False


def loadRequestSearchVars(requestVar):

	arr_ap = json.loads(requestVar['arrAp'])
	arr_cc = json.loads(requestVar['arrCc'])
	arr_epi = json.loads(requestVar['arrEpi'])
	arr_iso = json.loads(requestVar['arrIso'])
	arr_isln = json.loads(requestVar['arrIsln'])
	arr_loc = json.loads(requestVar['arrLoc'])


	searchType = 'and'
	if 'searchType' in requestVar:
		searchType = requestVar['searchType']


	return (arr_ap, arr_cc, arr_epi, arr_iso, arr_isln, arr_loc, searchType)


def loadRequestSearchVars_proj(requestVar):
	arr_ap = json.loads(requestVar['arrAp'])
	arr_cc = json.loads(requestVar['arrCc'])
	arr_epi = json.loads(requestVar['arrEpi'])
	arr_iso = json.loads(requestVar['arrIso'])
	arr_isln = json.loads(requestVar['arrIsln'])
	arr_loc = json.loads(requestVar['arrLoc'])
	projectId = json.loads(requestVar['projectId'])

	if projectId:
		arr_iso.append({'project': projectId})
	#searchProj['project'] = projectId
	#arr_iso = [searchProj]


	searchType = 'and'
	if 'searchType' in requestVar:
		searchType = requestVar['searchType']

	return (arr_ap, arr_cc, arr_epi, arr_iso, arr_isln, arr_loc, projectId, searchType)
