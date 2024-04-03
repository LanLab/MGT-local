from . import rawQueries
import datetime
from django_countries import countries
from . import queryDb as q
import importlib
# from Salmonella.models import Tables_ap, Tables_cc, Project

def getDataForReport(username, selCountry, selProj, isAuth, yearStart, yearEnd, org):
	Tables_ap, Tables_cc, Project = getModels(org)

	userProjIds = []; country_name = None; dict_dataForReport = dict(); list_tabAps = []; list_tabCcs = []; project_name = None;
	isSelCountry = False
	if selCountry != None and selCountry != '' and selCountry != 'null':

		country_name = dict(countries)[selCountry]
		isSelCountry = True

	if selProj != None and selProj != '' and selProj != 'null' and username != None:
		# print ("The project");

		userProjIds = q.getUserProjectIds(username, org)

		if (int(selProj) not in userProjIds):
			print (selProj)
			print(userProjIds)
			print ("Error: you are trying to access a project that is not your own")
			return dict_dataForReport;
		# check if selProj in usrProjIds;
		# print (userProjIds)
		project_name = Project.objects.filter(id=selProj).get().identifier



	now = yearEnd # datetime.datetime.now()
	year_10Ago = yearStart # now.year - 10

	list_tabAps = list(Tables_ap.objects.filter(table_num=0).order_by('display_order').values('table_name', 'display_name', 'scheme_id'))

	list_tabCcs = list(Tables_cc.objects.all().values('table_name', 'display_name', 'scheme_id').order_by('display_table', 'display_order'))

	res = getData(year_10Ago, now, country_name, selProj, userProjIds, isAuth, list_tabAps, list_tabCcs, org)

	dict_dataForReport['isolates'] = res[0]
	dict_dataForReport['cols'] = res[1]
	dict_dataForReport['tabAps'] = list_tabAps
	dict_dataForReport['tabCcs'] = list_tabCcs
	#dict_dataForReport['yearCurr'] = now.year
	#dict_dataForReport['year_10Ago'] = year_10Ago
	dict_dataForReport['yearCurr'] = yearEnd
	dict_dataForReport['year_10Ago'] = yearStart
	dict_dataForReport['isSelCountry'] = isSelCountry
	dict_dataForReport['country'] = country_name
	dict_dataForReport['project_name'] = project_name

	# print("original time " + str(now.year) + ' ' + str(year_10Ago))
	print(dict_dataForReport)

	return dict_dataForReport


def getData(year_10Ago, yearCurr, selCountry, selProj, userProjIds, isAuth, list_tabAps, list_tabCcs, org):
	Tables_ap, Tables_cc, Project = getModels(org)
	queryStr = "select i.identifier, iM_i.year, iM_i.month, iM_l.country "

	if selCountry:
		queryStr = queryStr + ", iM_l.state"

	for tabApObj in list_tabAps:
		queryStr = queryStr + ", v." + tabApObj['table_name'] +"_st"

	for tabCcObj in list_tabCcs:
		queryStr = queryStr + ", " + tabCcObj['table_name']

	queryStr = queryStr + " from " + f"\"{org}_isolate\" as i" + ", " + f"\"{org}_view_apcc\" as v" + ", " + f"\"{org}_isolation\" as iM_i" + ", " + f"\"{org}_location\" as iM_l"

	queryStr = queryStr + " where i.mgt_id = v.mgt_id and iM_i.id = i.isolation_id and i.location_id = iM_l.id and iM_i.year >= " + str(year_10Ago) + " and iM_i.year <= " + str(yearCurr) ;

	if selCountry:
		if selCountry == 'United States of America': 
			# print("(4) - now also USA")
			queryStr = queryStr + " and (iM_l.country LIKE '%" + selCountry + "%' or iM_l.country LIKE '%USA%') "

		else: 
			queryStr = queryStr + " and iM_l.country LIKE '%" + selCountry + "%'";

	queryStr = queryStr + addWhereIsAuthPart_1(isAuth, selProj, userProjIds, org)

	print (queryStr)

	(isolates, columns) = rawQueries.executeQuery_table(queryStr, org)

	# print (isolates)
	return (isolates, columns)


def addWhereIsAuthPart_1(isAuth, selProj, userProjIds, org):
	Tables_ap, Tables_cc, Project = getModels(org)
	queryStr = ''

	if not isAuth:
		queryStr = " and i.privacy_status='PU' "
	elif isAuth and selProj: # user selected a project
		queryStr = " and i.project_id=" + selProj
	elif isAuth and selProj == None and len(userProjIds) > 0: # user did not select a project
		queryStr = " and (i.privacy_status='PU' or i.privacy_id = ANY(ARRAY" + str(userProjIds) + ")"

	return queryStr



	year_3Ago = now.year - 3


	# Chart 1
	# bar chart data
	res = getIsoCntPerYear_1_1(year_10Ago, country_name, selProj, userProjIds, isAuth)
	dict_dataForReport['1_1_data'] = res[0]
	dict_dataForReport['1_1_cols'] = res[1]



	# line chart data
	res = getMgtCntPerYear_1_2(year_10Ago, country_name, selProj, userProjIds, isAuth)
	dict_dataForReport['1_2_data'] = res[0]
	dict_dataForReport['1_2_cols'] = res[1]


	# Chart 2
	res = getPastNYearLocInfo_2(year_3Ago, country_name, selProj, userProjIds, isAuth)
	dict_dataForReport['2_data'] = res[0]
	dict_dataForReport['2_cols'] = res[1]


	# Table 1 (3)
	list_tabAps = list(Tables_ap.objects.filter(table_num=0).order_by('display_order').values('table_name', 'display_name'))

	getStDataForTbl1_3(year_3Ago, now.year, country_name, selProj, userProjIds, isAuth, list_tabAps)


	return dict_dataForReport

def getModels(org):
    models = importlib.import_module(f'{org}.models')
    Tables_ap = models.Tables_ap
    Tables_cc = models.Tables_cc
    Project = models.Project
    
    return Tables_ap, Tables_cc, Project