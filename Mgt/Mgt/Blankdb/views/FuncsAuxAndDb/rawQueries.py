from Blankdb.models import View_apcc, Location, Isolation, Isolate, User, Tables_cc
from django.db import connections
import sys
import re


def executeQuery_count(queryStr):
	c = connections['blankdb'].cursor()
	c.execute(queryStr)
	iso = c.fetchall()
	c.close()

	return int(iso[0][0])


def executeQuery_table(queryStr):
	c = connections['blankdb'].cursor()

	c.execute(queryStr)
	iso = c.fetchall()
	columns = [col[0] for col in c.description]

	c.close()

	return (iso, columns)


##################### ISOLATE TABLE JOIN
db_isolate = "\"Blankdb_isolate\" as i"
db_view_apcc = "\"Blankdb_view_apcc\" as v"
db_isolation = "\"Blankdb_isolation\" as iM_i"
db_location = "\"Blankdb_location\" as iM_l"
db_iso_extFks = "\"Blankdb_isolate_extFks\" as i_ext"
db_extFks = "\"Blankdb_externalfks\" as iM_ext"
db_project = "\"Blankdb_project\" as p"

PuStart = 'i.id, i.identifier, i.server_status, i.assignment_status, i.serovar, i.mgt1, v.*, iM_l.*, iM_i.*'
PvStart = 'i.id, i.identifier, i.server_status, i.assignment_status, p.identifier, i.privacy_status, i.serovar, i.mgt1, v.*, iM_l.*, iM_i.*'
PvStart_projHidden = 'i.id, i.identifier, i.server_status, i.assignment_status, NULL AS project_id, i.privacy_status, NULL AS "isQuery", i.serovar, i.mgt1, v.*, iM_l.*, iM_i.*'
PvStart_projShow = 'i.id, i.identifier, i.server_status, i.assignment_status, p.identifier, i.privacy_status, i."isQuery", i.serovar, i.mgt1, v.*, iM_l.*, iM_i.*'
Count = 'count(*)'
Mgt9IsoFields = "i.id, i.identifier, i.mgt_id"

def getIsolates_auth_proj_cnt(isoSearchStr, projectIds, islnIds, locIds, mgtIds, searchType, isFirstSearchType):


	count = 0;

	(queryStr, isAnd) = sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, Count, False, False, True, searchType)

	queryStr = queryStr + inUserProjSql(projectIds, isAnd) # must be included

	queryStr = addTheSearchParams(queryStr, islnIds, locIds, mgtIds, True, searchType, isFirstSearchType)


	queryStr = queryStr + ';'

	# print (queryStr)

	count = executeQuery_count(queryStr)

	return count


def getIsolates_auth_proj(isoSearchStr, searchedProjIds, islnIds, locIds, mgtIds, offset, limit, orderBy, dir, isMgt9Ap, searchType, isFirstSearchType):
	# print('THE ISIOLATES')
	# print(isolates)
	isolates = []

	displayStr = PvStart_projShow

	if isMgt9Ap:
		displayStr = Mgt9IsoFields

	(queryStr, isAnd) = sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, displayStr, False, False, True, searchType)

	queryStr = queryStr + inUserProjSql(searchedProjIds, isAnd)

	queryStr = addTheSearchParams(queryStr, islnIds, locIds, mgtIds, True, searchType, isFirstSearchType)

	# queryStr (offset and limit)

	queryStr = addTheOrderBy(queryStr, orderBy, dir)
	queryStr = limitTheSearch(queryStr, offset, limit)

	queryStr = queryStr + ';'

	(isolates, columns) = executeQuery_table(queryStr)

	return (isolates, columns)




def getIsolates_auth_cnt(isoSearchStr, userProjectIds, islnIds, locIds, mgtIds, searchType, isFirstSearchType):

	count = 0;

	(queryStr, isAnd) = sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, Count, False, True, True, searchType)

	# exclude those in user projects
	if userProjectIds and len(userProjectIds) > 0:
		queryStr = queryStr + notInUserProjSql(userProjectIds)


	queryStr = addTheSearchParams(queryStr, islnIds, locIds, mgtIds, isAnd, searchType, isFirstSearchType)


	queryStr = queryStr + ';'


	count = executeQuery_count(queryStr)


	# TODO: COMPLETE THIS SECTION!! [DONE] # get those in uesr projects.
	if len(userProjectIds) > 0:
		count = count + getIsolates_auth_proj_cnt(isoSearchStr, userProjectIds, islnIds, locIds, mgtIds, searchType, isFirstSearchType)


	return (count)

def getIsolates_auth(isoSearchStr, userProjectIds, islnIds, locIds, mgtIds, offset, limit, orderBy, dir, isMgt9Ap, searchType, isFirstSearchType):

	isolates = []

	displayStr = PvStart_projHidden

	if isMgt9Ap:
		displayStr = Mgt9IsoFields

	(queryStr, isAnd) = sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, displayStr, False, True, True, searchType)


	# not in user projects
	if userProjectIds and len(userProjectIds) > 0:
		queryStr = queryStr + notInUserProjSql(userProjectIds)


	queryStr = addTheSearchParams(queryStr, islnIds, locIds, mgtIds, isAnd, searchType, isFirstSearchType)



	# TODO: CHANGE TO UNION (otherwise will end up with more than 100)
	if userProjectIds and len(userProjectIds) > 0:
		queryStr = queryStr + 'UNION ALL('

		displayStr2 = PvStart_projShow

		if isMgt9Ap:
			displayStr2 = Mgt9IsoFields

		(secondSql, isAnd) = sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, displayStr2, False, False, True, searchType)
		queryStr = queryStr + secondSql
		queryStr = queryStr + inUserProjSql(userProjectIds, isAnd)
		queryStr = addTheSearchParams(queryStr, islnIds, locIds, mgtIds, True, searchType, isFirstSearchType)

		queryStr = queryStr + ')'

		# print (queryStr)

	if not isMgt9Ap:
		queryStr = addTheOrderBy_without(queryStr, orderBy, dir)

	queryStr = limitTheSearch(queryStr, offset, limit)
	queryStr = queryStr + ';'


	print('The queryStr is ' + queryStr);
	(isolates, columns) = executeQuery_table(queryStr)
	# print(isolates)


	return (isolates, columns)


