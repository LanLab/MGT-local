from . import queryDb as q
from . import ownPaginator as ownPaginator
import re
from . import dataExtractTransform as det
from . import constants as c
from django.db.models import Q
from . import rawQueries
from . import getPoolOfCcMergeIds as getCcMergeIdsList
# from Salmonella.models import Project, User, Isolate, View_apcc, Location, Isolation, Tables_ap, Tables_cc
import importlib
from django.db import models
from django.core.exceptions import FieldDoesNotExist


### MAIN: AUTH (and non-auth) based search
def getIsolatesFromRightFn(arr_ap, arr_cc, arr_epi, arr_loc, arr_isln, arr_iso, pageNumToGet, totalPerPage, username, isExactProj, orderBy, dir, isCsv, isMgt9Ap, searchType, isMr, org):
	Project, User, Isolate, View_apcc, Location, Isolation, Tables_ap, Tables_cc = getModels(org)
	print ('VALUE OF ' + str(isExactProj) + " " + str(arr_iso) + ' ' + str(orderBy))

	isFirstSearchType = True
	isoCount = 0
	isolates = [];
	dict_pageInfo = ownPaginator.ownPaginator(0, 0, totalPerPage)
	dict_mergedIds = dict()

	(orderBy, dir) = convertToQueriableFields(orderBy, dir, org)

	(list_serverStatus, list_assignStatus, list_privStatus, boolChoices) = isolateChoices(org)

	try:
		(mgtIds, locIds, islnIds, isoSearchStr, searchedProjIds, userProjIds, dict_mergedIds, isFirstSearchType) = convertSearchToIds(arr_ap, arr_cc, arr_epi, arr_loc, arr_isln, arr_iso, username, isExactProj, searchType, isFirstSearchType, org)
	except IncorrectAccessError as e:
		print("Incorrect access error encoutered early on!.")
		print(e)

		return (isoCount, isolates, dict_pageInfo, dict_mergedIds, [], [], [], list_serverStatus, list_assignStatus, list_privStatus, boolChoices)



	if len(searchedProjIds) > 0: # if projects are searched for
		isoCount = rawQueries.getIsolates_auth_proj_cnt(isoSearchStr, searchedProjIds, islnIds, locIds, mgtIds, searchType, isFirstSearchType, org)

		dict_pageInfo = ownPaginator.ownPaginator(isoCount, pageNumToGet, totalPerPage)

		offset = dict_pageInfo['start_index']
		limit = c.TOTAL_ISO_PER_PAGE

		if isCsv:
			offset = 0
			limit = c.TOTAL_ISO_PER_DOWNLOAD

		if isMr:
			offset = 0
			limit = c.TOTAL_ISO_MICROREACT

		if isMgt9Ap:
			offset = 0
			limit = c.TOTAL_MGT9_ISO_DOWNLOAD

		(isolates, columns) = rawQueries.getIsolates_auth_proj(isoSearchStr, searchedProjIds, islnIds, locIds, mgtIds, offset, limit, orderBy, dir, isMgt9Ap, searchType, isFirstSearchType, org)



		(list_colsInfo, list_tabAps, list_tabCcs) = convertColsToDict(columns, True, org)



		# print("The columns are:")
		# print(columns)
		# print("THE ISOLATES")
		# print (isolates)

	elif username: # if projects are not searched for; but user is logged in

		print("UserProjIds outside is " + str(userProjIds))
		isoCount = rawQueries.getIsolates_auth_cnt(isoSearchStr, userProjIds, islnIds, locIds, mgtIds, searchType, isFirstSearchType, org)


		dict_pageInfo = ownPaginator.ownPaginator(isoCount, pageNumToGet, totalPerPage)

		offset = dict_pageInfo['start_index']
		limit = c.TOTAL_ISO_PER_PAGE

		if isCsv:
			offset = 0
			limit = c.TOTAL_ISO_PER_DOWNLOAD

		if isMr:
			offset = 0
			limit = c.TOTAL_ISO_MICROREACT

		if isMgt9Ap:
			offset = 0
			limit = c.TOTAL_MGT9_ISO_DOWNLOAD

		(isolates, columns) = rawQueries.getIsolates_auth(isoSearchStr, userProjIds, islnIds, locIds, mgtIds, offset, limit, orderBy, dir, isMgt9Ap, searchType, isFirstSearchType, org)
		# print("least thought of!")

		(list_colsInfo, list_tabAps, list_tabCcs) = convertColsToDict(columns, True, org)
	else: # user is not logged in

		isoCount = rawQueries.getIsolates_cnt(isoSearchStr, islnIds, locIds, mgtIds, searchType, isFirstSearchType, org)


		dict_pageInfo = ownPaginator.ownPaginator(isoCount, pageNumToGet, totalPerPage)
		# print(dict_pageInfo)
		# print(isCsv)


		offset = dict_pageInfo['start_index']
		limit = c.TOTAL_ISO_PER_PAGE

		if isCsv:
			offset = 0
			limit = c.TOTAL_ISO_PER_DOWNLOAD

		if isMr:
			offset = 0
			limit = c.TOTAL_ISO_MICROREACT

		if isMgt9Ap:
			offset = 0
			limit = c.TOTAL_MGT9_ISO_DOWNLOAD

			# rawQueryies.getIsolatesAndMgt9Ap(isoSearchStr, islnIds, locIds, mgtIds, offset, limit, orderBy, dir)

		# print(offset, limit)


		(isolates, columns) = rawQueries.getIsolates(isoSearchStr, islnIds, locIds, mgtIds, offset, limit, orderBy, dir, isMgt9Ap, searchType, isFirstSearchType, org)




		(list_colsInfo, list_tabAps, list_tabCcs) = convertColsToDict(columns, False, org)


	return (isoCount, isolates, dict_pageInfo, dict_mergedIds, list_colsInfo, list_tabAps, list_tabCcs, list_serverStatus, list_assignStatus, list_privStatus, boolChoices)

















