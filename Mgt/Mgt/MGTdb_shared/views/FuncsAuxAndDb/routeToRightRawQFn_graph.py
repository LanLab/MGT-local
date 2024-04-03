from . import routeToRightRawQFn
from . import rawQueries_graph as rqGraph
from django.http import Http404
import sys



def getDataFromRightFn(arr_ap, arr_cc, arr_epi, arr_loc, arr_isln, arr_iso, username, isExactProj, projIdToExcl, searchType, org):

	mgtIds = None;
	locIds = None
	islnIds = None
	isoSearchStr = None
	searchedProjIds = None
	userProjIds = None
	dict_mergedIds = None

	isFirstSearchType = True

	# (mgtIds, locIds, islnIds, isoSearchStr, searchedProjIds, userProjIds, dict_mergedIds, isFirstSearchType) = routeToRightRawQFn.convertSearchToIds(arr_ap, arr_cc, arr_epi, arr_loc, arr_isln, arr_iso, username, isExactProj, searchType, isFirstSearchType)
	try:
		(mgtIds, locIds, islnIds, isoSearchStr, searchedProjIds, userProjIds, dict_mergedIds, isFirstSearchType) = routeToRightRawQFn.convertSearchToIds(arr_ap, arr_cc, arr_epi, arr_loc, arr_isln, arr_iso, username, isExactProj, searchType, isFirstSearchType, org)
	except:
		print("Incorrect access error encoutered early on!.")
		print(sys.exc_info()[0])
		raise Http404("Incorrect access error. Please go back");

		# return (isoCount, isolates, dict_pageInfo, dict_mergedIds, [], [], [], list_serverStatus, list_assignStatus, list_privStatus)


	# print("The mgtIds are:");
	# print(islnIds);
	print("Everyone breathe ")
	print(username)
	print(isExactProj);
	print(isoSearchStr);
	print(searchedProjIds);
	print(userProjIds);
	print(locIds);
	print(arr_loc);
	print(mgtIds);
	print(islnIds);

	(isolates, columns) = rqGraph.get_timeOrLoc_StCountData(mgtIds, locIds, islnIds, isoSearchStr, searchedProjIds, userProjIds, isExactProj, projIdToExcl, org)

	return (isolates, columns);