def getIsolates_cnt(isoSearchStr, islnIds, locIds, mgtIds, searchType, isFirstSearchType):

	count = 0;

	(queryStr, isAnd) = sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, Count, False, True, False, searchType)

	queryStr = addTheSearchParams(queryStr, islnIds, locIds, mgtIds, isAnd, searchType, isFirstSearchType)


	queryStr = queryStr + ';'
	# print (queryStr)

	count = executeQuery_count(queryStr)

	return count



def getIsolates(isoSearchStr, islnIds, locIds, mgtIds, offset, limit, orderBy, dir, isMgt9Ap, searchType, isFirstSearchType):

	isolates = []

	displayStr = PuStart

	if isMgt9Ap:
		displayStr = Mgt9IsoFields


	(queryStr, isAnd) = sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, displayStr, False, True, False, searchType)


	queryStr = addTheSearchParams(queryStr, islnIds, locIds, mgtIds, isAnd, searchType, isFirstSearchType)

	queryStr = addTheOrderBy(queryStr, orderBy, dir)

	queryStr = limitTheSearch(queryStr, offset, limit)
	queryStr = queryStr + ';'

	# print(queryStr)



	(isolates, columns) = executeQuery_table(queryStr)

	return (isolates, columns)


######################### AUX
def addTheOrderBy(queryStr, orderBy, dir):
	if orderBy and dir:
		queryStr = queryStr + ' ORDER BY ' + orderBy + ' ' + dir + ' NULLS LAST ';

	else: # add the default sort order.
		queryStr = addTheDefaultOrderBy(queryStr)

		# ' cc2_4 asc, cc2_3 asc, cc2_2 asc, cc2_1 asc'
	return queryStr


def addTheDefaultOrderBy(queryStr):

	tableNames = Tables_cc.objects.filter(display_table=2).order_by('-display_order').values_list('table_name')

	queryStr = queryStr + ' ORDER BY ' # ' i.id '

	for i in range(0, len(tableNames)):
		queryStr = queryStr + tableNames[i][0] + ' asc '

		if i != len(tableNames)-1:
			queryStr = queryStr + ', '
		else:
			queryStr = queryStr # + ', i.id asc '

	return (queryStr)

def addTheOrderBy_without(queryStr, orderBy, dir):
	if orderBy and dir:
		orderBy = re.sub("^.*\.", "", orderBy)
		# print(orderBy)

		queryStr = queryStr + ' ORDER BY ' + orderBy + ' ' + dir + ' NULLS LAST ';

	else:
		queryStr = addTheDefaultOrderBy(queryStr)

	return queryStr

def doJoins(sqlStr, mgtIds, locIds, islnIds, isAuth, searchType):

	if mgtIds and len(mgtIds) > 0 and searchType != 'or':
		sqlStr = sqlStr + ' INNER JOIN ' + db_view_apcc
	else:
		sqlStr = sqlStr + ' LEFT JOIN ' + db_view_apcc

	sqlStr = sqlStr + ' ON i.mgt_id = v.mgt_id '

	if locIds and len(locIds) > 0 and searchType != 'or':
		sqlStr = sqlStr + ' INNER JOIN ' + db_location
	else:
		sqlStr = sqlStr + ' LEFT JOIN '+ db_location

	sqlStr = sqlStr + ' ON i.location_id = iM_l.id '

	if islnIds and len(islnIds) > 0 and searchType != 'or':
		sqlStr = sqlStr + ' INNER JOIN ' + db_isolation
	else:
		sqlStr = sqlStr + ' LEFT JOIN ' + db_isolation

	sqlStr = sqlStr + ' ON i.isolation_id = iM_i.id '

	if isAuth:
		sqlStr = sqlStr + ' LEFT JOIN ' + db_project
		sqlStr = sqlStr + ' ON i.project_id = p.id '


	return sqlStr


def sqlQueryStruct(isoSearchStr, islnIds, locIds, mgtIds, displayStr, isPriv, isPub, isAuth, searchType):
	sqlStr = 'SELECT ' + displayStr + ' FROM ' + db_isolate

	sqlStr = doJoins(sqlStr, mgtIds, locIds, islnIds, isAuth, searchType)

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


def limitTheSearch(queryStr, offset, limit):

	queryStr = queryStr + ' OFFSET ' + str(offset) + ' LIMIT ' + str(limit)

	return (queryStr)


def notInUserProjSql(userProjIds):
	return (' AND i.project_id != ALL(ARRAY' + str(userProjIds) + ') ')

def inUserProjSql(projIds, isAnd):
	theStr = ""

	if isAnd:
		theStr = ' AND '

	isAnd = True

	return (theStr + ' i.project_id = ANY(ARRAY' + str(projIds) + ') ')

def addTheSearchParams(queryStr, islnIds, locIds, mgtIds, isAnd, searchType, isFirstSearchType):

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