def getMgtIds(arr_ap, arr_cc, arr_epi, searchType, org):
	Project, User, Isolate, View_apcc, Location, Isolation, Tables_ap, Tables_cc = getModels(org)
	qs_mgtIds = None

	# for cc_query, and cc_mergeIds
	andOfOrQs = Q()
	dict_mergedIds = dict()

	if len(arr_cc) > 0 or len(arr_epi) > 0: # cc and epi query (combine into 1)
		(andOfOrQs, dict_mergedIds) = getCcMergeIdsList.getAndOfOrQsAndMergedIds(arr_cc, arr_epi, searchType, org)


	if len(arr_ap) > 0: # ap query
		if searchType == 'and':
			andOfOrQs = det.addToAndQFromList(andOfOrQs, arr_ap)
		elif searchType == 'or':
			andOfOrQs = det.addToOrQFromList_ap(andOfOrQs, arr_ap)


	# getting the mgt ids.
	qs_mgtIds = q.getMgtIdsFromViewWithQ(andOfOrQs, org)
	# print("qs_mgtIds: ")
	# print(qs_mgtIds)
	return (qs_mgtIds, dict_mergedIds)


def getLocIds(arr_loc, searchType, org):
	Project, User, Isolate, View_apcc, Location, Isolation, Tables_ap, Tables_cc = getModels(org)
	qs_location = None

	andQ_loc = Q()
	if (searchType == 'and'):
		andQ_loc = det.addToAndQICntnsFromList(andQ_loc, arr_loc)
	else:
		andQ_loc = det.addToOrQICntnsFromList(andQ_loc, arr_loc)

	qs_location = q.getLocationIdsWithQ(andQ_loc, org)

	return qs_location

def getIslnIds(arr_isln, searchType, org):
	Project, User, Isolate, View_apcc, Location, Isolation, Tables_ap, Tables_cc = getModels(org)
	qs_isln = None

	andQ_isln = Q()

	for dict_ in arr_isln:
		for key in dict_:
			if re.match("year", key) or re.match("date", key) or re.match("month", key):
				# print (key);

				if searchType == 'and':
					andQ_isln = det.addToAndQFromList(andQ_isln, [dict_])

				else:
					andQ_isln = det.addToOrQFromList(andQ_isln, [dict_])

			else:
				if searchType == 'and':
					andQ_isln = det.addToAndQICntnsFromList(andQ_isln, [dict_])

				else:
					andQ_isln = det.addToOrQICntnsFromList(andQ_isln, [dict_])


	qs_isln = q.getIsolnIdsWithQ(andQ_isln, org)

	# print("The Isolation search ");
	# print(qs_isln)
	return (qs_isln)




