export {isolateDetailSearch, sendToIsolateDetail};

import {rowApId, rowCcId, rowEpiId, table_iso, selTdClassName} from './isolateDetailPageFns.js';
import {getTheBoolsForDisp, ajaxCall} from './packageAndSend.js';
import {downloadCsvSuccess, downloadMgt9ApsSuccess} from './downloads.js';
import {downloadMrSuccess} from './microreact.js';


function getKeyByValue(object, value) {
  return Object.keys(object).find(key => object[key] === value);
}

function isolateDetailSearch(url, assignStatusChoices, serverStatusChoices, privStatusChoices){
	$('#isoDet_searchTab').show();

	$('#ajaxSearching').show();
	document.getElementById("searchSimStrains").disabled = true;

	var apSearchMap = {};
	var ccEpiSearchMap = {};
	var locMap = {};
	var islnMap = {};
	var projMap = {};
	var isoMap = {};

	// Aps
	if (document.getElementById(rowApId)){
		var tds = document.getElementById(rowApId).getElementsByTagName("td");
		apSearchMap = addStValsToMap(tds, apSearchMap, document.getElementById("isPerfectSt").checked);

	}

	// Ccs
	if (document.getElementById(rowCcId)){
		var tds = document.getElementById(rowCcId).getElementsByTagName("td");
		ccEpiSearchMap = addCcValsToMap(tds, ccEpiSearchMap);

	}

	// Epis
	if (document.getElementById(rowEpiId)){
		var tds = document.getElementById(rowEpiId).getElementsByTagName("td");
		ccEpiSearchMap = addCcValsToMap(tds, ccEpiSearchMap);
	}
	// All values in first table containing everything apart from the view.
	if(document.getElementById(table_iso)){
		var tds = document.getElementById(table_iso).getElementsByClassName("theSel");

		for (var i = 0; i < tds.length; i++){
			if (tds[i].classList.contains(selTdClassName)){
				console.log(tds[i].id);
				if (tds[i].id.match(/^iM_l\./)){
					locMap = addValToMap(locMap, tds[i].id, tds[i].innerText);
				}
				else if (tds[i].id.match(/^iM_i\./)){
					islnMap = addValToMap(islnMap, tds[i].id, tds[i].innerText);
				}
				else if ((tds[i].id.match(/^i\./) && tds[i].id.match(/project_id$/) )){
					projMap = addValToMap(projMap, "project", tds[i].innerText);
				}

				else if (tds[i].id.match(/^p\./) ){
					projMap = addValToMap(projMap, tds[i].id, tds[i].innerText);
				}
				else {
					var innerHtmlVal = tds[i].innerText;
					if (tds[i].id.match(/server_status/)){
						innerHtmlVal = getKeyByValue(serverStatusChoices, innerHtmlVal);
					}
					else if (tds[i].id.match(/assignment_status/)){
						innerHtmlVal = getKeyByValue(assignStatusChoices, innerHtmlVal);
					}
					else if (tds[i].id.match(/privacy_status/)){
						innerHtmlVal = getKeyByValue(privStatusChoices, innerHtmlVal);
					}
					isoMap = addValToMap(isoMap, tds[i].id, innerHtmlVal);
				}
			}
		}


		console.log("The isoMap is");
		console.log(isoMap);
	}


	// if (tds.length == 0){
	//	console.log("nothing here!");
	//	return;
	//}

	console.log("Search maps");
	console.log(apSearchMap);

	console.log(locMap);

	if (Object.keys(apSearchMap).length == 0 && Object.keys(ccEpiSearchMap).length == 0 && Object.keys(locMap).length == 0 && Object.keys(islnMap).length == 0 && Object.keys(projMap).length == 0 && Object.keys(isoMap).length ==0){
		console.log("nothing to search");
		$('#ajaxSearching').hide();
		document.getElementById("searchSimStrains").removeAttribute("disabled");
		return;
	}

	sendToIsolateDetail(url, apSearchMap, ccEpiSearchMap, locMap, islnMap, projMap, isoMap, null, null, null, null, false, false, false);

}


