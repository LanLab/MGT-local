# from Salmonella.models import View_apcc, Location, Isolation, Isolate, User, Tables_cc
from django.db import connections
from django.conf import settings
# from Mgt.settings import RAWQUERIES_DISPLAY
import sys
import re
import importlib


def executeQuery_count(queryStr, org):
	c = connections[f'{org.lower()}'].cursor()
	c.execute(queryStr)
	iso = c.fetchall()
	c.close()

	return int(iso[0][0])


def executeQuery_table(queryStr, org):
	c = connections[f'{org.lower()}'].cursor()

	c.execute(queryStr)
	iso = c.fetchall()
	columns = [col[0] for col in c.description]

	c.close()

	return (iso, columns)


##################### ISOLATE TABLE JOIN
# db_isolate = "\"Salmonella_isolate\" as i"
# db_view_apcc = "\"Salmonella_view_apcc\" as v"
# db_isolation = "\"Salmonella_isolation\" as iM_i"
# db_location = "\"Salmonella_location\" as iM_l"
# db_iso_extFks = "\"Salmonella_isolate_extFks\" as i_ext"
# db_extFks = "\"Salmonella_externalfks\" as iM_ext"
# db_project = "\"Salmonella_project\" as p"

# PuStart = 'i.id, i.identifier, i.server_status, i.assignment_status, i.serovar, i.mgt1, v.*, iM_l.*, iM_i.*'
# PvStart = 'i.id, i.identifier, i.server_status, i.assignment_status, p.identifier, i.privacy_status, i.serovar, i.mgt1, v.*, iM_l.*, iM_i.*'
# PvStart_projHidden = 'i.id, i.identifier, i.server_status, i.assignment_status, NULL AS project_id, i.privacy_status, NULL AS "isQuery", i.serovar, i.mgt1, v.*, iM_l.*, iM_i.*'
PvStart_projShow = 'i.id, i.identifier, i.server_status, i.assignment_status, p.identifier, i.privacy_status, i."isQuery", i.serovar, i.mgt1, v.*, iM_l.*, iM_i.*'
Count = 'count(*)'
Mgt9IsoFields = "i.id, i.identifier, i.mgt_id"

def getIsolates_auth_proj_cnt(isoSearchStr, projectIds, islnIds, locIds, mgtIds, searchType, isFirstSearchType, org):
	View_apcc, Location, Isolation, Isolate, User, Tables_cc = getModels(org)
	
	count = 0;

	(queryStr, isAnd) = sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, Count, False, False, True, searchType, org)

	queryStr = queryStr + inUserProjSql(projectIds, isAnd, org) # must be included

	queryStr = addTheSearchParams(queryStr, islnIds, locIds, mgtIds, True, searchType, isFirstSearchType, org)


	queryStr = queryStr + ';'

	# print (queryStr)

	count = executeQuery_count(queryStr, org)

	return count


def getIsolates_auth_proj(isoSearchStr, searchedProjIds, islnIds, locIds, mgtIds, offset, limit, orderBy, dir, isMgt9Ap, searchType, isFirstSearchType, org):
	View_apcc, Location, Isolation, Isolate, User, Tables_cc = getModels(org)
	# print('THE ISIOLATES')
	# print(isolates)
	isolates = []
 
	displayStr = 'i.id, i.identifier, i.server_status, i.assignment_status, p.identifier, i.privacy_status, i."isQuery", i.serovar, i.mgt1, v.*, iM_l.*, iM_i.*' + settings.RAWQUERIES_DISPLAY[org]

	if isMgt9Ap:
		displayStr = Mgt9IsoFields

	(queryStr, isAnd) = sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, displayStr, False, False, True, searchType, org)

	queryStr = queryStr + inUserProjSql(searchedProjIds, isAnd, org)

	queryStr = addTheSearchParams(queryStr, islnIds, locIds, mgtIds, True, searchType, isFirstSearchType, org)

	# queryStr (offset and limit)

	queryStr = addTheOrderBy(queryStr, orderBy, dir, org)
	queryStr = limitTheSearch(queryStr, offset, limit, org)

	queryStr = queryStr + ';'

	(isolates, columns) = executeQuery_table(queryStr, org)

	return (isolates, columns)