def makeSearchStr_retProjIdsIfSearProj(arr_iso, username, isExactProj, searchType, isFirstSearchType, org):
	Project, User, Isolate, View_apcc, Location, Isolation, Tables_ap, Tables_cc = getModels(org)
	searchStr = "";
	projectIds = []

	for dict_ in arr_iso:
		for key in dict_:
			if re.match("privacy_status", key) or re.match('isQuery', key):
				searchStr = searchStr + " and i.\"" + key +"\"=\'" + dict_[key] + "\'";

			elif re.match("server_status", key) or re.match("assignment_status", key) or re.match("mgt1", key):
				if isFirstSearchType == True:
					searchStr = searchStr + ' ' + ' AND '
					isFirstSearchType = False
				else:
					searchStr = searchStr +  ' ' + searchType

				searchStr = searchStr + " i." + key +"=\'" + dict_[key] + "\'";

			elif username and re.match("project", key) and isExactProj == False:

				projectIds = q.getAndAddProjectIds(username, dict_[key], projectIds, org)

				# print("project ids are :::")
				# print(projectIds)
				# searchStr = searchStr + " and i.project=\'" + dict_[key] + "\'";
				if len(projectIds) == 0:
					print("Project belongs to someone else")
					raise IncorrectAccessError("Project belongs to someone else")

			elif username and re.match("project", key) and isExactProj == True:
				if not isProjectByUser(dict_[key], username, org):
					print("Project belongs to someone else")
					raise IncorrectAccessError("Project belongs to someone else")
				projectIds = [int(dict_[key])]
				print("THE PROJECT IDS ARE:::")
				print(projectIds)

			elif re.match("identifier", key):
				if isFirstSearchType == True:
					searchStr = searchStr + ' ' + ' AND '
					isFirstSearchType = False
				else:
					searchStr = searchStr +  ' ' + searchType
				searchStr = searchStr + " i.identifier ILIKE \'%" + dict_[key] + "%\'"

			elif re.match("serovar", key):
				if isFirstSearchType == True:
					searchStr = searchStr + ' ' + ' AND '
					isFirstSearchType = False
				else:
					searchStr = searchStr +  ' ' + searchType

				searchStr = searchStr + " i.serovar ILIKE \'%" + dict_[key] + "%\'"

			elif re.match("id", key):
				searchStr = searchStr + " and i.id=\'" + dict_[key] + "\'"

			else:
				print("Unknown key supplied")
				raise IncorrectAccessError("Unknown key supplied")

	# print (searchStr);
	return (searchStr, projectIds, isFirstSearchType)

class IncorrectAccessError(Exception):
	"""Raise when user searched for strings which did not return any ids in the database"""

def isProjectByUser(projectId, username, org):
	Project, User, Isolate, View_apcc, Location, Isolation, Tables_ap, Tables_cc = getModels(org)
	if Project.objects.filter(id=int(projectId),user=User.objects.get(userId=username)).exists():
		return True

	return False


def isEmptyApCcEpi(arr_orig, org):
	Project, User, Isolate, View_apcc, Location, Isolation, Tables_ap, Tables_cc = getModels(org)
	arr_ = arr_orig.copy()

	if arr_ and len(arr_) > 0:
		firstElem = arr_.pop()
		if firstElem:

			# print("return is not empty")
			return False

	# print("return is empty")

	# print(arr_)
	arr_ = arr_orig # as a fail safe only
	return True

