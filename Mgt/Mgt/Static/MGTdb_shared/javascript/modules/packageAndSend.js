export {getUrlToSendToFromUrl, sortElemsAndSend, ajaxCall, getInitialData, doTheOrderBy, getOtherPage, checkAndGetPageNum, getTheBoolsForDisp};
export {doVisChngSuccess};

// import {downloadMgt9ApsSuccess} from './packageAndSend.js';
import {downloadCsvSuccess, downloadMgt9ApsSuccess} from './downloads.js';
import {serverStatus, assignStatus, privacyStatus, isQuery, islnYear, islnMonth, islnDate, locPostcode, groupIso, groupLoc, groupIsln, sort_forward, sort_reverse, url_initialIsolates, url_initialProjIsolates, url_searchIsoList, url_searchIsoDetail, url_searchProjDetail} from './constants.js';
import {getInitialProjData} from './projectDetail_initSearch.js';
import {sendToIsolateDetail} from './isolateDetailAjax.js';
import {downloadMrSuccess} from './microreact.js';


function ajaxCall(url, data, fnOnSuccess){
	$.ajax({
		type: 'POST',
		url: url,
		data: data,
		// dataType: 'html',
		success: function(response){
			// doSuccesfulThings();
			console.log("This was sucesful");
			fnOnSuccess(response);
		},
		error: function (xhr, status, error) {
			console.log("There has been an error");
			xhr.abort();
			printTheError()
		}
	});
}

function printTheError(){
	// var tab = document.getElementById("infoTable");
	// tab.innerHTML = "Error: please enter atleast one value for search";

	$('#ajaxSearching').hide();
	if (document.getElementById("filterIsolates")){
		document.getElementById("filterIsolates").removeAttribute("disabled");
	}

}

function doNothingSuccess(response){
}

function doVisChngSuccess(response){

	$('#ajaxSearching').hide();
	document.getElementById("filterIsolates").removeAttribute("disabled");
	$('#isolateTable').html(response);

}

function doVisChngSuccess_proj(response){

	$('#ajaxSearching').hide();
	document.getElementById("filterIsolates").removeAttribute("disabled");
	$('#isolateTable').html(response);
	// console.log('response is: ');
	// console.log(response);
	// addRowToFilterTbl("theSearchTbl", {{dirColsInfo|safe}}, {{dirAps|safe}}, {{dirCcs|safe}}, {{serverStatusChoices|safe}}, {{assignStatusChoices|safe}}, {{privStatusChoices|safe}}, apTn, aps[apTn]);
}





function addRowsToIsoObj(isoObj, arrColsForCsv, list_tabRows_byAp9Id, mgt9Ap){

	// Get a row from each element in the list.


	for (var tabNum =0; tabNum < list_tabRows_byAp9Id.length; tabNum++ ){

		var qs = JSON.parse(list_tabRows_byAp9Id[tabNum]);



		var theRow = qs.find(obj => { return obj.pk == mgt9Ap }); // add this row to isoObj

		doTheAddRow(isoObj, arrColsForCsv, theRow);
	}

}

function doTheAddRow(isoObj, arrColsForCsv, theRow){

	for (let [key, value] of Object.entries(theRow.fields)) {
		// Exclude st, dst, 'date' cols, 'cc_*' cols

		if (key == 'st' || key == 'ST' || key == 'dst' || key == "DST"){
		}
		else if (key.match(/^date/) || key.match(/^cc[0-9]+\_[0-9]+/)){

		}
		else{
			// add
			if (arrColsForCsv.indexOf(key) == -1){
				arrColsForCsv.push(key);
			}

			if (value.match(/\_/)){
				value = value.replace(/\_.$/, '');
			}

			if (value < 0){
				value = value * -1;
			}

			isoObj[key] = value;
		}
	}
}


function getMgt9ApId(theMapping, mgtId){


	var mgt9ApId = theMapping.filter(function(row){
		return (row[0] == mgtId);
	});

	return(mgt9ApId);
}

// ================================================= //


// ORDER_BY IMPL.