def getIsolates_auth_cnt(isoSearchStr, userProjectIds, islnIds, locIds, mgtIds, searchType, isFirstSearchType, org):
	View_apcc, Location, Isolation, Isolate, User, Tables_cc = getModels(org)

	count = 0;

	(queryStr, isAnd) = sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, Count, False, True, True, searchType, org)

	# exclude those in user projects
	if userProjectIds and len(userProjectIds) > 0:
		queryStr = queryStr + notInUserProjSql(userProjectIds, org)


	queryStr = addTheSearchParams(queryStr, islnIds, locIds, mgtIds, isAnd, searchType, isFirstSearchType, org)


	queryStr = queryStr + ';'


	count = executeQuery_count(queryStr, org)


	# TODO: COMPLETE THIS SECTION!! [DONE] # get those in uesr projects.
	if len(userProjectIds) > 0:
		count = count + getIsolates_auth_proj_cnt(isoSearchStr, userProjectIds, islnIds, locIds, mgtIds, searchType, isFirstSearchType, org)


	return (count)

def getIsolates_auth(isoSearchStr, userProjectIds, islnIds, locIds, mgtIds, offset, limit, orderBy, dir, isMgt9Ap, searchType, isFirstSearchType, org):
	View_apcc, Location, Isolation, Isolate, User, Tables_cc = getModels(org)

	isolates = []
 
	print(settings.RAWQUERIES_DISPLAY[org])
	displayStr = 'i.id, i.identifier, i.server_status, i.assignment_status, NULL AS project_id, i.privacy_status, NULL AS "isQuery", i.serovar, i.mgt1, v.*, iM_l.*, iM_i.*' + settings.RAWQUERIES_DISPLAY[org]

	if isMgt9Ap:
		displayStr = Mgt9IsoFields

	(queryStr, isAnd) = sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, displayStr, False, True, True, searchType, org)


	# not in user projects
	if userProjectIds and len(userProjectIds) > 0:
		queryStr = queryStr + notInUserProjSql(userProjectIds, org)


	queryStr = addTheSearchParams(queryStr, islnIds, locIds, mgtIds, isAnd, searchType, isFirstSearchType, org)



	# TODO: CHANGE TO UNION (otherwise will end up with more than 100)
	if userProjectIds and len(userProjectIds) > 0:
		queryStr = queryStr + 'UNION ALL('

		displayStr2 = 'i.id, i.identifier, i.server_status, i.assignment_status, p.identifier, i.privacy_status, i."isQuery", i.serovar, i.mgt1, v.*, iM_l.*, iM_i.*' + settings.RAWQUERIES_DISPLAY[org]
  
		if isMgt9Ap:
			displayStr2 = Mgt9IsoFields

		(secondSql, isAnd) = sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, displayStr2, False, False, True, searchType, org)
		queryStr = queryStr + secondSql
		queryStr = queryStr + inUserProjSql(userProjectIds, isAnd, org)
		queryStr = addTheSearchParams(queryStr, islnIds, locIds, mgtIds, True, searchType, isFirstSearchType, org)

		queryStr = queryStr + ')'

		# print (queryStr)

	if not isMgt9Ap:
		queryStr = addTheOrderBy_without(queryStr, orderBy, dir, org)

	queryStr = limitTheSearch(queryStr, offset, limit, org)
	queryStr = queryStr + ';'


	print('The queryStr is ' + queryStr);
	(isolates, columns) = executeQuery_table(queryStr, org)
	# print(isolates)


	return (isolates, columns)


def getIsolates_cnt(isoSearchStr, islnIds, locIds, mgtIds, searchType, isFirstSearchType, org):
	View_apcc, Location, Isolation, Isolate, User, Tables_cc = getModels(org)

	count = 0;

	(queryStr, isAnd) = sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, Count, False, True, False, searchType, org)

	queryStr = addTheSearchParams(queryStr, islnIds, locIds, mgtIds, isAnd, searchType, isFirstSearchType, org)


	queryStr = queryStr + ';'
	# print (queryStr)

	count = executeQuery_count(queryStr, org)

	return count



