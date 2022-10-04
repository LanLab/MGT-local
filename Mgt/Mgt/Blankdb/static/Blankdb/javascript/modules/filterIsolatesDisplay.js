export {addRowToFilterTbl};

import {getUrlToSendToFromUrl} from './packageAndSend.js';
import {privacyStatus, assignStatus, serverStatus, isQuery, islnYear, islnDate, islnMonth} from './constants.js';
import {rmProjectFromSel} from './projectDetail_initSearch.js';

function addRowToFilterTbl(tblStr, isoAndMdInfo, apInfo, ccInfo, serverStatusChoices, assignStatusChoices, privStatusChoices, searchedCol, searchedVal, boolChoices){

	console.log('In addRowToFilterTbl:');
	console.log(boolChoices);

	var tbl = document.getElementById(tblStr);
	var row = tbl.insertRow();

	// 1st col
	var cell = row.insertCell();
	var select = document.createElement('SELECT');
	if (getUrlToSendToFromUrl() == 'pg_searchProjDetail'){
		// remove 'Project' from the selection.
		rmProjectFromSel(isoAndMdInfo);
	}
	printSelectStr_isoMd(select, isoAndMdInfo, searchedCol);
	searchedVal = printSelectStr_ap(select, apInfo, searchedCol, searchedVal, "Sequence type", "ST");
	printSelectStr_cc(select, ccInfo, searchedCol, ["Clonal clusters", "Outbreak clusters"], "CC");
	select.onchange = function(){
		changeToSel(this, serverStatusChoices, assignStatusChoices, privStatusChoices, boolChoices);
	};
	cell.appendChild(select);

	// http://localhost:8000/blankdb/isolate-list?year__gte=2010&year__lte=2020


	// 2nd col
	var value = "";
	var cell2 = row.insertCell();
	var inputBox = document.createElement("input");
	if (searchedVal){ // add selected select box
		if ( (searchedCol == privacyStatus || searchedCol == assignStatus || searchedCol == serverStatus || searchedCol == isQuery) && (searchedVal in serverStatusChoices || searchedVal in assignStatusChoices || searchedVal in privStatusChoices || searchedVal in boolChoices)) {
			changeToSel(select, serverStatusChoices, assignStatusChoices, privStatusChoices, boolChoices, searchedVal);
			// inputBox.value=searchedVal;
		}
		else if(searchedCol == islnYear || searchedCol == islnDate || searchedCol == islnMonth){
			changeToSel(select, serverStatusChoices, assignStatusChoices, privStatusChoices, boolChoices, searchedVal);
		}
		else{ // add value in input box.
			inputBox.value=searchedVal;
			cell2.appendChild(inputBox);
		}

	}
	else{
		cell2.appendChild(inputBox);
	}




	// 3rd col
	var cell3 = row.insertCell();
	var plusBtn = document.createElement("button");
	plusBtn.innerText = '+';
	plusBtn.title = 'Add another search row';
	plusBtn.classList.add("btn");
	plusBtn.classList.add("btn-default-outline-spe");
	cell3.appendChild(plusBtn); // (attach function)
	plusBtn.onclick = function(){
		addRowToFilterTbl(tblStr, isoAndMdInfo, apInfo, ccInfo, serverStatusChoices, assignStatusChoices, privStatusChoices, null, null, boolChoices);
	};


	// 4th col
	var cell3 = row.insertCell();
	var plusBtn = document.createElement("button");
	plusBtn.innerText = '-';
	plusBtn.title = 'Delete this row';
	plusBtn.classList.add("btn");
	plusBtn.classList.add("btn-default-outline-spe");
	cell3.appendChild(plusBtn); // (attach function)
	plusBtn.onclick =function(){delCurrRow(plusBtn);};

	// 5th error col
	var cell5 = row.insertCell();
	cell5.classList.add('rowError');
}



function addRowFromBtn(addBtn, isoInfo, apInfo, ccInfo, epiInfo, isoMIsln, isoMLoc){

	var tbl = addBtn.parentNode.parentNode.parentNode;
	addRowToFilterTbl(tbl, isoInfo, apInfo, ccInfo, epiInfo, isoMLoc, isoMIsln, null, null);
}


function delCurrRow(delBtn){

	var row = delBtn.parentNode.parentNode;
	row.parentNode.removeChild(row);
}



///////////////////////////




function getDisplayName(tn, ccInfo, epiInfo){

	for (var i=0; i<ccInfo.length; i++){
		if (ccInfo[i].table_name == tn){
			// console.log("Display name: " + ccInfo[i].display_name);
			return ccInfo[i].display_name;
		}
	}

	for (var j=0; j<epiInfo.length; j++){
		if (epiInfo[j].table_name == tn){
			// console.log("Display name: " + ccInfo[i].display_name);
			return epiInfo[j].display_name;
		}
	}
}



function addPrevSearchToFilterTbl(searchedParams, isoAndMdInfo, apInfo, ccInfo, serverStatusChoices, assignStatusChoices, privStatusChoices){
	var aps = {};


	for (var tn in aps){
		value = aps[tn][0];
		if (aps[tn][1] != null){
			value = value + "." + aps[tn][1];
		}
		addRowToFilterTbl(theSearchTbl,
		isoHeader, apHeader, ccHeader, epiHeader, locHeader, islnHeader, tn, value);
	}
}



