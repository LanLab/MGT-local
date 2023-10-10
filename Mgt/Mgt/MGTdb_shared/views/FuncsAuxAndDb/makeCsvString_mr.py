
# from Salmonella.models import Isolate, View_apcc, Tables_ap, Tables_cc
from . import constants as c
from django.views.decorators.csrf import csrf_exempt
import io,csv
from django.http import HttpResponse
import re
import requests
from django_countries import countries
# import matplotlib.cm as cm
import json
import operator
import math
import random

from functools import partial
from geopy.geocoders import Nominatim

def makeCsv_andSendToMr(isolates, isAuth, list_colsInfo, org):
	Isolate, View_apcc, Tables_ap, Tables_cc = getModels(org)

	geolocator = Nominatim(user_agent='mgtdb.unsw.edu.au')
	outStr = makeCsv_microreact(isolates, isAuth, list_colsInfo, geolocator, org)

	# outStr = makeCsv_microreact(isolates, isAuth, list_colsInfo)

	dict_dataForMr = {}
	dict_dataForMr['name'] = 'MGT';
	dict_dataForMr['website'] = 'https://mgtdb.unsw.edu.au';
	dict_dataForMr['data'] = outStr
	dict_dataForMr['map_countryField'] = 'countryField'
	dict_dataForMr['timeline_grouped'] = True
	dict_dataForMr['map_style'] = 'bright'
	dict_dataForMr['map_clustered'] = True
	dict_dataForMr['map_grouped'] = True


	# res = {"shortId":"qrnzUaGeX5fXqrcJrgn54A","url":"https://microreact.org/project/qrnzUaGeX5fXqrcJrgn54A/"}
	res = sendToMicroReact(dict_dataForMr)

	return (outStr, res)


def sendToMicroReact(dict_dataForMr):

	# res = requests.post('https://microreact.org/api/project/', json=dict_dataForMr)
	"""
	if 'text' in res:
		print(res.text)
		return (json.loads(res.text))
	else:
		print (res.text)
		return (json.loads(res.text))
	"""

	return ({})

def makeCsv_microreact(isolates, isAuth, list_colsInfo, geolocator, org):
	"""
	Make tab separated string from search results so return to user through ajax
	:param isolates:
	:return:
	"""


	dict_countries_coords = {} # dict_[country] => (lat, long)

	(header, colNums, list_apTns, list_ccTns, dict_apCols, dict_ccCols, colNums_md, col_serverStatus, col_assignStatus, col_country) = extractTheHeader(list_colsInfo, org)

	dict_colors = [] # dict_[stVal] => hexColor

	outStr = ",".join(header) + "\n"

	for isolate in isolates:

		stColors = []

		countryCode = "-";
		latitude = None
		longitude = None

		if isolate[col_serverStatus] == 'C' and isolate[col_assignStatus] == 'A':

			# Adding the isolate cols
			for i in range(0, len(colNums)):
				outStr = outStr + str(isolate[colNums[i]])

				if i < len(colNums)-1:
					outStr = outStr + ","


			# Adding the ap cols
			lastTn = list_apTns[len(list_apTns) - 1]
			for tn in list_apTns:

				color = ""


				(col_st, col_dst) = dict_apCols[tn]

				outStr = outStr + ","
				if isolate[col_st]:
					outStr = outStr + str(isolate[col_st])

					# Next two lines ignore dst for microreact.
					# if isolate[col_dst] and isolate[col_dst] != 0:
					#	outStr = outStr + "." + str(isolate[col_dst])


					if isolate[col_st] in dict_colors:
						color = isolate[col_st]
					else:
						color = toColor2(isolate[col_st])


					if tn == lastTn:
					#	mgt9Col = toColor(isolate[col_st])
						mgt9Col = "red";

				stColors.append(color)


			# Adding the cc and epi cols
			for tn in list_ccTns:
				ccVal = None

				for ccCol in dict_ccCols[tn]:

					if isolate[ccCol]:
						if ccVal == None or isolate[ccCol] < ccVal:

							ccVal = isolate[ccCol]


				outStr = outStr + ","

				if ccVal != None:
					outStr = outStr + str(ccVal)
				# outStr = outStr +


			# Location and isolation
			for colNum in colNums_md:

				outStr = outStr + ","

				if isolate[colNum]:

					md = isolate[colNum]

					# print(type(isolate[colNum]))
					if isinstance(md, str):
						# print(md)
						md = re.sub(',', '', isolate[colNum])

					outStr = outStr + str(md)

					if colNum == col_country:
						# countryCode =  get_codeIS3166(isolate[colNum]);
						(latitude, longitude) =  get_codeIS3166(isolate[colNum], geolocator, dict_countries_coords);

			stColors.reverse()
			# outStr = outStr + ", " + countryCode + ',' + ','.join(stColors) + "\n"
			outStr = outStr + ", "

			if latitude == None:
				outStr = outStr + ','
			else:
				outStr = outStr + str(latitude) + ',' + str(longitude)

			# + str(countryCode) +

			outStr = outStr + ',' + ','.join(stColors) + "\n"

	# toColor(-5952982)
	# toColor(-12525360)
	return outStr



