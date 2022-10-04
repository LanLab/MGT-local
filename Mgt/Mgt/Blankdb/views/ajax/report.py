from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from Blankdb.views.FuncsAuxAndDb import rawQueries_report as rawQ_r


@csrf_exempt
def page(request):

	if len(request.POST) > 0:

		respData = {}

		if 'yearStart' not in request.POST or 'yearEnd' not in request.POST or int(request.POST['yearStart']) > int(request.POST['yearEnd']): 
			respData['Error'] = "Error: year start and end are not right."
			
		elif request.user.is_authenticated:
			if ('country' not in request.POST or request.POST['country'] == '') and ('project' not in request.POST or request.POST['project'] == ''): # check input val
				respData['Error'] = "Please select either a project or a country."

			else:
				respData = rawQ_r.getDataForReport(request.user.username, request.POST['country'], request.POST['project'], True, int(request.POST['yearStart']), int(request.POST['yearEnd'])) # fn checks if proj is user project.
		else:
			if ('country' not in request.POST or request.POST['country'] == ''): # check input val
				# form.add_error(None, )

				respData['Error'] = "Please select either a project or a country."
			# elif check yearStart and yearEnd here...
			else:
				# check proj is user project
				print('YearStart: ' + request.POST['yearStart'] + ' YearEnd: ' + request.POST['yearEnd'])
				respData = rawQ_r.getDataForReport(request.user.username, request.POST['country'], None, False, int(request.POST['yearStart']), int(request.POST['yearEnd']))

		return JsonResponse(respData, safe=False)

	return JsonResponse({}, safe=False)


"""
	if len(request.POST) > 0: # some post data has been sent
		form = downloadReportForm_auth(request.POST, user=request.user.username)
		print (request.POST)
		if form.is_valid():



			if request.user.is_authenticated:

				if ('country' not in request.POST or request.POST['country'] == '') and ('project' not in request.POST or request.POST['project'] == ''): # check input val
					form.add_error(None, "Please select either a project or a country.")

				else:
					# check proj is user project
					rawQ_r.getDataForReport(request.user.username, request.POST['country'], request.POST['project'])

			else:
				if ('country' not in request.POST or request.POST['country'] == ''): # check input val
					form.add_error(None, "Please select a country.")

				else:
					dict_dataForReport = rawQ_r.getDataForReport(None, request.POST['country'], None)

					return render(request, 'Blankdb/summaryReport.html', {'dataForReport': dict_dataForReport);


	else: # no post data has been sent
"""