// SEARCH BOX DISPLAY IMPL.



function changeToSel(selObj, serverStatusChoices, assignStatusChoices, privStatusChoices, boolChoices, selectedVal){
	// serverStatusChoices = JSON.parse(serverStatusChoices);
	// console.log(serverStatusChoices);
	// console.log("in this fun.");
	// console.log("now go thru, check and update where necessary");
	console.log(' the sel obj is ' + selObj);
	var tr = $(selObj).closest('tr');
	console.log(tr);

	if (selObj.value == serverStatus){
		tr[0].cells[1].innerHTML = createSelStr(serverStatusChoices, selectedVal);
	}
	else if (selObj.value == assignStatus){
		tr[0].cells[1].innerHTML = createSelStr(assignStatusChoices, selectedVal);
	}
	else if (selObj.value == privacyStatus){
		tr[0].cells[1].innerHTML = createSelStr(privStatusChoices, selectedVal);
	}
	else if (selObj.value == isQuery){
		console.log('Comes here...?');
		console.log(boolChoices);
		tr[0].cells[1].innerHTML = createSelStr(boolChoices, selectedVal);
	}
	else if (selObj.value == islnYear || selObj.value == islnMonth){
	// else if (selObj.value.match(/^year/) || selObj.value.match(/^date/) || selObj.value.match(/^month/)){
		// console.log(tr[0]);
		// var inputBox = document.createElement("input");
		// tr[0].insertCell(inputBox);


		let innerStr  = "Start: <input class=\"startTime\" type=\"text\" size=4 ";
		if (selectedVal && selectedVal.length > 1){
			innerStr = innerStr + 'value=\"' + selectedVal[0] + "\"";
		}
		innerStr = innerStr + "> &nbsp;&nbsp; End: <input class=\"endTime\" type=\"text\" size=4 ";
		if (selectedVal && selectedVal.length > 1){
			innerStr = innerStr + 'value=\"' + selectedVal[1] + "\"";
		}
		innerStr = innerStr + ">";

		tr[0].cells[1].innerHTML = innerStr;
	}
	else if (selObj.value == islnDate){
	// else if (selObj.value.match(/^year/) || selObj.value.match(/^date/) || selObj.value.match(/^month/)){
		// console.log(tr[0]);
		// var inputBox = document.createElement("input");
		// tr[0].insertCell(inputBox);


		let innerStr  = "Start: <input class=\"startTime\" type=\"date\" size=4 ";
		if (selectedVal && selectedVal.length > 1){
			innerStr = innerStr + 'value=\"' + selectedVal[0] + "\"";
		}
		innerStr = innerStr + "> &nbsp;&nbsp; End: <input class=\"endTime\" type=\"date\" size=4 ";
		if (selectedVal && selectedVal.length > 1){
			innerStr = innerStr + 'value=\"' + selectedVal[1] + "\"";
		}
		innerStr = innerStr + ">";

		tr[0].cells[1].innerHTML = innerStr;
	}
	else{
		tr[0].cells[1].innerHTML = "<input class=\"txtInpt\" type=\"text\">";
	}

}

function createSelStr(statusChoices, selectedVal){

	var selStr = "<select class=\"srvrStatusSel\">";
	for (var key in statusChoices) {
	    if (statusChoices.hasOwnProperty(key)) {
			var selected = "";
			if (selectedVal && selectedVal == key){
				selected = "selected";
			}
	        selStr = selStr + " <option value=\"" + key + "\" "+ selected + " > " + statusChoices[key] + "</option>";
	    }
	}
	selStr = selStr + "</select>";

	return selStr;
}


function checkCol2(selObj){
	console.log("now go thru, check and update where necessary");
	// console.log(selObj.value);
	var tr = $(selObj).closest('tr');

	if (selObj.value == serverStatus){
		// console.log(tr[0].cells[1].innerHTML);
		// console.log("change to sel box");

		var selStr = "<select class=\"srvrStatusSel\">";
		for (var i=0; i<serverStatusStr.length; i++){
			selStr = selStr + " <option value=\"" + serverStatusStr[i].value + "\"> " + serverStatusStr[i].option + "</option>";
		}
		selStr = selStr + "</select>";
		tr[0].cells[1].innerHTML = selStr;
	}
	else if (selObj.value == assignStatus){
		var selStr = "<select class=\"assignStatusSel\">";
		for (var i=0; i<assignStatusStr.length; i++){
			selStr = selStr + " <option value=\"" + assignStatusStr[i].value + "\"> " + assignStatusStr[i].option + "</option>";
		}
		selStr = selStr + "</select>";
		tr[0].cells[1].innerHTML = selStr;

	}
	else if (selObj.value == privacyStatus) {
		var selStr = "<select class=\"privStatusSel\">";
		for (var i=0; i<privacyStatusStr.length; i++){
			selStr = selStr + " <option value=\"" + privacyStatusStr[i].value + "\"> " + privacyStatusStr[i].option + "</option>";
		}
		selStr = selStr + "</select>";
		tr[0].cells[1].innerHTML = selStr;
	}
	else if (selObj.value == islnYear) {
		tr[0].cells[1].innerHTML = "Start year: <input class=\"startTime\" type=\"text\" size=4> &nbsp;&nbsp; End year: <input class=\"endTime\" type=\"text\" size=4>";
	}
	else if (selObj.value == islnDate){
		tr[0].cells[1].innerHTML = "Start date: <input type=\"date\" class=\"startTime\"> &nbsp;&nbsp; End date: <input type=\"date\" class=\"endTime\">";
	}
	else {
		tr[0].cells[1].innerHTML = "<input class=\"txtInpt\" type=\"text\">";
	}


	// console.log(selObj.value)
}




