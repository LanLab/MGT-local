from django import forms
from Blankdb.models import Isolate, Project, User
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from Blankdb.views.FuncsAuxAndDb import queryDb as q
from django.urls import reverse
# from django.core.exceptions import PermissionDenied
# from . import isolateForms_CreateEdit as isolateForms
from django.views.generic.edit import FormView
from . import isolateForms_CreateEdit as isolateForms
import re
from django.utils.dateparse import parse_date
from datetime import datetime
from django.core.exceptions import PermissionDenied
from Blankdb.models.isoMetaModels import continent_choices
from django_countries import countries
import pyparsing as pp


def page(request):
	project = None # for sending back on initial page load.

	if len(request.POST) == 0: # get request.
		projs = q.getUserProjectIds(request.user.username)

		if len(projs) == 0:
			return redirect('/Blankdb/create-project')

		if len(request.GET) > 0:
			if not (int(request.GET.get('project')) in projs):
				raise PermissionDenied("Error: you are trying to add an isolate to a project that is not yours.")

			project = Project.objects.get(id=request.GET.get('project'))
			form_md = isolateForms.IsolateMetaDataForm(request.user, initial={'project': project})
			# form_files = isolateForms.IsolateCreateBulkForm()

		else:
			# print("get all users project ids")
			form_md = isolateForms.IsolateMetaDataForm(request.user)
			# form_files = isolateForms.IsolateCreateBulkForm()



	else: # when POST request.


		# checkProjInUser(projectId, userId)


		form_md = isolateForms.IsolateMetaDataForm(request.user, request.POST, request.FILES) # add to form.


		if not form_md.is_valid():
			return render(request, 'Blankdb/isolateCreateBulk_mdFile.html', {'form_iso': form_md, 'project': request.POST['project']})

		else:
			# save each object!

			dict_notAddedIsolates = handle_metadata_file(form_md, request.FILES['file_md'], request.POST['project'])

			# print("after the handle meta data")

			if (len(form_md.errors)):
				# print("Errors detected in form")
				return render(request, 'Blankdb/isolateCreateBulk_mdFile.html', {'form_iso': form_md, 'project': request.POST['project']})

			# files = request.FILES.getlist('files')
			# print(request.FILES, request.POST['project'])
			#3 regex = re.compile(r'.+\.csv')
			# file_csv = [f for f in files if regex.search(f)]
			# print(file_csv)

			# csv = files.remove()
			# print(files)
			if (len(dict_notAddedIsolates) > 0):
				return render(request, 'Blankdb/isolateCreateBulk_mdFile.html', {'form_iso': form_md, 'project': request.POST['project'], 'notAddedIsolates': dict_notAddedIsolates})

			return HttpResponseRedirect(reverse('Blankdb:isolate_create_bulk_al', kwargs={'pk': request.POST['project']}))

	# return HttpResponseRedirect(reverse('Blankdb:project_detail', kwargs={'pk': isolateObj.id}))

	return render(request, 'Blankdb/isolateCreateBulk_mdFile.html', {'form_iso': form_md, 'project': project})

############################### Adding each isolate and its metadata

def getAndAddLocInfo(continent, country, state, postcode):

	dict_loc = dict()
	dict_loc['continent'] = continent
	dict_loc['country'] = country
	dict_loc['state'] = state
	dict_loc['postcode'] = postcode

	form_loc = isolateForms.LocationForm(dict_loc)

	return form_loc


def getAndAddIslnInfo(form_md, source, type, host, disease, date, year, month):
	dict_isln = dict()
	dict_isln['source'] = makeNoneIfEmpty(source)
	dict_isln['type'] = makeNoneIfEmpty(type)
	dict_isln['host'] = makeNoneIfEmpty(host)
	dict_isln['disease'] = makeNoneIfEmpty(disease)
	dict_isln['year'] = makeNoneIfEmpty(year)
	dict_isln['month'] = makeNoneIfEmpty(month)
	dict_isln['date'] = makeNoneIfEmpty(date)

	if date:

		arr = re.split("[\-\.]", date)


		if len(arr) != 3 or not (int(arr[0]) or int(arr[1]) or int(arr[2])):
			form_md.add_error(None, 'Date must be provided in the format YYYY.MM.DD or YYYY-MM-DD')

		elif int(arr[1]) < 1 or int(arr[1]) > 12:
			form_md.add_error(None, "A date's months should be between 1 and 12. Date format is YYYY-MM-DD or YYYY.MM.DD.") # " Currently is " + str(month))
		else:

			# print(arr[0] + " " + arr[1] + " " + arr[2])

			try:


				dict_isln['date'] = datetime(int(arr[0]), int(arr[1]), int(arr[2])) # add date,

				dict_isln['year'] = int(arr[0])
				dict_isln['month'] = int(arr[1])

			except:
				form_md.add_error(None, "Unable to add date, please contact the admistrator")
			# add year and month





	form_isln = isolateForms.IsolationForm(dict_isln)

	return form_isln


		#	if re.match("\-", date): # date format YYYY-MM-DD
		#		dict_isln['date'] = datetime.strptime(date, "%Y-%m/-%d/")

		#	elif re.match("\.", date): # date format YYYY.MM.DD

		#		dict_isln['date'] = datetime.strptime(date, "%Y.%m/.%d/")











