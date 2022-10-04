
export {doApLayout, doCcLayout};
// LAYOUT OF ALL TABLES #################################
/* module.exports = {
	doApLayout: doApLayout,
}
*/

import {getRandomColor} from './generateColors.js';
import {sort_forward, sort_reverse} from './constants.js';


function getCellInnerHtml(table_name, display_name, tnStr, sessionVar, searchVar_str){
	// console.log(table_name + " " + display_name + " " + tnStr + " " + sessionVar + " " + searchVar_str);
	var tnToChk = tnStr + "." + table_name;
	var innerStr = '<b> <button title="Click to sort table using values in this column." id=\'' + table_name + '\'';
	var classes = "btn speLink";

	if (sessionVar[0].hasOwnProperty('orderBy') && tnToChk == sessionVar[0].orderBy) {
		classes = classes + ' ' + sessionVar[0].dir;
	}
	innerStr = innerStr + ' class="' + classes + '" ';

	innerStr = innerStr +  ' onclick="javascript:Blankdb_doTheOrderBy(\'' + table_name + '\', \'' + searchVar_str + '\', \'' + tnStr + '\')"> <b> ' + display_name ;
	if (sessionVar[0].hasOwnProperty('orderBy') && tnToChk == sessionVar[0].orderBy && sessionVar[0].dir == sort_forward) {
		innerStr  =  innerStr + '<sup>v</sup>';
	}
	else if (sessionVar[0].hasOwnProperty('orderBy') && tnToChk == sessionVar[0].orderBy && sessionVar[0].dir == sort_reverse){
		innerStr  =  innerStr + '<sup>^</sup>';
	}
	else{
	}
	innerStr = innerStr + " </b> </button> </b>";

	return (innerStr);
}


