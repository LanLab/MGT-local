
# from Salmonella.models import Tables_ap, Mgt
import importlib
from django.apps import apps
from django.core import serializers
from . import rawQueries

from django.apps import apps
import re
import io,csv
from django.http import HttpResponse

def convertToCsv_ap9(isolates, mgtId_ap9Id, dict_tabRows_byAp9Id, colNamesCombined, isGrapeTree, org):
	Tables, Mgt = getModels(org)
	buffer = io.StringIO()
	wr = csv.writer(buffer, quoting=csv.QUOTE_NONE, delimiter='|', quotechar='')

	if len(mgtId_ap9Id) > 0:

		if isGrapeTree: 
			wr.writerow(["#Isolate\t"+colNamesCombined])
		else: 
			wr.writerow(["Isolate\t"+colNamesCombined])


		# print (dict_tabRows_byAp9Id.keys())

		for (isoId, isolate, mgtId) in isolates:

			ap9Id = get_values(mgtId_ap9Id, mgtId)

			if (ap9Id in dict_tabRows_byAp9Id.keys()):
				# print("Found " + str(ap9Id))
				wr.writerow([isolate + '\t' + dict_tabRows_byAp9Id[ap9Id]])
				# print(dict_tabRows_byAp9Id[ap9Id])

			# print (mgtId, ap9Id)



	else:
		wr.writerow(["Isolate,"])

		if (len(isolates) > 0):
			print(isolates);
			for (isoId, isolate, mgtId) in isolates:
				wr.writerow([isolate + '\tNo_allelic_profile_available'])



	buffer.seek(0)
	response = HttpResponse(buffer, content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="allelic_profiles.tsv"'


	return response



def get_values(iterables, key_to_find):
	# return list(filter(lambda x:key_to_find in x[1], iterables))
	for item in iterables:
		if item[0] == key_to_find:
			return item[1]


def getTheDataMgt9Aps(isolates, list_colsInfo, isGrapeTree, org):
	Tables, Mgt = getModels(org)

	# get mgt_id col. num.
	mgtIdColNum = getMgtIdColNum(list_colsInfo)
	print("################# mgtIdColNum")
	print(list_colsInfo)
	# print(mgtIdColNum)


	theMgtIds_inIso = [item[mgtIdColNum] for item in isolates]
	# print(theMgtIds_inIso)

	# print("The isolates:")
	# print(isolates)
	# print("The mgt ids")
	# print(forDownload_mgtIds)

	(mgtId_ap9Id, list_tabRows_byAp9Id, colNamesCombined) = getMgt9Aps_v2(theMgtIds_inIso, isGrapeTree, org)

	# print(mgtId_ap9Id)



	return (mgtId_ap9Id, list_tabRows_byAp9Id, colNamesCombined)

	# from django.core import serializers
	# import json
	# print("The list tab rows:")
	# print(list_tabRows)
	# arrTabRows = json.dumps({"data": list_tabRows})

	# return (list_tabRows, mgtId_ap9Id, isolates)


def getMgtIdColNum(list_colsInfo):

	for d_ in list_colsInfo:
		if d_['table_name'] == 'mgt_id':
			return d_['db_col']


def getLargestSchemeId(org): 
	Tables_ap, Mgt = getModels(org)
	largestScheme = Tables_ap.objects.filter(table_num=0).order_by('-display_order').first() 
	return (largestScheme.scheme_id, largestScheme.table_name) 


def getTablesMgt9AsList(largestSchemeId, org):
	Tables_ap, Mgt = getModels(org)
	tablesMgt9Res = Tables_ap.objects.filter(scheme_id=largestSchemeId).order_by('table_num').values_list('table_name')

	tablesMgt9 = [item[0] for item in tablesMgt9Res]

	return tablesMgt9



def getTheAp9IdsFromMgt(theMgtIds, largestScheme_tn, org):
	Tables, Mgt = getModels(org)
	mgtId_ap9Id = Mgt.objects.filter(id__in=theMgtIds).values_list('id', largestScheme_tn) # 'ap9_0_id')

	list_ap9Id = [item[1] for item in mgtId_ap9Id] # [1] == getting only the ap9_0_id

	return(mgtId_ap9Id, list_ap9Id)



def getMgt9Aps_v2(theMgtIds, isGrapeTree, org):
	Tables, Mgt = getModels(org)
	(largestSchemeId, largestScheme_tn) = getLargestSchemeId(org)

	tablesMgt9 = getTablesMgt9AsList(largestSchemeId, org)
	(mgtId_ap9Id, list_ap9Id) = getTheAp9IdsFromMgt(theMgtIds, largestScheme_tn, org)

	print("The mgtId_ap9Id is ");
	print(len(mgtId_ap9Id))
	print("The list ap9Id is ");
	print(len(list_ap9Id))

	dict_allelicProfiles = dict()
	colNamesCombined = []

	print("===============")
	print(len(list_ap9Id));
	# list_ap9Id.remove(None)
	list_ap9Id = [s for s in list_ap9Id if s != None]
	print(len(list_ap9Id));


	if (len(mgtId_ap9Id) > 0 and len(list_ap9Id) > 0):
		(theAP9, columns) = buildQueryAndGetData(tablesMgt9, list_ap9Id, org);
		list_cols = getTheHeader(tablesMgt9, org);

		#print("The column are:")
		#print(columns)
		#print(theAP9)

		(idPos, toExludePositions) = getMg9ApColumnNames_v2(list_cols, isGrapeTree, org)
		# print(toExludePositions)
		# print(colNamesCombined);
		# (idPos, toExludePositions, colNamesCombined) = getMg9ApColumnNames(list_cols)
		# print(colNamesCombined);
		# print(toExludePositions);
		# print(sorted(toExludePositions, reverse=True))
		(dict_allelicProfiles, colNamesCombined) = cleanUpRows(toExludePositions, idPos, theAP9, list_cols, isGrapeTree, org)

	# print(theAP9[0])
	# theAP9.insert(0, colNamesCombined)
	# print(colNamesCombined)
	# print(theAP9[0])

	return (mgtId_ap9Id, dict_allelicProfiles, colNamesCombined)



def cleanUpRows(toExludePositions, idPos, isolates, list_cols, isGrapeTree, org):
	Tables, Mgt = getModels(org)
	dict_allelicProfiles = {}

	for i in range(0,len(isolates)):
		# isolate = isolate.replace('(', '')

		isolate = ",".join(isolates[i])
		isolate = re.sub('[\(\)]+','', isolate)
		isoArr = isolate.split(",")


		# print(len(isoArr))

		key = isoArr[idPos]

		# toExludePositions.append(idPos)
		for idx in sorted(toExludePositions + [idPos], reverse=True):
			# print (idx);
			del isoArr[idx]

		if isGrapeTree:
			for i in range(2, len(isoArr)):
				isoArr[i] = re.sub('^-', '', isoArr[i])
				isoArr[i] = re.sub('\_[0-9]+$', '', isoArr[i])
		# print(len(isoArr))
		# isolates[i] = ",".join(isoArr)
		# isolates[i] = isoArr

		dict_allelicProfiles[int(key)] = "\t".join(isoArr)
		# print(isoArr)


	for idx in sorted(toExludePositions + [idPos], reverse=True):
		# print (idx);
		del list_cols[idx]


	colNamesCombined = "\t".join(list_cols);
	return (dict_allelicProfiles, colNamesCombined)


def buildQueryAndGetData(tablesMgt9, list_ap9Id, org):
	Tables, Mgt = getModels(org)
	queryStr = 'select'
	for i in range(0, len(tablesMgt9)):
		# queryStr = queryStr + ' "Salmonella_' + tablesMgt9[i]  + '"::text'
		queryStr = queryStr + ' "' + tablesMgt9[i]  + '"::text'

		if (i < len(tablesMgt9) - 1):
			queryStr = queryStr + ', '

	queryStr = queryStr + ' from '
	for i in range(0, len(tablesMgt9)):
		queryStr = queryStr + f' "{org}_' + tablesMgt9[i] + '" as "' + tablesMgt9[i] + '"'

		if (i < len(tablesMgt9) - 1):
			queryStr = queryStr + ', '

	queryStr = queryStr + '  where id = ANY(ARRAY' + str(list_ap9Id) + ') '

	for i in range(1, len(tablesMgt9)):
		queryStr = queryStr + ' and ' + tablesMgt9[i] + '.main_id = id'


	(theAP9, columns) = rawQueries.executeQuery_table(queryStr,org)
	return (theAP9, columns);

def getTheHeader(tablesMgt9, org):
	Tables, Mgt = getModels(org)
	print("Tables Mgt 9");
	print(tablesMgt9);
	list_cols = [];
	for i in range(0, len(tablesMgt9)):
		queryStr = f'select * from "{org}_' + tablesMgt9[i] + '" where false;'
		(theData, theCols) = rawQueries.executeQuery_table(queryStr,org)
		list_cols = list_cols + theCols;
		# print(theCols);

	return (list_cols)



def getMg9ApColumnNames_v2(list_cols, isGrapeTree, org):
	Tables, Mgt = getModels(org)
	allFieldsCounter = 0
	toExludePositions = [] # to delete from main

	# colNamesCombined = []

	#list_cols.reverse()
	for i in range(0, len(list_cols) ):
		if re.match('^id$', list_cols[i], flags=re.I):
			idPos = allFieldsCounter
			# print(aField.name);
		elif re.match('^main\_id$', list_cols[i], flags=re.I) or re.match("^date\_", list_cols[i], flags=re.I) or re.match("^cc[0-9]+\_[0-9]+\_id", list_cols[i], flags=re.I):
			toExludePositions.append(allFieldsCounter)
			print(str(i) + " " + list_cols[i])
		elif isGrapeTree == True and (re.match('^dst$', list_cols[i], flags=re.I) or re.match('^st$', list_cols[i], flags=re.I)):
			toExludePositions.append(allFieldsCounter);
			print ("Excluding column " + list_cols[i]);

		#else:
		# colNamesCombined.append(list_cols[i])



		allFieldsCounter = allFieldsCounter + 1



		# print(toExludePositions)
	# print(len(colNamesCombined))

	# convert colnames to string
	# colNamesCombined.reverse()
	# colNamesStr = ','.join(colNamesCombined)

	return (idPos, toExludePositions)# , colNamesStr)
	# return (toExludePositions, colNamesCombined)



def getMgt9Aps(theMgtIds, org):
	Tables, Mgt = getModels(org)
	list_tabRows = list()


	(mgtId_ap9Id, list_ap9Id) = getTheAp9IdsFromMgt(theMgtIds, org)

	# Get the ap9 tables (ordered!)
	tablesMgt9 = getTablesMgt9AsList(org)

	# For each table get the rows (and add to list...(?)

	for i in range(0, len(tablesMgt9)):

		theModel = apps.get_model(app_label=org, model_name=tablesMgt9[i])

		if i == 0:
			theRows = theModel.objects.filter(id__in=list_ap9Id)

			# print("The rows are:")
			# print(theRows)

		else:

			theRows = theModel.objects.filter(main_id__in=list_ap9Id)

		qs_json = serializers.serialize('json', theRows)

		list_tabRows.append(qs_json)




	# print("The list length is " + str(len(list_tabRows)))

	return (mgtId_ap9Id, list_tabRows)


def getModels(org):
    models = importlib.import_module(f'{org}.models')
    Tables_ap = models.Tables_ap
    Mgt = models.Mgt
    
    return Tables_ap, Mgt