function addValToMap(theMap, key, value){

	// for (var i=0; i<tds.length; i++){
		// console.log(tds[i].id);
		// console.log("yolo! " + tds[i].innerText);
	key = key.replace(/^.+\./, '')
	// console.log('over here ... ' + key);
	theMap[key] = value;


	return theMap;
}

function addMdValsToMap(tds, locMap){

	for (var i=0; i<tds.length; i++){
		// console.log(tds[i].id);
		// console.log("yolo! " + tds[i].innerText);
		locMap[tds[i].id] = tds[i].innerText;
	}

	return locMap;
}


function addStValsToMap(tds, allSearchMap, isPerfectSt){
	console.log("In the addStValsToMap function")
	for (var i = 0; i < tds.length; i++){
		// console.log(tds[i]);
		// console.log(selTdClassName);
		if (tds[i].classList.contains(selTdClassName)){
			tds[i].id = tds[i].id.replace(/^v./, '');
			console.log("Over here " + tds[i].id + "_st");

			var tn = tds[i].id + "_st";

			allSearchMap[tn] = tds[i].innerText;
			//  jsonIsoHgtInfo[0].fields[tn];

			if (isPerfectSt == true){
				// remove the .dst from prev val and replace with 0.
				allSearchMap[tn] = allSearchMap[tn].replace(/\.[0-9]+$/, "");


				tn = tds[i].id + "_dst";
				allSearchMap[tn] = 0;

			}
			else if (tds[i].innerText.match(".")){ // Ignoring DST value 
				allSearchMap[tn] = allSearchMap[tn].replace(/\..*$/, ''); 
			}

		}
	}
	return (allSearchMap);
}

function addCcValsToMap(tds, allSearchMap){//  jsonIsoHgtInfo){

	for (var i = 0; i < tds.length; i++){
		if (tds[i].classList.contains(selTdClassName)){
			tds[i].id = tds[i].id.replace(/^v./, '');
			allSearchMap[tds[i].id] = tds[i].innerText; //jsonIsoHgtInfo[0].fields[tds[i].id];
		}
	}
	return (allSearchMap);
}


function sendToIsolateDetail(url, apSearchMap, ccEpiSearchMap, locMap, islnMap, projMap, isoMap, pageNumToGet, orderBy, dir, isCsv, isMgt9Ap, isGrapeTree, isMr){

  // console.log("THIS IS THE IS-GRAPH-TREE " + isGrapeTree);

	var theBools = getTheBoolsForDisp();
	var data = {
		'json_apSearchTerms': JSON.stringify(apSearchMap),
		'json_ccEpiSearchTerms': JSON.stringify(ccEpiSearchMap),
		'json_location': JSON.stringify(locMap),
		'json_isolation': JSON.stringify(islnMap),
		'json_project': JSON.stringify(projMap),
		'json_iso': JSON.stringify(isoMap),
		'isAp': theBools.isAp,
		'isDst': theBools.isDst,
		'isMgtColor': theBools.isMgtColor,
		'pageNumToGet': pageNumToGet,
		'csrfmiddlewaretoken': '{{ csrf_token }}',
		'orderBy': orderBy,
		'dir': dir,
		'isCsv':isCsv,
		'isMgt9Ap': isMgt9Ap,
		'isGrapeTree': isGrapeTree,
		'isMr': isMr,
		'searchType': 'and',
	};

  if (isMr == true){
		ajaxCall(url, data, downloadMrSuccess);
	}
	else if(isCsv == true){
		ajaxCall(url, data, downloadCsvSuccess);
	}
	else if (isMgt9Ap == true){
		ajaxCall(url, data, downloadMgt9ApsSuccess)
	}
	else{
		ajaxCall(url, data, isolateDetailSuccess);
	}

}


function isolateDetailSuccess(response){
	$('#ajaxSearching').hide();
	document.getElementById("searchSimStrains").removeAttribute("disabled");
	$('#isolateTable').html(response);
}