def getIsolates(isoSearchStr, islnIds, locIds, mgtIds, offset, limit, orderBy, dir, isMgt9Ap, searchType, isFirstSearchType, org):
	View_apcc, Location, Isolation, Isolate, User, Tables_cc = getModels(org)

	isolates = []
 
	displayStr = 'i.id, i.identifier, i.server_status, i.assignment_status, i.serovar, i.mgt1, v.*, iM_l.*, iM_i.*' + settings.RAWQUERIES_DISPLAY[org]

	if isMgt9Ap:
		displayStr = Mgt9IsoFields


	(queryStr, isAnd) = sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, displayStr, False, True, False, searchType, org)


	queryStr = addTheSearchParams(queryStr, islnIds, locIds, mgtIds, isAnd, searchType, isFirstSearchType, org)

	queryStr = addTheOrderBy(queryStr, orderBy, dir, org)

	queryStr = limitTheSearch(queryStr, offset, limit, org)
	queryStr = queryStr + ';'

	print(queryStr)
	# print(isolates)

	(isolates, columns) = executeQuery_table(queryStr, org)


	return (isolates, columns)


######################### AUX
def addTheOrderBy(queryStr, orderBy, dir, org):
	View_apcc, Location, Isolation, Isolate, User, Tables_cc = getModels(org)
	if orderBy and dir:
		queryStr = queryStr + ' ORDER BY ' + orderBy + ' ' + dir + ' NULLS LAST ';

	else: # add the default sort order.
		queryStr = addTheDefaultOrderBy(queryStr, org)

		# ' cc2_4 asc, cc2_3 asc, cc2_2 asc, cc2_1 asc'
	return queryStr


def addTheDefaultOrderBy(queryStr, org):
	View_apcc, Location, Isolation, Isolate, User, Tables_cc = getModels(org)

	tableNames = Tables_cc.objects.filter(display_table=2).order_by('-display_order').values_list('table_name')

	queryStr = queryStr + ' ORDER BY ' # ' i.id '

	for i in range(0, len(tableNames)):
		queryStr = queryStr + tableNames[i][0] + ' asc '

		if i != len(tableNames)-1:
			queryStr = queryStr + ', '
		else:
			queryStr = queryStr # + ', i.id asc '

	return (queryStr)

def addTheOrderBy_without(queryStr, orderBy, dir, org):
	View_apcc, Location, Isolation, Isolate, User, Tables_cc = getModels(org)
	if orderBy and dir:
		orderBy = re.sub("^.*\.", "", orderBy)
		# print(orderBy)

		queryStr = queryStr + ' ORDER BY ' + orderBy + ' ' + dir + ' NULLS LAST ';

	else:
		queryStr = addTheDefaultOrderBy(queryStr, org)

	return queryStr

def doJoins(sqlStr, mgtIds, locIds, islnIds, isAuth, searchType, org):
	View_apcc, Location, Isolation, Isolate, User, Tables_cc = getModels(org)

	if mgtIds and len(mgtIds) > 0 and searchType != 'or':
		sqlStr = sqlStr + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v"
	else:
		sqlStr = sqlStr + ' LEFT JOIN ' + f"\"{org}_view_apcc\" as v"

	sqlStr = sqlStr + ' ON i.mgt_id = v.mgt_id '

	if locIds and len(locIds) > 0 and searchType != 'or':
		sqlStr = sqlStr + ' INNER JOIN ' + f"\"{org}_location\" as iM_l"
	else:
		sqlStr = sqlStr + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l"

	sqlStr = sqlStr + ' ON i.location_id = iM_l.id '

	if islnIds and len(islnIds) > 0 and searchType != 'or':
		sqlStr = sqlStr + ' INNER JOIN ' + f"\"{org}_isolation\" as iM_i"
	else:
		sqlStr = sqlStr + ' LEFT JOIN ' + f"\"{org}_isolation\" as iM_i"

	sqlStr = sqlStr + ' ON i.isolation_id = iM_i.id '

	if isAuth:
		sqlStr = sqlStr + ' LEFT JOIN ' + f"\"{org}_project\" as p"
		sqlStr = sqlStr + ' ON i.project_id = p.id '


	return sqlStr


def sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, displayStr, isPriv, isPub, isAuth, searchType, org):
	View_apcc, Location, Isolation, Isolate, User, Tables_cc = getModels(org)
	sqlStr = 'SELECT ' + displayStr + ' FROM ' +  f"\"{org}_isolate\" as i"

	sqlStr = doJoins(sqlStr, mgtIds, locIds, islnIds, isAuth, searchType, org)

	sqlStr = sqlStr + ' WHERE '

	isAnd = False

	if isPriv:
		sqlStr = sqlStr + ' i.privacy_status = \'PV\' '
		isAnd = True

	if isPub:
		sqlStr = sqlStr + ' i.privacy_status = \'PU\' '
		isAnd = True

	if isoSearchStr:
		if not isAnd:
			isoSearchStr = re.sub("^[\s]+AND", "", isoSearchStr, flags=re.I)
			isAnd = True

		sqlStr = sqlStr + isoSearchStr

	return (sqlStr, isAnd)


def limitTheSearch(queryStr, offset, limit, org):
	View_apcc, Location, Isolation, Isolate, User, Tables_cc = getModels(org)

	queryStr = queryStr + ' OFFSET ' + str(offset) + ' LIMIT ' + str(limit)

	return (queryStr)


def notInUserProjSql(userProjIds, org):
	View_apcc, Location, Isolation, Isolate, User, Tables_cc = getModels(org)
	return (' AND i.project_id != ALL(ARRAY' + str(userProjIds) + ') ')

def inUserProjSql(projIds, isAnd, org):
	View_apcc, Location, Isolation, Isolate, User, Tables_cc = getModels(org)
	theStr = ""

	if isAnd:
		theStr = ' AND '

	isAnd = True

	return (theStr + ' i.project_id = ANY(ARRAY' + str(projIds) + ') ')

def addTheSearchParams(queryStr, islnIds, locIds, mgtIds, isAnd, searchType, isFirstSearchType, org):
	View_apcc, Location, Isolation, Isolate, User, Tables_cc = getModels(org)

	isBracketOpened = False;

	if mgtIds and len(mgtIds) > 0:
		if isAnd:
			if isFirstSearchType:
				queryStr = queryStr + ' AND ('
				isFirstSearchType = False
				isBracketOpened = True
			else:
				queryStr = queryStr + searchType

		queryStr = queryStr + ' v.mgt_id = ANY(ARRAY' +  str(list(mgtIds)) +') '
		isAnd = True

	if islnIds and len(islnIds) > 0:
		if isAnd:
			if isFirstSearchType:
				queryStr = queryStr + ' AND ('
				isFirstSearchType = False
				isBracketOpened = True
			else:
				queryStr = queryStr + searchType

		queryStr = queryStr + ' iM_i.id = ANY(ARRAY' +  str(list(islnIds)) +') '
		isAnd = True

	if locIds and len(locIds) > 0:
		if isAnd:
			if isFirstSearchType:
				queryStr = queryStr + ' AND ('
				isFirstSearchType = False
				isBracketOpened = True
			else:
				queryStr = queryStr + searchType

		queryStr = queryStr + ' iM_l.id = ANY(ARRAY' +  str(list(locIds)) +') '
		isAnd = True


	if isBracketOpened == True:
		queryStr = queryStr + ")"


	return queryStr

def getModels(org):
    models = importlib.import_module(f'{org}.models')
    View_apcc = models.View_apcc
    Location = models.Location
    Isolation = models.Isolation
    Isolate = models.Isolate
    User = models.User
    Tables_cc = models.Tables_cc
    
    return View_apcc, Location, Isolation, Isolate, User, Tables_cc