def makeNoneIfEmpty(val):

	if val == "":
		return None

	return val


def doesIsoExistInProj(projectId, isoIdentifier):
	# check that isoIdentifier not in project Id

	return Isolate.objects.filter(project_id__pk=projectId, identifier=isoIdentifier).exists()

def doesTmpFnExistInProj(projectId, tmpFn_alleles):
	return Isolate.objects.filter(project_id__pk=projectId, tmpFn_alleles=tmpFn_alleles).exists()

def isEmpty(theVal):

	if theVal and not re.match(r"^[\s\t]+$", theVal):
		return False

	# print("Over here! " + theVal)
	return True



def checkAllReqAreNotEmpty(form_md, arrLine, dict_colNums):

	if isEmpty(arrLine[dict_colNums['continent']]) or isEmpty(arrLine[dict_colNums['country']]) or isEmpty(arrLine[dict_colNums['year']]) or isEmpty(arrLine[dict_colNums['identifier']]) or isEmpty(arrLine[dict_colNums['tmpFn_alleles']]) or isEmpty(arrLine[dict_colNums['privacy_status']]):

		form_md.add_error(None, "One or more of the required data values is missing in the provided CSV file. You must provide values for the Isolate identifier, Allele filename, Privacy status, Continent, Country and Year.")


def checkProvidedTypes(form_md, arrLine, dict_colNums):

	if not re.match("^[a-zA-Z0-9\_\-]+$", arrLine[dict_colNums['identifier']]):
		form_md.add_error(None, "Isolate identifier: Only alphanumeric characters, '_' or '-' is allowed. Please check the uploaded CSV.")
		return

	if not re.match("^[a-zA-Z0-9\_\-]+\.(fasta|fa)$", arrLine[dict_colNums['tmpFn_alleles']]):
		form_md.add_error(None, "Allele filename: only alphanumeric characters, '_' or '-' is allowed. Furthermore, this filename should end in .fasta or .fa")
		return

	if not (arrLine[dict_colNums['privacy_status']] == 'PU' or arrLine[dict_colNums['privacy_status']] == 'PV'):
		form_md.add_error(None, "Privacy status: only PU (to make isolate public) or PV (to make isolate private) are expected for this column.")
		return

	if not re.match("^[0-9]{4}$", arrLine[dict_colNums['year']]):
		form_md.add_error(None, "Year: must be a number with four digits " + arrLine[dict_colNums['year']] + ".")
		return

	if not (arrLine[dict_colNums['continent']] in dict(continent_choices)):
		# print (arrLine[dict_colNums['continent']].lower() + " is the provided continent")
		form_md.add_error(None, "Continent: A provided continent is not allowed. Please see the instructions for allowable values.")
		return

	if (not (arrLine[dict_colNums['country']] in dict(countries).values())):

		form_md.add_error(None, "Country: A provided country value is not allowed. Please see the instructions for allowable values.")
		return


import json
def addIsolateAndMd(form_md, arr, dict_colNums, projectId):
	# form location

	checkAllReqAreNotEmpty(form_md, arr, dict_colNums)
	checkProvidedTypes(form_md, arr, dict_colNums)

	if len(form_md.errors) > 0:
		return None



	locObj = None
	islnObj = None
	isolateObj = None


	# Form location
	form_loc = getAndAddLocInfo(arr[dict_colNums['continent']],  arr[dict_colNums['country']], arr[dict_colNums['state']], arr[dict_colNums['postcode']])

	if not form_loc.is_valid():

		theErrors =  json.loads(form_loc.errors.as_json())
		isAnyError = False

		for error in theErrors:
			if error == "__all__": # ignoring the combination already exists constraint.
				continue

			isAnyError = True

			form_md.add_error(None, error + " - " + theErrors[error][0]['message'])


		if isAnyError:
			form_md.add_error(None, "Isolate location errors:")

			return None

	# if exists, get the object, else save!
	locObj = form_loc.save()

	# Form isolation
	form_isln = getAndAddIslnInfo(form_md, arr[dict_colNums['source']], arr[dict_colNums['type']], arr[dict_colNums['host']], arr[dict_colNums['disease']], arr[dict_colNums['date']],  arr[dict_colNums['year']], arr[dict_colNums['month']])

	if not form_isln.is_valid():
		print(form_isln.errors.as_json())

		theErrors =  json.loads(form_isln.errors.as_json())
		isAnyError = False

		for error in theErrors:
			errorName = error
			if error == "__all__":
				errorName = ""
			 	# continue

			isAnyError = True

			form_md.add_error(None, errorName + " - " + theErrors[error][0]['message'])


		if isAnyError:
			form_md.add_error(None, "Found isolate isolation errors.")

			return None

	islnObj = form_isln.save()


	# form isolate
	dict_iso = dict()
	dict_iso['identifier'] = arr[dict_colNums['identifier']]
	dict_iso['privacy_status'] = arr[dict_colNums['privacy_status']]
	dict_iso['project'] = projectId
	dict_iso['tmpFn_alleles'] = arr[dict_colNums['tmpFn_alleles']]
	dict_iso['server_status'] = 'A'

	form_iso = isolateForms.IsolateForm_tmp(dict_iso)

	if  not form_iso.is_valid():
		isError = False
		theErrors =  json.loads(form_iso.errors.as_json())

		for error in theErrors:
			# if not errorsToIgnore(theErrors[error][0]['message']):
			isError = True
			form_md.add_error(None, error + " - " + theErrors[error][0]['message'])


		form_md.add_error(None, "Error detected in isolate.")


	isolateObj = form_iso.save(commit=False)

	if locObj:
		isolateObj.location = locObj
	if islnObj:
		isolateObj.isolation = islnObj


	try:
		isolateObj.save()
	except:
		form_md.add_error(None, "Isolate not saved in the database")