def convertSearchToIds(arr_ap, arr_cc, arr_epi, arr_loc, arr_isln, arr_iso, username, isExactProj, searchType, isFirstSearchType, org):
	Project, User, Isolate, View_apcc, Location, Isolation, Tables_ap, Tables_cc = getModels(org)
	mgtIds = None # querySets
	locIds = None
	islnIds = None
	isoSearchStr = ""
	searchedProjIds = [] # searched project ids
	userProjIds = [] #
	dict_mergedIds = dict()



	if not isEmptyApCcEpi(arr_ap, org) or not isEmptyApCcEpi(arr_cc, org) or not isEmptyApCcEpi(arr_epi, org):

		(mgtIds, dict_mergedIds) = getMgtIds(arr_ap, arr_cc, arr_epi, searchType, org)

		if not mgtIds or len(mgtIds) == 0:
			print("Mgt ids not found")
			raise IncorrectAccessError('Mgt ids not found.') # nothing found, so return empty

		# if len(dict_mergedIds) > 0:
		# 	print(dict_mergedIds)
		#	print("need to do something here...")

	if len(arr_loc) > 0 and len(arr_loc[0]) > 0:
		locIds = getLocIds(arr_loc, searchType, org)

		if not locIds or len(locIds) == 0: # nothing found
			print(str(arr_loc) + " " + str(len(arr_loc)))
			print("Loc ids not found.")
			raise IncorrectAccessError('Loc ids not found.')

	if len(arr_isln) > 0 and len(arr_isln[0]) > 0:
		print(arr_isln);
		islnIds = getIslnIds(arr_isln, searchType, org)

		if not islnIds or len(islnIds) == 0:
			print('Isln ids not found.')
			raise IncorrectAccessError('Isln ids not found.')

	if len(arr_iso) > 0 and len(arr_iso[0]) > 0:
		(isoSearchStr, searchedProjIds, isFirstSearchType) = makeSearchStr_retProjIdsIfSearProj(arr_iso, username, isExactProj, searchType, isFirstSearchType, org)
		# print ("The searched project ids are: " + str(searchedProjIds))

		if isoSearchStr == "" and len(searchedProjIds) == 0: # empty search string
			print("No iso to features to search")
			raise IncorrectAccessError('No iso to features to search')

	if username:
		userProjIds = q.getUserProjectIds(username, org)
		# print (userProjIds)
		if (len(searchedProjIds) > 0 and len(userProjIds) == 0) or not set(searchedProjIds).issubset(set(userProjIds)):
			# print("Searched projects when either user hasnt created any projects or the searched project is not a user project")
			# print("here...?")
			raise IncorrectAccessError('Searched projects when either user hasnt created any projects or the searched project is not a user project')



	return (mgtIds, locIds, islnIds, isoSearchStr, searchedProjIds, userProjIds, dict_mergedIds, isFirstSearchType)

def convertToQueriableFields(orderBy, dir, org):
	Project, User, Isolate, View_apcc, Location, Isolation, Tables_ap, Tables_cc = getModels(org)

	if orderBy and 'isQuery' in orderBy:
		orderBy = re.sub('isQuery', '\"isQuery\"', orderBy)
		# print ("The new orderBy is " + orderBy)

	if dir == 'Ascending':
		dir = 'ASC'
	elif dir == 'Descending':
		dir = 'DESC'

	return (orderBy, dir);

def convertColNmForDownload(list_colsInfo, org): # only show the display names
	Project, User, Isolate, View_apcc, Location, Isolation, Tables_ap, Tables_cc = getModels(org)
	#print(len(list_colsInfo))
	list_colNames_downld = list()
	#print('within the function')

	for dict_ in list_colsInfo:
		list_colNames_downld.append(dict_['display_name'])
		# print(dict_['display_name'])

	return (list_colNames_downld)

def convertColsToDict(columns, isAuth, org):
	Project, User, Isolate, View_apcc, Location, Isolation, Tables_ap, Tables_cc = getModels(org)
	# print(columns)
	list_colsInfo = list() # [dict1{table_name, display_name, data_colNum}, dict2 ... ]

	isIsoFound = False
	isLocFound = False
	isIslnFound = False
	isProjFound = False
	isIdentIso = False
	isIdentProj = False


	counter = 0;




	for col in columns:
		dict_col = dict()
		dict_col['table_name'] = col


		(display_name, searchStr, isIsoFound, isLocFound, isIslnFound, isProjFound, isIdentIso, isIdentProj) =  getDisplayName(col, isIsoFound, isLocFound, isIslnFound, isAuth, isProjFound, isIdentIso, isIdentProj, org)
		dict_col['display_name'] = display_name
		dict_col['db_col'] = counter
		dict_col['t_search'] = searchStr
		counter = counter + 1

		list_colsInfo.append(dict_col)


	list_tabAps = list(Tables_ap.objects.filter(table_num=0).values('table_name', 'display_order', 'display_name'))
	list_tabCcs = list(Tables_cc.objects.all().values('table_name', 'display_table', 'display_order', 'display_name'))

	return (list_colsInfo, list_tabAps, list_tabCcs)