function printHeader(row, isAp, searchVar, colsInfo, tabAps, tabCcs){ // , apOrCcHeader, isAp, epiHeader, locHeader, isolnHeader, isPriv){


	// row.classList = "";
 	row.classList.add('tblHeaderRow');




	var dispColCounter = 0;

	// console.log("over here!!!!");
	// console.log(isoInfo);

	var searchVar_str = JSON.stringify(searchVar);
	searchVar_str = searchVar_str.replace(/\"/g, "\\'");

	// searchVar_str = searchVar_str.replace(/\".i)
	// searchVar_str = searchVar_str.replace(/\\/g, '\'');

	var isEmptyAdded = false;

	var i = 0;
	while (i<colsInfo.length){

		// Ids
		if (colsInfo[i].table_name.toLowerCase() == 'id' || colsInfo[i].table_name.toLowerCase() == 'mgt' || colsInfo[i].table_name.toLowerCase() == 'mgt_id'){
			// console.log("id or mgtid encountered do nothing");
		}
		// Ap
		else if (i < colsInfo.length-1 && colsInfo[i+1].table_name.match(/\_st$/)){ // if st, dst encountered!

			if(isAp == true){
				// console.log("only to print these");
				let apObj = tabAps.find(x => x.table_name == colsInfo[i].table_name);
				// console.log("ap " + colsInfo[i].table_name + " " + apObj.display_name);
				// console.log(apObj);

				var cell = row.insertCell(dispColCounter++);
				cell.classList.add('bdr-default');



				var innerStr = getCellInnerHtml(apObj.table_name, apObj.display_name, colsInfo[i].t_search, searchVar, searchVar_str);
				cell.innerHTML = innerStr;


			}


			i = i + 2;




		}
		// Ccs table 1
		else if (i < colsInfo.length-1 && colsInfo[i+1].table_name.match(/\_merge$/) && colsInfo[i].table_name.match(/1_[0-9]+$/)){

			if (!isAp || isAp==false){
				// console.log("presidential ");
				// console.log(colsInfo[i]);

				let ccObj = tabCcs.find(x => x.table_name == colsInfo[i].table_name);

				// console.log(ccObj);
				var cell = row.insertCell(dispColCounter++);
				cell.classList.add('bdr-default');

				var innerStr = getCellInnerHtml(ccObj.table_name, ccObj.display_name, colsInfo[i].t_search, searchVar, searchVar_str);
				cell.innerHTML = innerStr;
			}

			i = i + 1;


		}
		// Ccs table 2
		else if (i < colsInfo.length-1 && colsInfo[i+1].table_name.match(/\_merge$/) && colsInfo[i].table_name.match(/2_[0-9]+$/)){


			// add empty column
			if (isEmptyAdded == false) {
				var cell = row.insertCell(dispColCounter++);
				cell.innerHTML = "";
				isEmptyAdded = true;
			}


			let ccObj = tabCcs.find(x => x.table_name == colsInfo[i].table_name);

			if (!ccObj){
				// console.log(colsInfo[i]);
				var aCol = colsInfo[i];
				var name = aCol.table_name.replace('cc', '');
				var vals = name.split('\_');
				// console.log(vals);
				ccObj = tabCcs.find(x => x.display_table == vals[0] && x.display_order == vals[1]);
			}

			// console.log("cc " + (colsInfo[i]) + " " + ccObj.display_name);

			var cell = row.insertCell(dispColCounter++);
			cell.classList.add('bdr-default');

			var innerStr = getCellInnerHtml(ccObj.table_name, ccObj.display_name, colsInfo[i].t_search, searchVar, searchVar_str);
			cell.innerHTML = innerStr;
			i = i + 1;
		}
		// Isolate, project, aps, ccs
		else {
			// console.log("to print: " + colsInfo[i].table_name + " " + colsInfo[i].t_search);
			var cell = row.insertCell(dispColCounter++);
			cell.classList.add('bdr-default');

			var innerStr = getCellInnerHtml(colsInfo[i].table_name, colsInfo[i].display_name, colsInfo[i].t_search, searchVar, searchVar_str);
			cell.innerHTML = innerStr;
		}


		i++;
	}
}






function isValExist(val){
	// console.log(val);
	if (typeof val === 'undefined' || val === ''){
		return false;
	}

	return true;
}

function numToColor(num) {
    num >>>= 0;
    var b = parseInt(num) & 0xFF,
        g = (parseInt(num) & 0xFF00) >>> 8,
        r = (parseInt(num) & 0xFF0000) >>> 16,
        a = ( (parseInt(num) & 0xFF000000) >>> 24 ) / 255 ;
    return "rgba(" + [r, g, b, a].join(",") + ")";
}





function doCcLayout(isolates, searchVar, isShowCol, colsInfo, tabAps, tabCcs, serverStatusChoices, assignStatusChoices, privStatusChoices){

	console.log("The isolates are");
	console.log(isolates);

	$('#tabularViewDiv').show();
	$('#graphicalViewDiv').hide();

	$('#isolateTable').show();

	// Make cc active, and ap secondary.
	removeClassFromBtn("apView", "btn-default-spe");
	removeClassFromBtn("graphicalView", "btn-default-spe");

	addClassToBtn("ccView", "btn-default-spe");
	// Disable DST (since it's only required for ap view).
	toggleDisableBtn("btn_toggleDst", true);
	// Check if isDisplayColor (only check if isShowCol == NULL?, i.e. not passed in through the server).
	// if (isShowCol == null){
	var isShowCol = document.getElementById("btn_toggleCol").classList.contains('btn-default-spe');
	// 	console.log('IsShowCol ' + isShowCol);
	// }

	var tab = document.getElementById("infoTable");
	tab.innerHTML = "";

	if (isolates.length == 0){
		tab.innerHTML = "No isolates here.";
		return;
	}




	var dispRowCounter = 0;

	var tab = document.getElementById("infoTable");
	tab.innerHTML = "";


	var cell = null;
	var dict_colors = {stCol: {}, hue: 0};

	var isolateId = colsInfo.find(x => x.table_name.toLowerCase() == "id" && x.t_search == 'i');

	var row = tab.insertRow(dispRowCounter++);
	printHeader(row, false, searchVar, colsInfo, tabAps, tabCcs);

	for (var i=0; i<isolates.length; i++){
		row = tab.insertRow(dispRowCounter++);

		// dispColCounter = 0;

		dict_colors = printTheIsoRow(row, isolates[i], colsInfo, serverStatusChoices, assignStatusChoices, privStatusChoices, isolateId.db_col, false, isShowCol, false, dict_colors);
	}
}




function updateHue(hue){

	hue = hue * 12;

	if (hue > 360){
		hue = hue % 360;
	}
	return (hue);
}

function getColor(hue){
	return ("hsl(" + hue + ", 90%, 80% )");
	// https://stackoverflow.com/questions/43193341/how-to-generate-random-pastel-or-brighter-color-in-javascript
}


var rgbToHex = function (rgb) {
  var hex = Number(rgb).toString(16);
  if (hex.length < 2) {
       hex = "0" + hex;
  }
  hex = "#" + (hex & 0x00FFFFFF).toString(rgb);
  return hex;
};



function RainBowColor(length, maxLength)
{
    var i = (length * 255 / maxLength);
    var r = Math.round(Math.sin(0.024 * i + 0) * 127 + 128);
    var g = Math.round(Math.sin(0.024 * i + 2) * 127 + 128);
    var b = Math.round(Math.sin(0.024 * i + 4) * 127 + 128);
    return 'rgb(' + r + ',' + g + ',' + b + ')';
}
function addColorToDictIfNotPesent(colKey, i, dict_colors){

	if (!dict_colors.stCol.hasOwnProperty(colKey)){
		dict_colors.hue = updateHue(dict_colors.hue);
		var num = colKey;
		if (num.match(/\_/)){
			num = num.replace(/^.+\_/, '');
		}

		// theColor = RainBowColor(num, 100);
		// theColor = rainbow(num);
		// theColor =  numToColor(num); //
		let theColor = getRandomColor(num, i, 0.5); // getColor(hue);
		// theColor = rgbToHex(num);
		// theColor = ('#' + num.toString(16).padStart(6, '0'));

		// theColor = getColor(updateHue(num));
		// console.log("The color is " + theColor + " the num is " + num + " colorKey is " + colKey);
		dict_colors.stCol[colKey] = theColor;
	}

	return (dict_colors);
}


function RGBAToHexA(rgba) {
  let sep = rgba.indexOf(",") > -1 ? "," : " ";
  rgba = rgba.substr(5).split(")")[0].split(sep);

  // Strip the slash if using space-separated syntax
  if (rgba.indexOf("/") > -1)
    rgba.splice(3,1);

  for (let R in rgba) {
    let r = rgba[R];
    if (r.indexOf("%") > -1) {
      let p = r.substr(0,r.length - 1) / 100;

      if (R < 3) {
        rgba[R] = Math.round(p * 255);
      } else {
        rgba[R] = p;
      }
    }
  }
}

var Url_isolateList = "isolate-list";
function printTheIsoRow(row, isolate, colsInfo, serverStatusChoices, assignStatusChoices, privStatusChoices, isolateIdCol, isAp, isShowCol, isShowDst, dict_colors){

	var dispColCounter = 0;
	var isEmptyAdded = false;
	var i = 0;
	var colKey = "";
	var isIsoIdentifierPrint = false;

	while (i < colsInfo.length){

		// Ids
		if (colsInfo[i].table_name.toLowerCase() == 'id' || colsInfo[i].table_name.toLowerCase() == 'mgt' || colsInfo[i].table_name.toLowerCase() == 'mgt_id'){
			// console.log("id or mgtid encountered do nothing");
		}
		else if (i < colsInfo.length-1 && colsInfo[i+1].table_name.match(/\_st$/)){ // if st, dst encountered!

			if(isAp == true){

				var cell = row.insertCell(dispColCounter++);

				if (isolate[colsInfo[i+1].db_col] == null){
					cell.innerHTML = '-';
				}
				else{

					var theInnerHtml = isolate[colsInfo[i+1].db_col];
					var theInnerLink = "<a title=\"Clear to search isolates with this value.\" class=\"speLinkOpp\" href=\"" + Url_isolateList + "?" + colsInfo[i+1].table_name + "=" + isolate[colsInfo[i+1].db_col];
					// cell.innerHTML = isolate[colsInfo[i+1].db_col];

					// Start: set color

					colKey = (colsInfo[i+1].db_col) + "_" + isolate[colsInfo[i+1].db_col];

					// console.log(colKey);

					dict_colors = addColorToDictIfNotPesent(colKey, i, dict_colors);

					if (isShowCol == true) {
						cell.style.backgroundColor = dict_colors.stCol[colKey];
					}



					if (isShowDst == true){
						if (isolate[colsInfo[i+2].db_col] != 0){
							// cell.innerHTML = cell.innerHTML + "." + isolate[colsInfo[i+2].db_col];
							theInnerHtml = theInnerHtml + "." + isolate[colsInfo[i+2].db_col];
							theInnerLink = theInnerLink + "&" + colsInfo[i+2].table_name + "=" + isolate[colsInfo[i+2].db_col];

						}
					}
					theInnerLink = theInnerLink + "\">" + theInnerHtml + "</a>";
					cell.innerHTML = theInnerLink; //theInnerHtml;
					// cell.classList.add('btn');
				}

			}

			i = i + 2;
		}

		// Ccs table 1
		else if (i < colsInfo.length-1 && colsInfo[i+1].table_name.match(/\_merge$/) && colsInfo[i].table_name.match(/1_[0-9]+$/)){

			if (!isAp || isAp==false){
				var cell = row.insertCell(dispColCounter++);
				if (isolate[colsInfo[i].db_col] == null){
					cell.innerHTML = "-";
				}
				else{
					colKey = "";

					var theInnerHtml = null;
					var theInnerLink = "<a title=\"Clear to search isolates with this value.\" class=\"speLinkOpp\" href=\"" + Url_isolateList + "?";

					if (isolate[colsInfo[i+1].db_col] != null){ // if cc_merge
						var minCc = Math.min(isolate[colsInfo[i].db_col], isolate[colsInfo[i+1].db_col]);
						// cell.innerHTML = minCc;

						theInnerHtml = minCc;
						colKey = colsInfo[i].db_col +"_" + minCc;
					}
					else{
						// cell.innerHTML = isolate[colsInfo[i].db_col];
						theInnerHtml = isolate[colsInfo[i].db_col];
						colKey = colsInfo[i].db_col + "_" + isolate[colsInfo[i].db_col];
					}

					theInnerLink = theInnerLink + colsInfo[i].table_name + "=" + theInnerHtml + "\">" + theInnerHtml + "</a>";
					cell.innerHTML = theInnerLink;

					dict_colors = addColorToDictIfNotPesent(colKey, i, dict_colors);

					if (isShowCol == true){
						cell.style.backgroundColor = dict_colors.stCol[colKey];
					}

					// console.log(theInnerLink);
				}


			}

			i = i + 1;


		}

		// Ccs table 2
		else if (i < colsInfo.length-1 && colsInfo[i+1].table_name.match(/\_merge$/) && colsInfo[i].table_name.match(/2_[0-9]+$/)){


			// add empty column
			if (isEmptyAdded == false) {
				var cell = row.insertCell(dispColCounter++);
				cell.innerHTML = "";
				isEmptyAdded = true;
			}

			var cell = row.insertCell(dispColCounter++);
			if (isolate[colsInfo[i].db_col] == null){
				cell.innerHTML = "-";
			}
			else {

				colKey = "";

				var theInnerHtml = null;
				var theInnerLink = "<a title=\"Clear to search isolates with this value.\" class=\"speLinkOpp\" href=\"" + Url_isolateList + "?";

				if (isolate[colsInfo[i+1].db_col] != null){
					var minCc = Math.min(isolate[colsInfo[i].db_col], isolate[colsInfo[i+1].db_col]);
					// cell.innerHTML = minCc;
					theInnerHtml = minCc;
					colKey = colsInfo[i].db_col +"_" + minCc;

				}
				else{
					// cell.innerHTML = isolate[colsInfo[i].db_col];
					theInnerHtml = isolate[colsInfo[i].db_col];
					colKey = colsInfo[i].db_col +"_" + isolate[colsInfo[i].db_col];
				}

				theInnerLink = theInnerLink + colsInfo[i].table_name + "=" + theInnerHtml + "\">" + theInnerHtml + "</a>";
				cell.innerHTML = theInnerLink;
				dict_colors = addColorToDictIfNotPesent(colKey, i, dict_colors);


				if (isShowCol == true){
					cell.style.backgroundColor = dict_colors.stCol[colKey];
				}
			}
			i = i + 1;
		}
		// Isolate, project, aps, ccs
		else {
			// console.log("to print: " + colsInfo[i].table_name + " " + colsInfo[i].t_search);

			if (colsInfo[i].table_name.toLowerCase() == 'identifier' && isIsoIdentifierPrint == false){
				var cell = row.insertCell(dispColCounter++);
				cell.innerHTML = "<a class=\"speLink\" href=\"/blankdb/isolate-" + isolate[colsInfo[isolateIdCol].db_col] + "-detail\">" + isolate[colsInfo[i].db_col]+  "</a>";
				isIsoIdentifierPrint = true;
			}

			else if (colsInfo[i].table_name.toLowerCase() == 'server_status'){

				var cell = row.insertCell(dispColCounter++);
				cell.innerHTML = serverStatusChoices[isolate[colsInfo[i].db_col]];
				// console.log(colsInfo[i]);
			}

			else if (colsInfo[i].table_name.toLowerCase() == 'assignment_status'){
				var cell = row.insertCell(dispColCounter++);
				if (isolate[colsInfo[i].db_col]){
					cell.innerHTML = assignStatusChoices[isolate[colsInfo[i].db_col]];
				}
				else {
					cell.innerHTML = '-';
				}
			}

			else if (colsInfo[i].table_name.toLowerCase() == 'privacy_status'){
				var cell = row.insertCell(dispColCounter++);
				cell.innerHTML = privStatusChoices[isolate[colsInfo[i].db_col]];
			}

			else{
				var cell = row.insertCell(dispColCounter++);
				cell.innerHTML = isolate[colsInfo[i].db_col];

			}
		}

		i++;
	}

	return dict_colors;

}


function doApLayout(isolates, searchVar, isShowCol, isShowDst, colsInfo, tabAps, tabCcs, serverStatusChoices, assignStatusChoices, privStatusChoices){

	// console.log(serverStatusChoices);


	$('#tabularViewDiv').show();
	$('#graphicalViewDiv').hide();



	$('#isolateTable').show();

	removeClassFromBtn("ccView", "btn-default-spe");
	removeClassFromBtn("graphicalView", "btn-default-spe");
	addClassToBtn("apView", "btn-default-spe");
	toggleDisableBtn("btn_toggleDst", false);

	var isShowCol = document.getElementById("btn_toggleCol").classList.contains('btn-default-spe');
	var isShowDst = document.getElementById("btn_toggleDst").classList.contains('btn-default-spe');

	var tab = document.getElementById("infoTable");
	tab.innerHTML = "";

	if (isolates.length == 0){
		tab.innerHTML = "No isolates here.";
		return;
	}

	var dispRowCounter = 0;
	var dict_colors = {stCol: {}, hue: 0};

	var cell = null;



		// var theColor = getRandomColor(); // getColor(hue);


	var row = tab.insertRow(dispRowCounter++);
	var isolateId = colsInfo.find(x => x.table_name.toLowerCase() == "id" && x.t_search == 'i');



	printHeader(row, true, searchVar, colsInfo, tabAps, tabCcs);

	// console.log(colsInfo);

	for (var i=0; i<isolates.length; i++){
		row = tab.insertRow(dispRowCounter++);

		//dispColCounter = 0;

		dict_colors = printTheIsoRow(row, isolates[i], colsInfo, serverStatusChoices, assignStatusChoices, privStatusChoices, isolateId.db_col, true, isShowCol, isShowDst, dict_colors);

	}
	return (dict_colors);


	// console.log(dict_colors);

}