function printSelectApStr(apInfo, groupStr, typeDispStr, tnUrl){

	var str = "<optgroup label='" + groupStr + "'>";


	for  (var i = 0; i< apInfo.length; i++){
		var selected = "";
		if (tnUrl && tnUrl == apInfo[i].table_name){
			selected = "selected";
		}
		str = str + "<option value='" + apInfo[i].table_name + "' " + selected + " >";
		str = str + apInfo[i].scheme__display_name;

		if (typeDispStr){
			str = str + " - " + typeDispStr;
		}
		str = str + "</option>";
	}
	str = str + "</optgroup>";

	return str;
}


function printSelectStr_cc(selectObj, apInfo, tnSearchSelect, groupList, typeDispStr){

	// console.log("inside the function " + tnSearchSelect);

	var optgroup = document.createElement("optgroup");
	optgroup.label = groupList[apInfo[0].display_table-1];
	selectObj.add(optgroup);



	for  (var i = 0; i < apInfo.length; i++){
		if (i > 0 && apInfo[i-1].display_table != apInfo[i].display_table){

			optgroup = document.createElement("optgroup");
			optgroup.label = groupList[apInfo[i].display_table-1];
			selectObj.add(optgroup);
		}

		var option = document.createElement("option");
		option.text = apInfo[i].display_name;  //+ " - " + typeDispStr;
		option.value = apInfo[i].table_name;

		// var selected = "";
		if (tnSearchSelect && tnSearchSelect == apInfo[i].table_name){
			option.selected = true;
		}



		if (apInfo[i].hasOwnProperty('display_table') && apInfo[i].display_table == 1) {

			option.text = option.text + " - " + typeDispStr;

		}


		optgroup.appendChild(option);
	}

}

function printSelectStr_ap(selectObj, apInfo, tnSearchSelect, searchedVal, groupStr, typeDispStr){

	// console.log(tnSearchSelect);

	var optgroup = document.createElement("optgroup");
	optgroup.label = groupStr;
	selectObj.add(optgroup);

	for  (var i = 0; i< apInfo.length; i++){

		var option = document.createElement("option");
		option.text = apInfo[i].display_name + " - " + typeDispStr;
		option.value = apInfo[i].table_name;

		if (tnSearchSelect && tnSearchSelect ==
		apInfo[i].table_name){
			option.selected = true;
			var convertedVal = searchedVal;
			searchedVal = convertedVal[0];
			if (convertedVal[1] != null){
				searchedVal = searchedVal + '.' + convertedVal[1];
			}
		}

		optgroup.appendChild(option);

	}
	return searchedVal;

}

function printSelectStr_isoMd(selectObj, dirColsInfo, tnSearchSelect){

	var optGroup = "";
	// var str = ""; //= "<optgroup label='" + groupStr + "'>";

	var optgroup = null;

	for  (var i = 0; i< dirColsInfo.length; i++){

		if (optGroup != dirColsInfo[i].group){ // print optgroup



			optgroup = document.createElement("optgroup");
			optgroup.label = dirColsInfo[i].group;
			selectObj.add(optgroup);



			optGroup = dirColsInfo[i].group;

		}


		var selected = false;
		// console.log("booze cruize " + tnSearchSelect + " " + dirColsInfo[i].table_name);
		if (tnSearchSelect && tnSearchSelect == dirColsInfo[i].table_name){
			selected = true;
			// console.log("Over herereerere eerere ");
		}


		// adding option to optgroup
		var option = document.createElement("option");
		option.text = dirColsInfo[i].display_name;
		option.value = dirColsInfo[i].table_name;
		if (selected==true){
			option.setAttribute('selected', selected);
		}
		optgroup.appendChild(option);


	}

}


function printSelectCcStr(selectObj, apInfo, groupStr, typeDispStr, tnUrl){

	var str = "<optgroup label='" + groupStr + "'>";


	for  (var i = 0; i< apInfo.length; i++){
		var selected = "";
		if (tnUrl && tnUrl == apInfo[i].table_name){
			selected = "selected";
		}

		str = str + "<option value='" + apInfo[i].table_name + "' " + selected + " >";


		str = str + apInfo[i].display_name;

		if (typeDispStr){
			str = str + " - " + typeDispStr;
		}

		str = str + "</option>";


	}
	str = str + "</optgroup>";

	return str;
}
