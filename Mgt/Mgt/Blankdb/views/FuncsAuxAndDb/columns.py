import re

from Blankdb.models import Isolate, View_apcc, Location, Isolation, Tables_cc, Tables_ap


def columns(isAuth):

	list_isoAndMeta = list()

	list_isoAndMeta = addColsInfoToList(list_isoAndMeta, Isolate._meta.fields, 'Isolate', isAuth)
	list_isoAndMeta = addColsInfoToList(list_isoAndMeta, Location._meta.fields, 'Location', isAuth)
	list_isoAndMeta = addColsInfoToList(list_isoAndMeta, Isolation._meta.fields, 'Isolation', isAuth)


	list_tabAps = list(Tables_ap.objects.filter(table_num=0).values('table_name', 'display_order', 'display_name'))

	list_tabCcs = list(Tables_cc.objects.all().values('table_name', 'display_table', 'display_order', 'display_name'))

	return (list_isoAndMeta, list_tabAps, list_tabCcs)



def addColsInfoToList(list_, theFields, group, isAuth):

	for fld in theFields:
		dbColName = fld.get_attname_column()[1] # tuple(name_in_model, name_in_db)

		if dbColName == 'project_id':
			dbColName = 'project'

		if dbColName in ['file_forward', 'file_reverse', 'file_alleles', 'tmpFn_alleles', 'file_assembly']:
			continue

		if re.search('\_id$', dbColName) or dbColName == 'id' or dbColName in ['date_created', 'date_modified']:
			print("Need to remove the id col")
			continue

		if isAuth == False and dbColName in ['project', 'privacy_status', 'isQuery']:
			continue

		if re.search("dst$", dbColName) or re.search("merge$", dbColName):
			continue


		if group == None and re.search('st$', dbColName):
			group = 'Sequence types'

		# if group == None and re.search()


		dict_cols = dict()
		dict_cols['display_name'] = fld.verbose_name
		dict_cols['table_name'] = dbColName
		dict_cols['group'] = group

		list_.append(dict_cols)

	return(list_)


def getApColsForDisplay(db_cols, apCols, prependStart, prependEnd):
	# print (db_cols)
	list_colsToDisp = list()
	list_dispNames = list()

	for apTn in apCols:
		print (apTn)

		st = apTn['table_name'] + "_st"
		dst = apTn['table_name'] + "_dst"

		if st in db_cols:
			list_colsToDisp.append(db_cols.index(st))
			list_dispNames.append(apTn['scheme__display_name'])

		if dst in db_cols:
			list_colsToDisp.append(db_cols.index(dst))


	for i in range(prependEnd, prependStart-1, -1):
		list_colsToDisp.insert(0, i)
		list_dispNames.insert(0, db_cols[i])


	# print (list_dispNames)

	# print (list_colsToDisp)
	return (list_colsToDisp, list_dispNames)
