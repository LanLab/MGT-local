from . import rawQueries

def get_timeOrLoc_StCountData(mgtIds, locIds, islnIds, isoSearchStr, searchedProjIds, userProjIds, isProjPage, projIdToExcl, org):

	print('THE ISO SEARCH STR IS ');
	print(isoSearchStr);
	print(userProjIds);
	print(searchedProjIds);

	queryStr = 'SELECT qInner.*, v2.* '
	queryStr = queryStr + f'FROM "{org}_view_apcc" as v2 RIGHT JOIN '
	queryStr = queryStr + '('


	queryStr = queryStr + "SELECT count(i.id), v.mgt_id as mgt_id, iM_i.year as year, iM_i.month, iM_i.date, iM_l.continent, iM_l.country, iM_l.state, iM_l.postcode "
	queryStr = queryStr + f'FROM "{org}_isolate" as i '

	if islnIds and len(islnIds) > 0:
		queryStr = queryStr + f'INNER JOIN "{org}_isolation" as iM_i ON i.isolation_id = iM_i.id '
		# print("Do the isolation inner join & add a where...")
	else:
		queryStr = queryStr + f'LEFT JOIN "{org}_isolation" as iM_i ON i.isolation_id = iM_i.id '

	if mgtIds and len(mgtIds) > 0:
		queryStr = queryStr + f'INNER JOIN "{org}_view_apcc" as v ON i.mgt_id = v.mgt_id '
	else:
		queryStr = queryStr + f'LEFT JOIN "{org}_view_apcc" as v ON i.mgt_id = v.mgt_id '



	if locIds and len(locIds) > 0:
		queryStr = queryStr + f'INNER JOIN "{org}_location" as iM_l ON i.location_id = iM_l.id '
	else:
		queryStr = queryStr + f'LEFT JOIN "{org}_location" as iM_l ON i.location_id = iM_l.id '


	queryStr = queryStr + "WHERE " # " i.privacy_status ='PU' "

	if isProjPage == True or (isProjPage == False and searchedProjIds and len(searchedProjIds) > 0): # in a single project;
		print("The searched Proj id is " + str(searchedProjIds) + " " + str(isProjPage))

		queryStr = queryStr + " i.project_id = " + str(searchedProjIds[0])

	elif isProjPage == False and userProjIds != None and searchedProjIds != None and len(userProjIds) > 0 and len(searchedProjIds) == 0: # i.e. no proj searched for
		queryStr = queryStr + " (i.privacy_status ='PU' OR i.project_id = ANY(ARRAY" + str(list(userProjIds)) + "))"

	elif isProjPage == False:
		queryStr = queryStr + " i.privacy_status ='PU' "

		if projIdToExcl != None and len(projIdToExcl) > 0:
			queryStr = queryStr + " AND i.project_id != " + projIdToExcl[0] ;
	else:
		print("UNKNOWN CASE ENCOUNTERED!");


	if islnIds and len(islnIds) > 0:
		queryStr = queryStr + " AND i.isolation_id = ANY(ARRAY" + str(list(islnIds)) + ")";

	if locIds and len(locIds) > 0:
		queryStr = queryStr + " AND i.location_id = ANY(ARRAY" + str(list(locIds)) + ")";

	if mgtIds and len(mgtIds) > 0:
		queryStr = queryStr + " AND v.mgt_id = ANY(ARRAY" + str(list(mgtIds)) + ")";

	if (isoSearchStr and isoSearchStr != ""):
		queryStr = queryStr + isoSearchStr;

	queryStr = queryStr + " GROUP BY v.mgt_id, iM_i.year, iM_i.month, iM_i.date, iM_l.continent, iM_l.country, iM_l.state, iM_l.postcode "

	if (isProjPage == True):
		queryStr = queryStr + ", i.project_id "


	queryStr = queryStr + ') qInner on qInner.mgt_id = v2.mgt_id '
	queryStr = queryStr + "ORDER BY qInner.year, qInner.month, qInner.date,  qInner.continent, qInner.country, qInner.state, qInner.postcode "
	queryStr = queryStr + ';'


	print(queryStr);

	(isolates, columns) = rawQueries.executeQuery_table(queryStr, org);

	return (isolates, columns);
