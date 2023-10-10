export {getInitialProjData, rmProjectFromSel};

import {getTheBoolsForDisp, ajaxCall, doVisChngSuccess} from './packageAndSend.js';
import {downloadCsvSuccess, downloadMgt9ApsSuccess} from './downloads.js';
import {downloadMrSuccess} from './microreact.js';


function getInitialProjData(url, projectId, pageNumToGet, orderBy, dir, isCsv, isMgt9Ap, isGrapeTree, isMr){
	let theBools = getTheBoolsForDisp();
	let data = {
		'projectId': JSON.stringify(projectId),
		'pageNumToGet': pageNumToGet,
		'orderBy': orderBy,
		'dir': dir,
		'isAp': theBools.isAp,
		'isDst': theBools.isDst,
		'isMgtColor': theBools.isMgtColor,
		'isCsv': isCsv,
		'isMgt9Ap': isMgt9Ap,
		'isGrapeTree': isGrapeTree,
		'isMr': isMr,
	};

	if (isMr == true){
		ajaxCall(url, data, downloadMrSuccess);
	}
	else if (isCsv == true){
		ajaxCall (url, data, downloadCsvSuccess);
	}
	else if (isMgt9Ap == true){
		ajaxCall(url, data, downloadMgt9ApsSuccess);
	}
	else{
		ajaxCall(url, data, doVisChngSuccess);
	}
}

// Removes project from filter table in project page.
function rmProjectFromSel(isoAndMdInfo){
	for (let i = 0; i <= isoAndMdInfo.length-1; i++){
		if (isoAndMdInfo[i].table_name == 'project'){
			isoAndMdInfo.splice(i, 1); // remove an eleement;
		}
	}
}