### Col names

def isolateChoices(org):
	Project, User, Isolate, View_apcc, Location, Isolation, Tables_ap, Tables_cc = getModels(org)
	list_serverStatus = dict(Isolate.server_status_choices)
	list_assignStatus = dict(Isolate.assignment_status_choices)
	list_privStatus = dict(Isolate.privacy_status_choices)
	boolChoices = {'t': 'True', 'f': 'False'}

	return(list_serverStatus, list_assignStatus, list_privStatus, boolChoices)




###### Getting the columns for display.
def getDisplayName(col, isIso, isLoc, isIsln, isAuth, isProjAdded, isIdentIso, isIdentProj, org):
	Project, User, Isolate, View_apcc, Location, Isolation, Tables_ap, Tables_cc = getModels(org)

	verboseName = None
	searchStr = None


	# print(str(isAuth) + "  donald trump " + str(isProjAdded))
	# print(col)

	if (col.lower() == "id"):
		if isIso == False:
			verboseName = Isolate._meta.get_field(col).verbose_name
			isIso = True
			searchStr = "i"

		# if isAuth == true && isProj == false:
		elif isAuth == True and isProjAdded == False:
			verboseName = Project._meta.get_field(col).verbose_name
			isProjAdded = True
			searchStr = 'p'

			# print("Over here!!")



		elif isLoc == False:
			verboseName = Location._meta.get_field(col).verbose_name
			isLoc = True
			searchStr = 'iM_l'

		elif isIsln == False:
			verboseName = Isolation._meta.get_field(col).verbose_name
			isIsln = True
			searchStr = 'iM_i'

	if (col.lower() == "identifier"):

		if isIdentIso == False:
			verboseName = Isolate._meta.get_field(col).verbose_name
			searchStr = 'i'
			isIdentIso = True

		elif isAuth == True and isIdentProj == False:
			verboseName = Project._meta.get_field(col).verbose_name
			searchStr = 'p'
			isIdentProj = True
			# print(verboseName)




	if verboseName == None and model_field_exists(Isolate, col):
		verboseName = Isolate._meta.get_field(col).verbose_name
		searchStr = 'i'
		# print("here!")

	if verboseName == None and model_field_exists(Project, col):
		verboseName = Project._meta.get_field(col).verbose_name
		searchStr = 'p'
		# print("here!")

	if verboseName == None and model_field_exists(View_apcc, col):
		verboseName = View_apcc._meta.get_field(col).verbose_name
		searchStr = 'v'

	if verboseName == None and model_field_exists(Location, col):
		verboseName = Location._meta.get_field(col).verbose_name
		searchStr = 'iM_l'

	if verboseName == None and model_field_exists(Isolation, col):
		verboseName = Isolation._meta.get_field(col).verbose_name
		searchStr = 'iM_i'


	return(verboseName, searchStr, isIso, isLoc, isIsln, isProjAdded, isIdentIso, isIdentProj)



def model_field_exists(theModel, field):
    try:
        theModel._meta.get_field(field)
        return True
    except FieldDoesNotExist:
        return False

def getModels(org):
    models = importlib.import_module(f'{org}.models')
    Project = models.Project
    User = models.User
    Isolate = models.Isolate
    View_apcc = models.View_apcc
    Location = models.Location
    Isolation = models.Isolation
    Tables_ap = models.Tables_ap
    Tables_cc = models.Tables_cc
    
    return Project, User, Isolate, View_apcc, Location, Isolation, Tables_ap, Tables_cc