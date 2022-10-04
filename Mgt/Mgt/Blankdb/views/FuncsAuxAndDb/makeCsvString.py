
from Blankdb.models import Isolate, View_apcc, Tables_ap, Tables_cc
from Blankdb.views.FuncsAuxAndDb import constants as c
from django.views.decorators.csrf import csrf_exempt
import io,csv
from django.http import HttpResponse
import re

def convertToCsv(list_colsInfo, isolates):

	buffer = io.StringIO()
	wr = csv.writer(buffer, quoting=csv.QUOTE_ALL)
	wr.writerow(list_colsInfo)
	wr.writerows(isolates)

	buffer.seek(0)
	response = HttpResponse(buffer, content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="isolates.csv"'

	return response

@csrf_exempt
def makeCsv(isolates, isAuth, list_colsInfo):
	"""
	Make tab separated string from search results so return to user through ajax
	:param isolates:
	:return:
	"""

	(header, colNums, list_apTns, list_ccTns, dict_apCols, dict_ccCols, colNums_md, col_serverStatus, col_assignStatus) = extractTheHeader(list_colsInfo)

	outStr = "\t".join(header) + "\n"

	for isolate in isolates:
		if isolate[col_serverStatus] == 'C' and isolate[col_assignStatus] == 'A':

			# Adding the isolate cols
			for i in range(0, len(colNums)):
				outStr = outStr + str(isolate[colNums[i]])

				if i < len(colNums)-1:
					outStr = outStr + "\t"


			# Adding the ap cols
			for tn in list_apTns:
				(col_st, col_dst) = dict_apCols[tn]

				outStr = outStr + "\t"
				
				if isolate[col_st]:
					outStr = outStr + str(isolate[col_st])
					if isolate[col_dst] and isolate[col_dst] != 0:
						outStr = outStr + "." + str(isolate[col_dst])
				# outStr = outStr +


			# Adding the cc and epi cols
			for tn in list_ccTns:
				ccVal = None

				for ccCol in dict_ccCols[tn]:

					if isolate[ccCol]:
						if ccVal == None or isolate[ccCol] < ccVal:

							ccVal = isolate[ccCol]


				outStr = outStr + "\t"

				if ccVal != None:
					outStr = outStr + str(ccVal)
				# outStr = outStr +


			# Location and isolation
			for colNum in colNums_md:

				outStr = outStr + "\t"
				if isolate[colNum]:
					outStr = outStr + str(isolate[colNum])


			outStr = outStr + "\n"

	return outStr



def extractTheHeader (list_colsInfo):

	header = []; header_md = [];
	colNums = [] # general column numbers
	colNums_md = [] # column nums for metadata (location & isolation)
	col_serverStatus = -1; col_assignment_status = -1; # for checking

	dict_apCols = {}; # dict_{tableName} => [st, dst]
	list_apTns = []; # [tableName, ...]

	dict_ccCols = {}; # dict_{tableName} => [cc, ccMerge] (the Values are just appended here, as we just want the min).
	list_ccTns = []; # [tableName, ...]

	for colObj in list_colsInfo:
		# print(colObj['table_name'] + "\t" + colObj['display_name'])

		if (colObj['table_name'] == 'identifier' and colObj['display_name'] == 'Isolate') or (colObj['table_name'] == 'mgt1'):
			header.append(colObj['display_name'])
			colNums.append(colObj['db_col'])

		elif colObj['table_name'] == 'server_status':
			# print (colObj)
			col_serverStatus = colObj['db_col']

		elif colObj['table_name'] == 'assignment_status':
			col_assignment_status = colObj['db_col']

		# APs
		elif re.match('^ap[0-9]+_[0-9]+$', colObj['table_name']):
			# print (colObj['table_name'])
			dict_apCols[colObj['table_name']] = [None, None]
		elif re.match('^ap[0-9]+_[0-9]+_st$', colObj['table_name']):
			#print (colObj['table_name'])
			tn = re.sub('_st$', '', colObj['table_name'])
			dict_apCols[tn][0] = colObj['db_col']
			#print('Clean tn ' + tn)
		elif re.match('^ap[0-9]+_[0-9]+_dst$', colObj['table_name']):
			#print (colObj['table_name'])
			tn = re.sub('_dst$', '', colObj['table_name'])
			dict_apCols[tn][1] = colObj['db_col']
			#print('Clean dst tn ' + tn)


		# CCs
		elif re.match('^cc[0-9]+_[0-9]+$', colObj['table_name']):
			#print (colObj['table_name'])
			# tn = re.sub('_dst$', '', colObj['table_name'])
			if (colObj['table_name'] not in dict_ccCols):
				dict_ccCols[colObj['table_name']] = []


			dict_ccCols[colObj['table_name']].append(colObj['db_col'])

		elif re.match('^cc[0-9]+_[0-9]+_merge$', colObj['table_name']):
			print (colObj['table_name'])

			tn = re.sub('_merge$', '', colObj['table_name'])


			if (tn not in dict_ccCols):
				dict_ccCols[tn] = []


			dict_ccCols[tn].append(colObj['db_col'])



		# Locs and Isolation
		elif colObj['t_search'] == 'iM_i' or colObj['t_search'] == 'iM_l':
			if colObj['table_name'] != 'id':
				print (colObj);
				header_md.append(colObj['display_name'])
				colNums_md.append(colObj['db_col'])
		else:
			# print(colObj)
			pass
		# if re.match('^ap.*_st'colObj['table_name']


	# add MGT levels for ST headers
	qs_tablesAp = Tables_ap.objects.filter(table_num=0).order_by('display_order').values('table_name', 'scheme__display_name')
	for i in qs_tablesAp:
		header.append(i['scheme__display_name'])
		list_apTns.append(i['table_name'])

	# add MGT_CC for CC headers
	qs_tablesCc = Tables_cc.objects.filter(display_table=1).values('table_name', 'display_name').order_by(
	    'display_order')
	for i in qs_tablesCc:
		header.append(i['display_name'])
		list_ccTns.append(i['table_name'])

	#add ODC names as headers
	qs_tablesEpi = Tables_cc.objects.filter(display_table=2).values('table_name', 'display_name').order_by(
	    'display_order')
	for i in qs_tablesEpi:
		header.append(i['display_name'])
		list_ccTns.append(i['table_name'])


	header = header + header_md


	print(header)

	print(colNums)

	print(dict_apCols)
	print(dict_ccCols)

	print (list_apTns)
	print (list_ccTns)

	print (colNums_md)


	return (header, colNums, list_apTns, list_ccTns, dict_apCols, dict_ccCols, colNums_md, col_serverStatus, col_assignment_status)