def errorsToIgnore(msg):
	if msg == "Location with this Continent, Country, State or sub country and Postcode already exists.":
		return True

	if msg == "Isolation with this Source, Type, Host, Host disease and Collection date already exists.":
		return True

	return False

def handle_metadata_file(form_md, file_csv, projectId):
	dict_notAddedIsolates = dict()

	file_data = file_csv.read().decode('utf-8')

	lines = re.split('[\n\r]+', file_data)


	isHeader = True
	for line in lines:

		# line = re.sub('[\n\r]+$', '', line)

		if re.match("^[\s\t]*$", line):
			continue


		arr = pp.commaSeparatedList.parseString(line).asList()

		for i in range(0, len(arr)):
			arr[i] = re.sub("\"", "", arr[i])


		if isHeader == True:
			dict_colNums = extractHeader(form_md, arr)
			# print('Check extracted header') checked, and error added to form.

			if len(form_md.errors):
				return None

			isHeader = False
			continue


		# check if identifier and project are unique for this user...
		if doesIsoExistInProj(projectId, arr[dict_colNums['identifier']]):
			dict_notAddedIsolates[arr[dict_colNums['identifier']]] = "Isolate with identifier already exists in this project."

		#	print("Isolate already exists. " + arr[dict_colNums['identifier']])

		elif doesTmpFnExistInProj(projectId, arr[dict_colNums['tmpFn_alleles']]):
			dict_notAddedIsolates[arr[dict_colNums['identifier']]] = "The provided expected file name is not unique for this isolate"
		# 	print("Tmp file name not uniq for this project. " + arr[dict_colNums['identifier']])
			# not adding add to list to print out?

		# elif
		else:
			addIsolateAndMd(form_md, arr, dict_colNums, projectId)


	return dict_notAddedIsolates


def extractHeader(form_md, arrLine):
	dict_colNums = {'identifier': -1, 'privacy_status': -1, 'continent': -1, 'country': -1, 'state': -1, 'postcode': -1, 'source': -1, 'type': -1, 'host': -1, 'disease': -1, 'date': -1, 'year': -1, 'month': -1, 'tmpFn_alleles': -1}

	if len(arrLine) < len(dict_colNums):
		form_md.add_error(None, "Error: uploaded metadata file has too few columns");

	print(arrLine)
	for i in range(0,len(arrLine)):
		if 'isolate identifier' == arrLine[i].lower():
			dict_colNums['identifier'] = i

		if 'privacy status' == arrLine[i].lower():
			dict_colNums['privacy_status'] = i

		if 'continent' == arrLine[i].lower():
			dict_colNums['continent'] = i

		if 'country' == arrLine[i].lower():
			dict_colNums['country'] = i

		if 'state' == arrLine[i].lower():
			dict_colNums['state'] = i

		if 'postcode' == arrLine[i].lower():
			dict_colNums['postcode'] = i

		if 'source' == arrLine[i].lower():
			dict_colNums['source'] = i

		if 'type' == arrLine[i].lower():
			dict_colNums['type'] = i

		if 'host' == arrLine[i].lower():
			dict_colNums['host'] = i

		if 'disease' == arrLine[i].lower():
			dict_colNums['disease'] = i

		if 'date' == arrLine[i].lower():
			dict_colNums['date'] = i

		if 'year' == arrLine[i].lower():
			dict_colNums['year'] = i

		if 'month' == arrLine[i].lower():
			dict_colNums['month'] = i

		if 'allele filename' == arrLine[i].lower():
			dict_colNums['tmpFn_alleles'] = i


	if any(value == -1 for value in dict_colNums.values()):
		print(dict_colNums)
		form_md.add_error(None, "The uploaded meta data does not contain the expected columns. Please download the template file again from Step 1. and readd your data to it.")



	return(dict_colNums)

# Isolate identififer	Privacy status	Continent	Country	State	Postcode	Source	Type	Host	Disease	Date	Year	Month	Allele filename
