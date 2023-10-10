# from Salmonella.models import View_apcc, Location, Isolation, Isolate, User
from django.db import connections
import sys
import importlib
#################### SINGLE ISOLATE

# def ifPuGetObj(pk):
# 	return None;

#################### ISOLATION_VIEW TABLE

def getIsolnIdsWithDict(dict_, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	qs_islnIds = Isolation.objects.filter(**dict_).values_list('id', flat=True).distinct()

	return qs_islnIds

def getIsolnIdsWithQ(theQ, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	qs_islnIds = Isolation.objects.filter(theQ).values_list('id', flat=True).distinct()

	return qs_islnIds

#################### LOCATION_VIEW TABLE

def getLocationIdsWithDict(dict_, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	qs_locIds = Location.objects.filter(**dict_).values_list('id', flat=True).distinct()

	return qs_locIds

def getLocationIdsWithQ(theQ, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	qs_locIds = Location.objects.filter(theQ).values_list('id', flat=True).distinct()

	return qs_locIds

#################### MGT_VIEW TABLE

def getMergedIds(orQ, ccTn, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	qs_mergedIds = View_apcc.objects.filter(orQ).values_list(ccTn, ccTn+"_merge").distinct()

	print("query set " + str(qs_mergedIds));
	return qs_mergedIds

def getMgtIdsFromViewWithQ(theQ, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	qs_mgtIds = View_apcc.objects.filter(theQ).values_list('mgt_id', flat=True).distinct()

	return qs_mgtIds;

def getmgtIdsFromViewWithAndDict(dict_, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	qs_mgtIds = View_apcc.objects.filter(**dict_).values_list('mgt_id', flat=True).distinct()

	return qs_mgtIds

##################### ISOLATE TABLE JOIN
# db_isolate = f"\"{org}_isolate\" as i" 
# db_view_apcc = f"\"{org}_view_apcc\" as v"
# db_isolation = f"\"{org}_isolation\" as iM_i"
# db_location = f"\"{org}_location\" as iM_l"
# db_iso_extFks = f"\"{org}_isolate_extFks\" as i_ext"
# db_extFks = f"\"{org}_externalfks\" as iM_ext"
# db_project = f"\"{org}_project\" as p"

puStart = 'i.id, i.identifier, i.server_status, i.assignment_status, v.*, iM_l.*, iM_i.*'
pvStart = 'i.id, i.identifier, i.server_status, i.assignment_status, p.identifier, i.privacy_status, v.*, iM_l.*, iM_i.*'
pvStart_projHidden = 'i.id, i.identifier, i.server_status, i.assignment_status, NULL AS project_id, i.privacy_status, v.*, iM_l.*, iM_i.*'



def getTop5StByContinet(tn, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = []


	queryStr = 'SELECT * FROM (' + 'SELECT (row_number() over (partition by iM_l.continent ORDER BY COUNT(v.' + tn + '_st) DESC)) as ROW_ID, count(v.' + tn + '_st), iM_l.continent, v.' + tn + '_st FROM '  + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON  i.mgt_id = v.mgt_id INNER JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id WHERE i.privacy_status=\'PU\' GROUP BY iM_l.continent, v.' + tn + '_st) as t where ROW_ID <= 5;';

	print(queryStr);
	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error\n");
		raise

	# print('By continent')
	# print(iso)
	return iso



def getTop5St(tn, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	iso = []


	queryStr = 'SELECT v.' + tn + '_st, count(v.' + tn +'_st) as c from ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON  i.mgt_id = v.mgt_id GROUP BY v.' + tn + '_st ORDER BY c desc fetch first 5 rows only;';

	print(queryStr);

	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error\n");
		raise


	print(iso)
	return iso




def getIsolatesWithMisln_auth_proj(islnIds, isoSearchStr, offset, limit, projectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	iso = [];


	queryStr = 'SELECT  ' + pvStart  + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id WHERE i.project_id = ANY(ARRAY'+ str(projectIds) +') '+ isoSearchStr + ' and iM_i.id = ANY(ARRAY' +  str(list(islnIds)) +') ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise


	return iso

def getIsolatesWithMisln_auth_cnt(islnIds, isoSearchStr, userProjectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	count = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' ' + isoSearchStr + ' and iM_i.id = ANY(ARRAY' +  str(list(islnIds)) +');'

	if len(userProjectIds) > 0:
		queryStr = queryStr + ' i.project_id != ALL(ARRAY' + str(userProjectIds) + ') '


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	count = int(isoCount[0][0])

	if len(userProjectIds) > 0:
		count = count + getIsolatesWithMisln_auth_proj_cnt(islnIds, isoSearchStr, userProjectIds)

	return count

def getIsolatesWithMisln_auth(islnIds, isoSearchStr, offset, limit, userProjectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	iso = [];

	# public and not in user projects
	queryStr = 'SELECT ' + pvStart_projHidden + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id WHERE i.privacy_status=\'PU\' '+ isoSearchStr + ' and iM_i.id = ANY(ARRAY' +  str(list(islnIds)) +')'


	# only in user projects
	if len(userProjectIds) > 0:
		queryStr = queryStr + 'and i.project_id != ALL(ARRAY'+ str(userProjectIds) +')'

		queryStr = queryStr + 'UNION ALL(SELECT ' + pvStart_projHidden + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id WHERE i.project_id = ANY(ARRAY'+ str(userProjectIds) +') '+ isoSearchStr + ' and iM_i.id = ANY(ARRAY' +  str(list(islnIds)) +'))'


	queryStr = queryStr + ' ORDER BY server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'




	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise


	return iso

def getIsolatesWithMisln_cnt(islnIds, isoSearchStr, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	isoCount = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' ' + isoSearchStr + ' and iM_i.id = ANY(ARRAY' +  str(list(islnIds)) +');'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return isoCount[0][0]


def getIsolatesWithMisln(islnIds, isoSearchStr, offset, limit, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	iso = [];


	queryStr = 'SELECT ' + puStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' '+ isoSearchStr + ' and iM_i.id = ANY(ARRAY' +  str(list(islnIds)) +') ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise


	return iso


def getIsolatesWithMlocs_auth_proj_cnt(locIds, isoSearchStr, projectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	isoCount = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.project_id = ANY(ARRAY' + str(projectIds) + ') ' + isoSearchStr + ' and iM_l.id = ANY(ARRAY' +  str(list(locIds)) +');'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return isoCount[0][0]



def getIsolatesWithMlocs_auth_proj(locIds, isoSearchStr, offset, limit, projectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	queryStr = 'SELECT ' + pvStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id WHERE i.project_id = ANY(ARRAY' + str(projectIds) + ') ' + isoSearchStr + ' and iM_l.id = ANY(ARRAY' +  str(list(locIds)) +') ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ' ;'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso


def getIsolatesWithMlocs_auth_cnt(locIds, isoSearchStr, userProjectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	count = 0;

	# public and not in user projects
	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status = \'PU\' ' + isoSearchStr + ' and iM_l.id = ANY(ARRAY' +  str(list(locIds)) +');'

	if len(userProjectIds) > 0:
		queryStr = queryStr + ' and i.project_id != ALL(ARRAY' + str(userProjectIds) + ') '


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	# only in user projects

	count = int(isoCount[0][0])

	if len(userProjectIds) > 0:
		count = count + getIsolatesWithMlocs_auth_proj_cnt(locIds, isoSearchStr, userProjectIds, org)

	return count



def getIsolatesWithMlocs_auth(locIds, isoSearchStr, offset, limit, userProjectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	# public and not in user projects
	queryStr = 'SELECT ' + pvStart_projHidden + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id WHERE i.privacy_status = \'PU\' and i.project_id != ALL(ARRAY' + str(userProjectIds) + ') ' + isoSearchStr + ' and iM_l.id = ANY(ARRAY' +  str(list(locIds)) +')'

	# only in user projects

	if len(userProjectIds) > 0:
		queryStr = queryStr + 'UNION ALL(SELECT ' + pvStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id WHERE i.project_id = ANY(ARRAY' + str(userProjectIds) + ') ' + isoSearchStr + ' and iM_l.id = ANY(ARRAY' +  str(list(locIds)) +'))'


	queryStr = queryStr +  ' ORDER BY server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ' ;'

	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso





def getIsolatesWithMlocs_cnt(locIds, isoSearchStr, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	isoCount = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' ' + isoSearchStr + ' and iM_l.id = ANY(ARRAY' +  str(list(locIds)) +');'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return isoCount[0][0]



def getIsolatesWithMlocs(locIds, isoSearchStr, offset, limit, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	queryStr = 'SELECT ' + puStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' ' + isoSearchStr + ' and iM_l.id = ANY(ARRAY' +  str(list(locIds)) +') ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ' ;'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso


def getIsolateWithAmgt(mgtId, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	c = connections[f'{org.lower()}'].cursor()

	queryStr = 'SELECT ' + puStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id WHERE i.privacy_status=\'PU\' ORDER BY i.server_status LIMIT 1000';

	# print (queryStr)
	# i.'+ fieldName + ' LIKE \'' + val + '%\'
	c.execute(queryStr)
	iso = c.fetchall()

	c.close()

	return iso





def getIsolatesWithLocIsln_auth_cnt(qs_locIds, qs_islnIds, isoSearchStr, userProjectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	count = 0

	# public and not in user projects
	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' ' + isoSearchStr + ' and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) +  ');'

	if len(userProjectIds):
		queryStr = queryStr + ' AND i.project_id != ALL(ARRAY' + str(userProjectIds) + ') '

	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	# only in user projects
	count = int(isoCount[0][0])
	if len(userProjectIds) > 0:
		count = count + getIsolatesWithLocIsln_auth_proj_cnt(qs_locIds, qs_islnIds, isoSearchStr, userProjectIds, org)

	return count

def getIsolatesWithLocIsln_auth(qs_locIds, qs_islnIds, isoSearchStr, offset, limit, userProjectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	# public and not in user projects
	queryStr = 'SELECT ' + pvStart_projHidden + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id WHERE i.privacy_status = \'PU\' ' + isoSearchStr + ' and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) +  ')'


	# only in user projects
	if len(userProjectIds) > 0:
		queryStr = queryStr + ' and i.project_id != ALL(ARRAY' + str(userProjectIds) + ') '

		queryStr = queryStr + 'UNION ALL(SELECT ' + pvStart +' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id WHERE i.project_id = ANY(ARRAY' + str(userProjectIds) + ') ' + isoSearchStr + ' and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) +  '))'

	queryStr = queryStr + 'ORDER BY server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso




def getIsolatesWithLocIsln_auth_proj_cnt(qs_locIds, qs_islnIds, isoSearchStr, projectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	isoCount = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.project_id = ANY(ARRAY' + str(projectIds) + ') ' + isoSearchStr + ' and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) +  ');'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return isoCount[0][0]

def getIsolatesWithLocIsln_auth_proj(qs_locIds, qs_islnIds, isoSearchStr, offset, limit, projectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	queryStr = 'SELECT ' + pvStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id WHERE i.project_id = ANY(ARRAY' + str(projectIds) + ') ' + isoSearchStr + ' and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) +  ') ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso


def getIsolatesWithLocIsln_cnt(qs_locIds, qs_islnIds, isoSearchStr, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	isoCount = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' ' + isoSearchStr + ' and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) +  ');'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return isoCount[0][0]

def getIsolatesWithLocIsln(qs_locIds, qs_islnIds, isoSearchStr, offset, limit, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	queryStr = 'SELECT ' + puStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' ' + isoSearchStr + ' and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) +  ') ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso



def getIsolatesWithMFilters_auth_cnt(qs_mgtIds, qs_locIds, qs_islnIds, isoSearchStr, userProjectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	isoCount = 0;
	count = 0

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' AND i.project_id != ALL(ARRAY' + str(list(userProjectIds)) + ') ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) +  ');'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	count = isoCount[0][0] + getIsolatesWithMFilters_auth_proj_cnt(qs_mgtIds, qs_locIds, qs_islnIds, isoSearchStr, userProjectIds, org)

	return count



def getIsolatesWithMFilters_auth(qs_mgtIds, qs_locIds, qs_islnIds, isoSearchStr, offset, limit, userProjectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];
	# public and not in user projects
	queryStr = 'SELECT ' + pvStart_projHidden + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id WHERE i.privacy_status=\'PU\' AND i.project_id != ALL(ARRAY' + str(userProjectIds) + ') ' + isoSearchStr +  ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) +  ')'

	# only in user projects
	if len(userProjectIds) > 0:
		queryStr = queryStr + ' UNION ALL(SELECT ' + pvStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id WHERE i.project_id = ANY(ARRAY' + str(userProjectIds) + ') ' + isoSearchStr +  ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) +  '))'

	queryStr = queryStr + 'ORDER BY server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso



def getIsolatesWithMFilters_auth_proj_cnt(qs_mgtIds, qs_locIds, qs_islnIds, isoSearchStr, projectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	isoCount = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.project_id = ANY(ARRAY' + str(list(projectIds)) + ') ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) +  ');'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return isoCount[0][0]



def getIsolatesWithMFilters_auth_proj(qs_mgtIds, qs_locIds, qs_islnIds, isoSearchStr, offset, limit, projectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	queryStr = 'SELECT ' + pvStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id WHERE i.project_id = ANY(ARRAY' + str(projectIds) + ') ' + isoSearchStr +  ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) +  ') ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso


def getIsolatesWithMFilters_cnt(qs_mgtIds, qs_locIds, qs_islnIds, isoSearchStr, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	isoCount = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) +  ');'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return isoCount[0][0]



def getIsolatesWithMFilters(qs_mgtIds, qs_locIds, qs_islnIds, isoSearchStr, offset, limit, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	queryStr = 'SELECT ' + puStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' ' + isoSearchStr +  ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) +  ') ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso

def getIsolatesWithMfromView_auth_cnt(qs_mgtIds, isoSearchStr, userProjectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	count = 0

	# public and not in user projects
	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_l.id  WHERE i.privacy_status = \'PU\' ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +');'

	if len(userProjectIds) > 0:
		 queryStr = queryStr + ' and i.project_id != ALL(ARRAY' + str(userProjectIds) + ')'

	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	# only in user projects
	count = int(isoCount[0][0])

	if len(userProjectIds) > 0:
		count = count + getIsolatesWithMfromView_auth_proj_cnt(qs_mgtIds, isoSearchStr, userProjectIds, org)


	return count


def getIsolatesWithMfromView_auth(qs_mgtIds, isoSearchStr, offset, limit, userProjectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];
	# public and not in user projects
	queryStr = 'SELECT ' + pvStart_projHidden + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id  LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_l.id  WHERE i.privacy_status = \'PU\' ' + isoSearchStr +' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +')'


	# only in user projects
	if len(userProjectIds) > 0:
		queryStr = queryStr + ' AND i.project_id != ALL(ARRAY' + str(userProjectIds) + ') '

		queryStr = queryStr + ' UNION ALL(SELECT ' + pvStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_l.id  WHERE i.project_id = ANY(ARRAY' + str(userProjectIds) + ') ' + isoSearchStr +' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +'))'

	queryStr = queryStr + ' ORDER BY server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'

	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise



	return iso


def getIsolatesWithMfromView_auth_proj_cnt(qs_mgtIds, isoSearchStr, projectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	isoCount = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_l.id  WHERE i.project_id = ANY(ARRAY' + str(projectIds) + ') ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +');'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return isoCount[0][0]


def getIsolatesWithMfromView_auth_proj(qs_mgtIds, isoSearchStr, offset, limit, projectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	queryStr = 'SELECT ' + pvStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_l.id  WHERE i.project_id = ANY(ARRAY' + str(projectIds) + ') ' + isoSearchStr +' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso



def getIsolatesWithMfromView_cnt(qs_mgtIds, isoSearchStr, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	isoCount = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_l.id  WHERE i.privacy_status=\'PU\' ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +');'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return isoCount[0][0]


def getIsolatesWithMfromView(qs_mgtIds, isoSearchStr, offset, limit, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	queryStr = 'SELECT ' + puStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_l.id  WHERE i.privacy_status=\'PU\' ' + isoSearchStr +' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso



def getIsolatesWithMmgtsIsln_auth_cnt(qs_mgtIds, qs_islnIds, isoSearchStr, userProjectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	count = 0
	isoCount = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' AND i.project_id != ALL(ARRAY' + str(userProjectIds) + ') ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ');'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	count = isoCount[0][0] + getIsolatesWithMmgtsIsln_auth_proj_cnt(qs_mgtIds, qs_islnIds, isoSearchStr, userProjectIds, org)

	return count



def getIsolatesWithMmgtsIsln_auth(qs_mgtIds, qs_islnIds, isoSearchStr, offset, limit, userProjectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	# public and not in user projects
	queryStr = 'SELECT ' + pvStart_projHidden + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id WHERE i.privacy_status = \'PU\' AND i.project_id != ALL(ARRAY' + str(userProjectIds) + ') ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ')'

	# user projects only
	if len(userProjectIds) > 0:
		queryStr = queryStr + 'UNION ALL(SELECT ' + pvStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id WHERE i.project_id = ANY(ARRAY' + str(userProjectIds) + ') ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + '))'


	queryStr = queryStr + ' ORDER BY server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'

	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso




def getIsolatesWithMmgtsIsln_auth_proj_cnt(qs_mgtIds, qs_islnIds, isoSearchStr, projectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	isoCount = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.project_id = ANY(ARRAY' + str(projectIds) + ') ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ');'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return isoCount[0][0]



def getIsolatesWithMmgtsIsln_auth_proj(qs_mgtIds, qs_islnIds, isoSearchStr, offset, limit, projectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	queryStr = 'SELECT ' + pvStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id WHERE i.project_id = ANY(ARRAY' + str(projectIds) + ') ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso



def getIsolatesWithMmgtsIsln_cnt(qs_mgtIds, qs_islnIds, isoSearchStr, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	isoCount = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ');'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return isoCount[0][0]



def getIsolatesWithMmgtsIsln(qs_mgtIds, qs_islnIds, isoSearchStr, offset, limit, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	queryStr = 'SELECT ' + puStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' LEFT JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_i.id = ANY(ARRAY' + str(list(qs_islnIds)) + ') ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso




def getIsolatesWithMmgtsLocs_auth_cnt(qs_mgtIds, qs_locIds, isoSearchStr, userProjectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	isoCount = 0;
	count = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' AND i.project_id != ALL(ARRAY' + str(userProjectIds) + ') ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) + ');'

	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	count = isoCount[0][0] + getIsolatesWithMmgtsLocs_auth_proj_cnt(qs_mgtIds, qs_locIds, isoSearchStr, userProjectIds, org)

	return count

def getIsolatesWithMmgtsLocs_auth(qs_mgtIds, qs_locIds, isoSearchStr, offset, limit, userProjectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	queryStr = 'SELECT ' + pvStart_projHidden + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id WHERE i.privacy_status = \'PU\' AND i.project_id != ALL(ARRAY' + str(userProjectIds) + ') ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) + ')'


	if len(userProjectIds) > 0:
		queryStr = queryStr + 'UNION ALL(SELECT ' + pvStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id WHERE i.project_id = ANY(ARRAY' + str(userProjectIds) + ') ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) + '))'

	queryStr = queryStr + ' ORDER BY server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'

	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso



def getIsolatesWithMmgtsLocs_auth_proj_cnt(qs_mgtIds, qs_locIds, isoSearchStr, projectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	isoCount = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.project_id = ANY(ARRAY' + str(projectIds) + ') ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) + ');'

	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return isoCount[0][0]

def getIsolatesWithMmgtsLocs_auth_proj(qs_mgtIds, qs_locIds, isoSearchStr, offset, limit, projectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	queryStr = 'SELECT ' + pvStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id WHERE i.project_id = ANY(ARRAY' + str(projectIds) + ') ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) + ') ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'

	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso




def getIsolatesWithMmgtsLocs_cnt(qs_mgtIds, qs_locIds, isoSearchStr, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	isoCount = 0;

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) + ');'

	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		isoCount = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return isoCount[0][0]

def getIsolatesWithMmgtsLocs(qs_mgtIds, qs_locIds, isoSearchStr, offset, limit, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	iso = [];

	queryStr = 'SELECT ' + puStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id' + ' INNER JOIN '+ f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id  WHERE i.privacy_status=\'PU\' ' + isoSearchStr + ' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +') and iM_l.id = ANY(ARRAY' + str(list(qs_locIds)) + ') ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'

	try:
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()
	except:
		sys.stderr.write("Error: came across error \n")
		raise

	return iso




def getIsolates_srch(searchStr, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	c = connections[f'{org.lower()}'].cursor()

	queryStr = 'SELECT ' + puStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id WHERE i.privacy_status=\'PU\' ORDER BY i.server_status;'


	c.execute(queryStr)
	iso = c.fetchall()

	db_cols = list()
	for i in c.description:
		db_cols.append(i[0])

	c.close()

	return iso


def getAllPvProjIsolates(offset, limit, projectId, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	c = connections[f'{org.lower()}'].cursor()

	queryStr = 'SELECT ' + pvStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_project\" as p" +' ON i.project_id = p.id LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id WHERE i.project_id=\'' + projectId + '\' ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	c.execute(queryStr)
	iso = c.fetchall()

	db_cols = list()
	for i in c.description:
		db_cols.append(i[0])

	c.close()

	return iso


def getAllPuIsolates(offset, limit, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	c = connections[f'{org.lower()}'].cursor()

	queryStr = 'SELECT ' + puStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id WHERE i.privacy_status=\'PU\' ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	c.execute(queryStr)
	iso = c.fetchall()

	db_cols = list()
	for i in c.description:
		db_cols.append(i[0])

	c.close()

	return iso


def getAndAddProjectIds(username, str, arr_projs, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	projs = []

	try:
		user = User.objects.get(userId=username)


		projs = list(user.project_set.filter(identifier__icontains=str).values_list('id', flat=True))

	except:
		sys.stderr.write("User, or projects not in database " + username + '\n');
		pass

	arr_projs = arr_projs + projs
	print(arr_projs)
	return (arr_projs)


def getAndAddProjectIdsExact(username, str, arr_projs, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	user = User.objects.get(userId=username)
	projs = list(user.project_set.filter(identifier=str).values_list('id', flat=True))

	# print ("Projects !!! ")
	# print (projs)
	arr_projs = arr_projs + projs

	return (arr_projs)


def getUserProjectIds(username, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	projects = []

	try:
		userObj = User.objects.get(userId=username)
		projects = list(userObj.project_set.values_list('id', flat=True))
	except:
		# raise
		pass
		# user has never created a project for this organism before!.

	return (projects)



def getAllPuAndUserPvIsolates(offset, limit, username, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	projects = [];

	try:
		user = User.objects.get(userId=username)
		projects = list(user.project_set.values_list('id', flat=True))


	except:
		pass

	c = connections[f'{org.lower()}'].cursor()

	queryStr = '(SELECT ' + pvStart_projHidden + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id WHERE i.privacy_status=\'PU\''




	if len(projects) > 0:
		queryStr = queryStr + 'AND i.project_id != All(ARRAY' + str(projects) + '))';


	else:
		queryStr = queryStr + ')'


	if len(projects) > 0:
		queryStr = queryStr + 'UNION ALL (SELECT ' + pvStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id WHERE i.project_id = ANY(ARRAY' + str(projects) + '))'



	queryStr = queryStr + 'ORDER BY server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'

	c.execute(queryStr)
	iso = c.fetchall()

	db_cols = list()
	for i in c.description:
		db_cols.append(i[0])

	c.close()

	return iso



def getAllPuIsolates_cnt(org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	return Isolate.objects.filter(privacy_status='PU').count();

def userIsolate_cnt(username, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	try:
		user = User.objects.get(userId=username)
	except:
		# raise
		print("Username " + username + " not found in database");
		return 0

	projects = user.project_set.all()

	return Isolate.objects.filter(project__pk__in=projects, privacy_status='PV').count()



def getAllPvProjIso_cnt(projectId, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)

	return Isolate.objects.filter(project=projectId).count();


def getIsolatesWithIsoParam(isoSearchStr, offset, limit, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	c = connections[f'{org.lower()}'].cursor()

	queryStr = 'SELECT ' + puStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id WHERE i.privacy_status=\'PU\' ' + isoSearchStr + ' ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	c.execute(queryStr)
	iso = c.fetchall()

	db_cols = list()
	for i in c.description:
		db_cols.append(i[0])

	c.close()

	return iso



def getIsolatesWithIsoParam_auth_proj_cnt(isoSearchStr, projectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	c = connections[f'{org.lower()}'].cursor()

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id WHERE i.project_id = ANY(ARRAY' + str(projectIds) + ') ' + isoSearchStr + ';'


	c.execute(queryStr)
	iso = c.fetchall()

	db_cols = list()
	for i in c.description:
		db_cols.append(i[0])

	c.close()

	return iso[0][0]

def getIsolatesWithIsoParam_auth_proj(isoSearchStr, offset, limit, projectIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	c = connections[f'{org.lower()}'].cursor()

	queryStr = 'SELECT ' + pvStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id WHERE i.project_id = ANY(ARRAY' + str(projectIds) + ') ' + isoSearchStr + ' ORDER BY i.server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	c.execute(queryStr)
	iso = c.fetchall()

	db_cols = list()
	for i in c.description:
		db_cols.append(i[0])

	c.close()

	return iso



def getIsolatesWithIsoParam_auth_cnt(isoSearchStr, userProjIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	count = 0

	c = connections[f'{org.lower()}'].cursor()

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id WHERE i.privacy_status=\'PU\' ' + isoSearchStr

	if len(userProjIds) > 0:
		queryStr = queryStr + ' AND i.project_id != ALL(ARRAY' + str(userProjIds) + ');'


	c.execute(queryStr)
	iso = c.fetchall()

	db_cols = list()
	for i in c.description:
		db_cols.append(i[0])

	c.close()

	count = int(iso[0][0])

	if len(userProjIds) > 0:
		count = count + int(getIsolatesWithIsoParam_auth_proj_cnt(isoSearchStr, userProjIds, org))

	return (count)

def getIsolatesWithIsoParam_auth(isoSearchStr, offset, limit, userProjIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	c = connections[f'{org.lower()}'].cursor()

	# public and exclude all user projects
	queryStr = 'SELECT ' + pvStart_projHidden + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id WHERE i.privacy_status=\'PU\' ' + isoSearchStr




	# only user projects
	if len(userProjIds) > 0:
		queryStr = queryStr + 'and i.project_id != ALL(ARRAY' + str(userProjIds) + ')'

		queryStr = queryStr + 'UNION ALL(SELECT ' + pvStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_project\" as p" + ' ON i.project_id = p.id LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id WHERE i.project_id = ANY(ARRAY' + str(userProjIds) + ') ' + isoSearchStr + ')'


	queryStr = queryStr + ' ORDER BY server_status OFFSET ' + str(offset) + ' LIMIT ' + str(limit) + ';'


	c.execute(queryStr)
	iso = c.fetchall()

	c.close()





	return (iso)




def getIsolatesWithIsoParam_cnt(isoSearchStr, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	c = connections[f'{org.lower()}'].cursor()

	queryStr = 'SELECT count(*) FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id WHERE i.privacy_status=\'PU\' ' + isoSearchStr + ';'


	c.execute(queryStr)
	iso = c.fetchall()

	db_cols = list()
	for i in c.description:
		db_cols.append(i[0])

	c.close()

	return iso[0][0]


def getIsolatesWithMgtIds(qs_mgtIds, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	iso = [];

	queryStr = 'SELECT ' + puStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id WHERE i.privacy_status=\'PU\' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +')' + ' ORDER BY i.server_status LIMIT 1000;'

	# old: 'SELECT i.id, i.identifier, i.server_status, v.* from "Salmonella_isolate" as i, "Salmonella_view_apcc" as v where i.mgt_id = v.mgt_id and i.privacy_status=\'PU\' and v.mgt_id = ANY(ARRAY' +  str(list(qs_mgtIds)) +')'

	if (len(qs_mgtIds) > 0):
		c = connections[f'{org.lower()}'].cursor()
		c.execute(queryStr)
		iso = c.fetchall()
		c.close()

	return iso


def getIsolatesWithWhere(fieldName, val, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	c = connections[f'{org.lower()}'].cursor()

	queryStr = 'SELECT ' + puStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id WHERE i.privacy_status=\'PU\' and i.'+ fieldName + ' ILIKE \'' + val + '%\' ORDER BY i.server_status LIMIT 1000;'

	c.execute(queryStr)
	iso = c.fetchall()

	c.close()


	return iso


#################### ISO_METADATA TABLE SEARCHES

def getIsolatesWithLoc(fieldName, val, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	c = connections[f'{org.lower()}'].cursor()

	queryStr = 'SELECT ' + puStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id AND (iM_l.' + fieldName + ' ILIKE \'' + val + '%\') LEFT JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id WHERE i.privacy_status=\'PU\' ORDER BY i.server_status LIMIT 1000;'

	# print (queryStr)
	# i.'+ fieldName + ' LIKE \'' + val + '%\'
	c.execute(queryStr)
	iso = c.fetchall()

	c.close()

	return iso


def getIsolatesWithIsln(fieldName, val, org):
	View_apcc, Location, Isolation, Isolate, User = getModels(org)
	c = connections[f'{org.lower()}'].cursor()

	queryStr = 'SELECT ' + puStart + ' FROM ' + f"\"{org}_isolate\" as i"  + ' INNER JOIN ' + f"\"{org}_isolation\" as iM_i" + ' ON i.isolation_id = iM_i.id AND (iM_i.' + fieldName + ' ILIKE \'' + val + '%\') LEFT JOIN ' + f"\"{org}_location\" as iM_l" + ' ON i.location_id = iM_l.id LEFT JOIN ' + f"\"{org}_view_apcc\" as v" + ' ON i.mgt_id = v.mgt_id WHERE i.privacy_status=\'PU\'  ORDER BY i.server_status LIMIT 1000;'


	# print (queryStr)
	# i.'+ fieldName + ' LIKE \'' + val + '%\'
	c.execute(queryStr)
	iso = c.fetchall()

	c.close()

	return iso

def getModels(org):
    models = importlib.import_module(f'{org}.models')
    View_apcc = models.View_apcc
    Location = models.Location 
    Isolation = models.Isolation 
    Isolate = models.Isolate 
    User = models.User 
    
    return View_apcc, Location, Isolation, Isolate, User 