def toColor2(num):

	r = lambda: random.randint(0,255)

	hex = '#%02X%02X%02X' % (r(),r(),r())

	# print(hex)
	return (hex)



def toColor(num):
	num = zero_fill_right_shift(num, 0)
	b = num & 0xFF
	g = rshift((num & 0xFF00), 8) # >>> 8,
	r = rshift((num & 0xFF00), 8) # >>> 16,
	a = rshift((num & 0xFF000000), 24)/ 255 ;
	color_rgba = (r, g, b, a)
	color_hex = '#{:02x}{:02x}{:02x}'.format(*color_rgba)
	# print (str(r) + "\t" + str(g) + "\t" + str(b) + "\t" + str(a) + "\t" + color_hex)
	# return "rgba(" + [r, g, b, a].join(",") + ")";


	return (color_hex)

def zero_fill_right_shift(val, n):
    return (val >> n) if val >= 0 else ((val + 0x100000000) >> n)

def rshift(val, n):
	return (val % 0x100000000) >> n



def get_codeIS3166(country, geolocator, dict_countries_coords):
	if country.lower() == 'missing' or country.lower() == 'not collected':
		return (None, None)

	elif country in dict_countries_coords:
		return dict_countries_coords[country]

	location = geolocator.geocode(country)
	# print('Location: ' + country)

	if location == None:
		dict_countries_coords[country] = (None, None)
		return (None, None)

	dict_countries_coords[country] = (location.latitude, location.longitude)

	# print(location)
	# print (str(location.latitude) + ' ' + str(location.longitude))

	return (location.latitude, location.longitude)




def convertToCsv(list_colsInfo, isolates):

	buffer = io.StringIO()
	wr = csv.writer(buffer, quoting=csv.QUOTE_ALL)
	wr.writerow(list_colsInfo)
	wr.writerows(isolates)

	buffer.seek(0)
	response = HttpResponse(buffer, content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="isolates.csv"'

	return response



def extractTheHeader (list_colsInfo, org):
	Isolate, View_apcc, Tables_ap, Tables_cc = getModels(org)

	header = []; header_md = [];
	colNums = [] # general column numbers
	colNums_md = [] # column nums for metadata (location & isolation)
	col_serverStatus = -1; col_assignment_status = -1; # for checking

	dict_apCols = {}; # dict_{tableName} => [st, dst]
	list_apTns = []; # [tableName, ...]
	list_apColors = [];

	dict_ccCols = {}; # dict_{tableName} => [cc, ccMerge] (the Values are just appended here, as we just want the min).
	list_ccTns = []; # [tableName, ...]

	for colObj in list_colsInfo:
		# print(colObj['table_name'] + "\t" + colObj['display_name'])

		if (colObj['table_name'] == 'identifier' and colObj['display_name'] == 'Isolate'):

			header.append('id')
			colNums.append(colObj['db_col'])

		elif (colObj['table_name'] == 'mgt1'):
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

				if re.search('year', colObj['display_name'], flags=re.I):
					header_md.append('Year')

				elif re.search('month', colObj['display_name'], flags=re.I):
					header_md.append('Month')

				else:
					header_md.append(colObj['display_name'])

				if re.search('country', colObj['table_name'], flags=re.I):
					col_country = colObj['db_col']

				print (colObj);
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

		list_apColors.append(i['scheme__display_name'] + "__color")

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

	list_apColors.reverse()

	# header = header + header_md  + ['countryField'] +  list_apColors
	header = header + header_md  + ['latitude', 'longitude'] +  list_apColors


	# print ('The colCountry is ' + str(col_country))

	return (header, colNums, list_apTns, list_ccTns, dict_apCols, dict_ccCols, colNums_md, col_serverStatus, col_assignment_status, col_country)

def getModels(org):
    models = importlib.import_module(f'{org}.models')
    Isolate = models.Isolate
    View_apcc = models.View_apcc
    Tables_ap = models.Tables_ap
    Tables_cc = models.Tables_cc
    
    return Isolate, View_apcc, Tables_ap, Tables_cc