function doTheOrderBy(tableName, searchVar, tableId){

	// 1. toggle a buttons class (so that its sort_ascending or descending direction).
	var dir = '';


	if (document.getElementById(tableName).classList.contains(sort_forward)){
		removeClassFromBtn(tableName, sort_forward);
		addClassToBtn(tableName, sort_reverse);
		dir = sort_reverse;
		// console.log("Now it should reverse...");
	}
	else if (document.getElementById(tableName).classList.contains(sort_reverse)){
		removeClassFromBtn(tableName, sort_reverse);
		addClassToBtn(tableName, sort_forward);
		dir = sort_forward;
		// console.log("Now it should reverse...");
	}
	else{

		dir = sort_forward;
		addClassToBtn(tableName, sort_forward);
		// console.log(document.getElementById(tableName).classList);
	}


	var searchVar_str = searchVar.replace(/\'/g, '\"');


	var searchVar_js = JSON.parse(searchVar_str);

	// 2. Package the info, and
	searchVar_js[0]['dir'] = dir;
	searchVar_js[0]['orderBy'] = tableId + "." + tableName;


	// console.log(searchVar_js);
	getOtherPage(searchVar[0].pageNumToGet, searchVar_js);
 	// getOtherPage(searchVar);
}



// PAGINATION IMPL.




function checkAndGetPageNum(inputId, startIndex, endIndex, searchVar){

	var requestedPageNum = document.getElementById(inputId).value;


	// check value is not empty
	// Check value is numeric
	// check value is [startIndex, endIndex]

	if (!isOkNum(requestedPageNum) ){
		document.getElementById('pageNumErr').innerHTML = 'Please enter numbers.';
		return;
	}

	if (requestedPageNum < startIndex || requestedPageNum > endIndex){
		document.getElementById('pageNumErr').innerHTML = 'A valid page number must be between ' + startIndex + ' and ' + endIndex + '.';
		return;
	}

	document.getElementById('pageNumErr').innerHTML = '';

	document.getElementById('pageNumLoading').style.display = '';
	toggleDisableBtn('btnNonConsecPageNum', true);


	getOtherPage(requestedPageNum, searchVar, false, false, false, false);

	// console.log(startIndex + " " + endIndex);
	// console.log("searchVar");
	// console.log(searchVar);
}



function getOtherPage(pageNumToGet, searchVar, isCsv, isMgt9Ap, isMr, isGrapeTree){
	// console.log(searchVar);

	if (document.getElementById('pageNumLoading')){
		document.getElementById('pageNumLoading').style.display = '';
	}

	var orderBy = null;
	var dir = null;
	let searchType = 'and';

	if (searchVar[0].hasOwnProperty("orderBy")){
		orderBy = searchVar[0].orderBy;
		dir = searchVar[0].dir;
	}

	if (searchVar[0].hasOwnProperty('searchType')){
		searchType = searchVar[0].searchType;
	}


	if (searchVar[0].hasOwnProperty("pageType")){
		if (searchVar[0].pageType == "pg_initialIsolates"){
			//console.log("pg_initialIsolates");
			getInitialData(url_initialIsolates, pageNumToGet, orderBy, dir, isCsv, isMgt9Ap, isMr, isGrapeTree);

		}
		else if (searchVar[0].pageType == "pg_initialProjIsolates"){
			// console.log("pg_initialProjIsolates");
			getInitialProjData(url_initialProjIsolates, null, pageNumToGet, orderBy, dir, isCsv, isMgt9Ap, isGrapeTree, isMr);
		}
		else if (searchVar[0].pageType == "pg_searchIsoList"){
			// console.log("pg_searchIsoList");
			sendToIsolateList(url_searchIsoList, null, null, null, null, null, null, pageNumToGet, orderBy, dir, isCsv, isMgt9Ap, searchType, isGrapeTree, isMr);
		}
		else if (searchVar[0].pageType == "pg_searchIsoDetail"){
			console.log("pg_searchIsoDetail");
		 	// console.log("some thing else entirely!!");
			sendToIsolateDetail(url_searchIsoDetail, null, null,
				null, null, null, null, pageNumToGet, orderBy, dir, isCsv, isMgt9Ap, isGrapeTree, isMr);
		}
		else if (searchVar[0].pageType == "pg_searchProjDetail"){
			// console.log("pg_searchProjDetail");
			sendProjSearchData(url_searchProjDetail, null, null, null, null, null, null, null, pageNumToGet, orderBy, dir, isCsv, isMgt9Ap, searchType, isGrapeTree, isMr);
		}
	}
}



function updateUrl(searchVar){
	// var searchParams = new URLSearchParams(window.location.search);

	var currUrl = window.location.href.split('?')[0];
	console.log (window.location.href);

	var str = "";
	str = str + addIfNotUrlParams(currUrl, searchVar.arr_ap, str=="");
	str = str + addIfNotUrlParams(currUrl, searchVar.arr_cc, str=="");
	str = str + addIfNotUrlParams(currUrl, searchVar.arr_epi, str=="");
	str = str + addIfNotUrlParams(currUrl, searchVar.arr_iso, str=="");
	str = str + addIfNotUrlParams(currUrl, searchVar.arr_isln, str=="");
	str = str + addIfNotUrlParams(currUrl, searchVar.arr_loc, str=="");

	if (searchVar.hasOwnProperty('searchType')){
		// str = str + addIfNotUrlParams(currUrl, searchVar.searchType, str=="");

		if (!str || str != ""){
			str = str + "&";
		}

		str = str + 'searchType=' + searchVar.searchType;

	}


	// console.log(str);

	// window.history.replaceState({}, null, "?" +str);

	window.history.pushState({path:currUrl},'','?' + str);


	// window.location.search=str;
	// searchParams.set("foo", "bar");
	// window.location.search = searchParams.toString();
}

function addIfNotUrlParams(currUrl, arr_, isEmpty){
	var str = "";

	console.log("The currUrl " + currUrl);
	console.log(arr_);

	for (var i=0; i<arr_.length; i++){
		// window.history.pushState()
		if (!isEmpty || str != ""){
			str = str + "&";
		}

		for (var tn in arr_[i]){
			str = str + tn + "=" + arr_[i][tn];
		}

	}
	return (str);
}

// THE +++ AJAX SEARCH TABLE COMPONENT


function sortElemsAndSend(url, filterTblName, colsInfo, apInfo, ccInfo, serverStatusChoices, assignStatusChoices, privStatusChoices){
	let searchVals = packageElemsFromFilterTbl(filterTblName, colsInfo, apInfo, ccInfo, serverStatusChoices, assignStatusChoices, privStatusChoices);

	console.log("The searchVals are ")
	console.log(searchVals);

	if (!searchVals){
		return;
	}


	updateUrl(searchVals);
	// 3. pass to ajax function.

	let urlToSendTo = getUrlToSendToFromUrl();

	if (urlToSendTo == 'pg_searchIsoList'){
		sendToIsolateList(url, searchVals.arr_ap, searchVals.arr_cc, searchVals.arr_epi, searchVals.arr_iso, searchVals.arr_isln, searchVals.arr_loc, null, null, null, null, null, searchVals.searchType, false, false);
	}
	else if (urlToSendTo == 'pg_searchProjDetail'){
		let projId = getProjIdFromUrl();
		sendProjSearchData(url_searchProjDetail, projId, searchVals.arr_ap, searchVals.arr_cc, searchVals.arr_epi, searchVals.arr_iso, searchVals.arr_isln, searchVals.arr_loc, null, null, null, null, null, searchVals.searchType, false, false);
	}
}


function getProjIdFromUrl(){
	let res = window.location.href.replace(/^.*project\-/, '');
	let projectId = res.replace(/\-detail.*$/, '');

	return (projectId);
}

function getUrlToSendToFromUrl(){
	if (window.location.href.match(/project\-[0-9]+\-detail/)){
		return 'pg_searchProjDetail';
	}
	else{
		// defaults to isolate-list;
		return 'pg_searchIsoList';
	}
}

function packageElemsFromFilterTbl(filterTblName, colsInfo, apInfo, ccInfo, serverStatusChoices, assignStatusChoices, privStatusChoices){
	// 1. get all tds of table, and
	// 2. go through each one and add to dict (else print error messages).

	// console.log(tableRows);

	// console.log(projectId + " is project Id");

	var arr_iso = [];
	var arr_ap = [];
	var arr_cc = [];
	var arr_epi = [];
	var arr_loc = [];
	var arr_isln = [];


	// Getting the searchType 'and' or 'or'.
	let searchType = $("input[type='radio'][name='searchType']:checked").val();


	// 1. get all tds of table, and
	// 2. go through each one and add to dict.
	var tableRows = document.getElementById(filterTblName).getElementsByTagName("tr");


	for (var i = 0; i < tableRows.length; i++){


		// 1. Get values and check is ok.
		var rows = tableRows[i];
		var selectElem = rows.children[0].children[0];
		var selectedTn = selectElem[selectElem.selectedIndex].value;


		console.log("The selected tn is " + selectedTn);
		var inputVal = null;
		var secondVal = null;

		if (selectedTn == serverStatus || selectedTn == assignStatus || selectedTn == privacyStatus || selectedTn == isQuery){
			selectElem = rows.children[1].children[0];
			try{
				inputVal = selectElem[selectElem.selectedIndex].value;
			}
			catch(err){
				rows.children[rows.children.length-1].innerHTML = "Unknown value provided.";
				return;
			}
		}
		else if (selectedTn == islnYear || selectedTn == islnDate || selectedTn == islnMonth){

			inputVal = tableRows[i].getElementsByClassName("startTime")[0].value;
			secondVal = tableRows[i].getElementsByClassName("endTime")[0].value;

			inputVal = inputVal.trim(); 
			secondVal = secondVal.trim();

			if (selectedTn == islnYear || selectedTn == islnMonth){
				// 1. check is numeric
				if (!(isOkNum(inputVal) && isOkNum(secondVal))){
					rows.children[rows.children.length-1].innerHTML = "Values must be numeric.";
					return;
				}
				if (inputVal > secondVal){
					rows.children[rows.children.length-1].innerHTML = "Start must smaller than end.";
					return;
				}
			}
			else{
				if (!(isOkDate(inputVal) && isOkDate(secondVal))){
					rows.children[rows.children.length-1].innerHTML = "Date must be in the format: DD-MM-YYYY";
					return;
				}
			}
		}
		else {

			inputVal = rows.children[1].children[0].value;
			inputVal = inputVal.trim();
			if (selectedTn == locPostcode && !(isOkNum(inputVal))){
				rows.children[rows.children.length-1].innerHTML = "Numbers only.";
				return;
			}
			if (!isOkValBasicCheck(inputVal)){
				rows.children[rows.children.length-1].innerHTML = "Only alphabets, numbers, dots and spaces allowed!";
				return;
			}

			console.log(selectedTn + ' be my friend ' + inputVal);
			// inputVal = inputTd.value;

		}


		// 2. By now, all values should be hopefully ok
		rows.children[rows.children.length-1].innerHTML = ""; // clear error msg if any



		// 3. Now add value to appropriate dict. (and additional checks in ap and cc)

		var index = colsInfo.map(function(d) { return d.table_name; }).indexOf(selectedTn);

		if (index >= 0){
			if (colsInfo[index].group == groupIso){
				arr_iso = addToArr(arr_iso, selectedTn, inputVal);
			}
			else if (colsInfo[index].group == groupLoc){
				// arr_loc = isOkAddCcToDict(arr_loc, selectedTn, inputVal)
				arr_loc = addToArr(arr_loc, selectedTn, inputVal);
			}
			else if (colsInfo[index].group == groupIsln){
				if ((selectedTn == islnYear || selectedTn == islnDate || selectedTn == islnMonth) && (inputVal != secondVal)){
					// arr_isln = addToArr(arr_isln, selectedTn, inputVal);
					// arr_isln = addToArr(arr_isln, selectedTn, secondVal);
					arr_isln = addToArr(arr_isln, selectedTn+"__gte", inputVal);
					arr_isln = addToArr(arr_isln, selectedTn+"__lte", secondVal);
				}
				else{
					arr_isln = addToArr(arr_isln, selectedTn, inputVal);
				}
			}
		}

		index = apInfo.map(function(d) { return d.table_name; }).indexOf(selectedTn);
		if (index >= 0){
			// check either all numbers, or 2 numbers after splitting by '.'
			var retVal = isOkAddStDstToDict(arr_ap, selectedTn, inputVal);
			if (retVal == false){
				// print error msg.
				rows.children[rows.children.length-1].innerHTML = "Input either be completely numeric, or contain a single dot between an ST and a DST.";
				return;
			}
		}

		index = ccInfo.map(function(d) { return d.table_name; }).indexOf(selectedTn);

		if (index >= 0){
			if (!isOkNum(inputVal)){ // must only be numeric
				rows.children[rows.children.length-1].innerHTML = "Input either be completely numeric, or contain a single dot between an ST and a DST.";
				return;
			}
			addToArr(arr_cc, selectedTn, inputVal);
		}


	}

	$('#ajaxSearching').show();
	document.getElementById("filterIsolates").disabled = true;

	return {
		arr_iso: arr_iso,
		arr_ap: arr_ap,
		arr_cc: arr_cc,
		arr_epi: arr_epi,
		arr_loc: arr_loc,
		arr_isln: arr_isln,
		searchType: searchType
	};

}


function addToIsoDict(isoInfo, arr_iso, inputTd, tn, inputVal){

	var jsonObj = {};
	jsonObj[tn] = inputVal;
	arr_iso.push(jsonObj);

	return arr_iso;
}


function isPresent(apInfo, tn){

	for(var i=0; i<apInfo.length; i++){
		if (apInfo[i].table_name == tn){
			return true;
		}
	}
	return false;
}


function addToArr(arr_, tn, inputVal){
	var jsonObj = {};
	jsonObj[tn] = inputVal;
	arr_.push(jsonObj);

	return arr_;
}

function getIndexAndClass(){

}

function isOkAddStDstToDict(arr_ap, tn, inputVal){

	var arr = inputVal.split('\.');

	if (arr.length > 2){ // more than 1 dot is present.
		inputTd.classList.add("incorrect");
		return false;
	}

	if (isOkNum(arr[0]) == false || (arr.length == 2 && isOkNum(arr[1]) == false)){ // check all values are numeric
		inputTd.classList.add("incorrect");
		return false;
	}

	// add to search array for ajax

	var jsonObj = {};
	jsonObj[tn + "_st"] = arr[0];
	arr_ap.push(jsonObj);

	if (arr.length == 2){
		var jsonObj = {};
		jsonObj[tn + "_dst"] = arr[1];
		arr_ap.push(jsonObj);
	}

	return arr_ap;
}
// AJAX: order_by


// AJAX: SEARCH

function getTheBoolsForDisp(){

	let isAp = !document.getElementById('ccView').classList.contains('btn-default-spe');


	let isDst = false;
	if ($("#btn_toggleDst")){
		isDst = $("#btn_toggleDst").hasClass('btn-outline-success');
	}


	let isMgtColor = true;
	if ($("#btn_toggleCol")){
		isMgtColor = !$("#btn_toggleCol").hasClass('btn-outline-secondary');
	}

	return {
		isAp: isAp,
		isDst: isDst,
		isMgtColor: isMgtColor
	};
}




/*
function doTheAjaxOrderBy(url, order_by, dir){

	var data = {
		'order_by': order_by,
		'dir': dir,
		'isAp': document.getElementById('apView').classList.contains('is-primary'),
		// 'csrfmiddlewaretoken': '{{ csrf_token }}',
	};

	ajaxCall(url, data, doNothingSuccess);
}
*/

// ########################



// AJAX: Get initial data (on page load).
function getInitialData(url, pageNumToGet, orderBy, dir, isCsv, isMgt9Ap, isMr, isGrapeTree){
	// console.log("here!");

	var theBools = getTheBoolsForDisp();
	var data = {
		'pageNumToGet': pageNumToGet,
		'orderBy': orderBy,
		'dir': dir,
		'isAp': theBools.isAp,
		'isDst': theBools.isDst,
		'isMgtColor': theBools.isMgtColor,
		'isCsv': isCsv,
		'isMgt9Ap': isMgt9Ap,
		'isMr': isMr,
		'isGrapeTree': isGrapeTree,
	};

	console.log("The data is ");
	console.log(data);
	if (isMr == true){
		ajaxCall(url, data, downloadMrSuccess);
	}
	else if (isCsv == true){
		ajaxCall(url, data, downloadCsvSuccess);
	}
	else if (isMgt9Ap == true){
		ajaxCall(url, data, downloadMgt9ApsSuccess);
	}
	else{
		ajaxCall(url, data, doVisChngSuccess);
	}

}


// THE +++ AJAX SEARCH TABLE COMPONENT
function searchInProj(url, tblName, isoInfo, apInfo, ccInfo, epiInfo, isoMLoc, isoMIsln, projectId){

	var searchVals = sortTheElemsAndSend(tblName, isoInfo, apInfo, ccInfo, epiInfo, isoMLoc, isoMIsln);

	// add project_id to arr_iso
	if (!searchVals){
		return;
	}

	// searchVals.arr_iso.push({"project": projectId});

	// 3. pass to ajax function.
	sendProjSearchData(url, projectId, searchVals.arr_ap, searchVals.arr_cc, searchVals.arr_epi, searchVals.arr_iso, searchVals.arr_isln, searchVals.arr_loc, null, null, null, null, false, 'and', false, false);
}

function sendToIsolateList(url, arr_ap, arr_cc, arr_epi, arr_iso, arr_isln, arr_loc, pageNumToGet, orderBy, dir, isCsv, isMgt9Ap, searchType, isGrapeTree, isMr){

	var theBools = getTheBoolsForDisp();
	console.log("isAp in sendToIsolateList " + theBools.isAp + " searchType: " + searchType);

	var data= {
		'arrAp': JSON.stringify(arr_ap),
		'arrCc': JSON.stringify(arr_cc),
		'arrEpi': JSON.stringify(arr_epi),
		'arrIso': JSON.stringify(arr_iso),
		'arrIsln': JSON.stringify(arr_isln),
		'arrLoc': JSON.stringify(arr_loc),
		'isAp': theBools.isAp,
		'isDst': theBools.isDst,
		'isMgtColor': theBools.isMgtColor,
		'pageNumToGet': pageNumToGet,
		'orderBy': orderBy,
		'dir': dir,
		'isCsv':isCsv,
		'isMgt9Ap': isMgt9Ap,
		'searchType': searchType,
		'isGrapeTree': isGrapeTree,
		'isMr': isMr,
	};


	if (isMr == true){
		ajaxCall(url, data, downloadMrSuccess);
	}
	else if (isCsv == true){
		ajaxCall(url, data, downloadCsvSuccess);
	}
	else if (isMgt9Ap == true){
		ajaxCall(url, data, downloadMgt9ApsSuccess);
	}
	else{
		ajaxCall(url, data, doVisChngSuccess);
	}

}



function sendProjSearchData(url, projectId, arr_ap, arr_cc, arr_epi, arr_iso, arr_isln, arr_loc, pageNumToGet, orderBy, dir, isCsv, isMgt9Ap, searchType, isGrapeTree, isMr){
	console.log("The searchType2 is " + searchType + ", isGrapeTree: " + isGrapeTree );
	var theBools = getTheBoolsForDisp();
	var data= {
		'arrAp': JSON.stringify(arr_ap),
		'arrCc': JSON.stringify(arr_cc),
		'arrEpi': JSON.stringify(arr_epi),
		'arrIso': JSON.stringify(arr_iso),
		'arrIsln': JSON.stringify(arr_isln),
		'arrLoc': JSON.stringify(arr_loc),
		'projectId': JSON.stringify(projectId),
		'isAp': theBools.isAp,
		'isDst': theBools.isDst,
		'isMgtColor': theBools.isMgtColor,
		'pageNumToGet': pageNumToGet,
		'orderBy': orderBy,
		'dir': dir,
		'isCsv': isCsv,
		'isMgt9Ap': isMgt9Ap,
		'searchType': searchType,
		'isGrapeTree': isGrapeTree,
		'isMr': isMr,
	};

	if (isMr == true){
		ajaxCall(url, data, downloadMrSuccess);
	}
	else if (isCsv == true){
		ajaxCall(url, data, downloadCsvSuccess);
	}
	else if (isMgt9Ap == true){
		ajaxCall(url, data, downloadMgt9ApsSuccess);
	}
	else{
		ajaxCall(url, data, doVisChngSuccess);
	}

}
