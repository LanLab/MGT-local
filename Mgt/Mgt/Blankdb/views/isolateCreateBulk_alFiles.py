from django.shortcuts import render, redirect, get_object_or_404
from Blankdb.models import Location, Isolate, Isolation, Project, User
from django.core.exceptions import PermissionDenied
from Blankdb.views.FuncsAuxAndDb import routeToRightRawQFn as routeToRightFn


def page(request, pk):

	# check if project exists
	proj = get_object_or_404(Project, pk=pk)

	# check if project owned by user.
	if not proj.user.userId == request.user.username:
		raise PermissionDenied("Error: you are trying to add an isolate to a project that is not yours.")


	if request.POST:
		dict_savedFiles = dict()
		list_rejectedFiles = list()

		# if request.FILES:
		# 	uploaded_files = [request.FILES.get('file_upload[%d]' % i)
        #        for i in range(0, len(request.FILES))]

		#	print("The uploaded files are:")
		#	print(uploaded_files)

		print('The file name is: ')
		# print(request.FILES['file'])
		uploaded_file = request.FILES['file']
		print(uploaded_file)

		# isolateObj = None
		try:
			isolateObj = Isolate.objects.get(tmpFn_alleles=uploaded_file, project_id=pk)
			print("Found " + isolateObj.identifier)

			isolateObj.file_alleles = request.FILES['file']
			isolateObj.tmpFn_alleles = None
			isolateObj.server_status = 'V'
			isolateObj.save()

			print(isolateObj.tmpFn_alleles)

		except Isolate.DoesNotExist:
			list_rejectedFiles.append(request.FILES['file'])




		print("Rejected files .... ")
		print(list_rejectedFiles)


	# get all isolates which has tmp_filename value.

	IsolColNames = ['Isolate', 'Project name', 'Serovar', 'Privacy status', 'Server status', 'Expected filename', 'Continent', 'Country', 'State', 'Postcode', 'Source', 'Type', 'Host', 'Disease', 'Date', 'Year', 'Month']

	isolates = Isolate.objects.filter(project=proj).exclude(tmpFn_alleles=None).values('identifier', 'project_id__identifier', 'serovar', 'privacy_status', 'server_status', 'tmpFn_alleles', 'location_id__continent', 'location_id__country', 'location_id__state', 'location_id__postcode', 'isolation_id__source', 'isolation_id__type', 'isolation_id__host', 'isolation_id__disease', 'isolation_id__date', 'isolation_id__year', 'isolation_id__month')

	print(isolates)

	(list_serverStatus, list_assignStatus, list_privStatus) = routeToRightFn.isolateChoices()

	return render(request, 'Blankdb/isolateCreateBulk_alFiles.html', {"project": proj, "isolates": isolates, "IsoColNames": IsolColNames, "serverStatus": list_serverStatus, "assignStatus": list_assignStatus, "privStatus": list_privStatus})
