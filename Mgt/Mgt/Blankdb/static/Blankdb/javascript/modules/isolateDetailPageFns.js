export {rowLayoutOfApsAndCcs, doSimHl, removeSimHl, doSmpToggle, doHighlighting, clearHighlighting, toggleHighlighting, clearHlSelection};
export {rowApId, rowCcId, rowEpiId, table_iso, selTdClassName};

var rowApId = "rowAp";
var rowCcId = "rowCc";
var rowEpiId = "rowEpi";

var selTdClassName = "theSel";
var hoverTdClassName = "theHl";

var baseColor = "theLightYellow";

//var table_loc = "tblLocation";
//var table_isln = "tblIsolation";
//var table_proj = "tblProject";
var table_iso = "tableMain";

// var table_isoMd = "tab_isoMd";


function predicateBy(prop){
   return function(a,b){
      if (a[prop] > b[prop]){
          return 1;
      } else if(a[prop] < b[prop]){
          return -1;
      }
      return 0;
   }
}


function rowLayoutOfApsAndCcs(rowName, tabApCcs, colsInfo, theIsolate, isApLine, ccTableNum){
	/* console.log(tabApCcs);
	console.log(colsInfo);
	console.log(theIsolate);
	console.log(tabApCcs.sort(predicateBy('display_order'))); */

	// function(item){
	// 	return item.display_table==2;
	// }

	var dispColCounter = 0;
	var rowAp = document.getElementById(rowName);

	let cell = rowAp.insertCell(dispColCounter++);
	cell.innerHTML = "";
	if (isApLine == false){
		tabApCcs = tabApCcs.filter(function(item){
	    	return item.display_table==ccTableNum;
		});
	}
	var maxCol = 0;
	for (var i in tabApCcs.sort(predicateBy('display_order'))) {

		cell = rowAp.insertCell(dispColCounter++);

		let id_colObj = colsInfo.find(x => x.table_name == tabApCcs[i].table_name); // this is the ap Id (next is st, then dst);
		if (isApLine == true) {
			let st_colObj = colsInfo.find(x => x.table_name == tabApCcs[i].table_name + "_st");
			let dst_colObj = colsInfo.find(x => x.table_name == tabApCcs[i].table_name + "_dst");

			// console.log(colObj.db_col);

			cell.innerHTML = theApVal(theIsolate[0][id_colObj.db_col], theIsolate[0][st_colObj.db_col], theIsolate[0][dst_colObj.db_col]);
			cell.title = "Click to select.";
		}

		if (isApLine == false) {
			var merge_colObj = colsInfo.find(x => x.table_name == tabApCcs[i].table_name + "_merge");
			// console.log(merge_colObj);
			cell.innerHTML = theCcVal(theIsolate[0][id_colObj.db_col], theIsolate[0][merge_colObj.dbCol]);
			cell.title = "Click to select.";
		}

		cell.id = id_colObj.t_search + "." + id_colObj.table_name;

		cell.setAttribute("onmouseenter", 'Blankdb_doHighlighting("' + rowName + '", ' + i + ', "'+ hoverTdClassName + '");');
		cell.setAttribute("onmouseleave", 'Blankdb_clearHighlighting("' + rowName + '", ' + i + ', "' + hoverTdClassName + '");');
		cell.setAttribute("onclick", 'Blankdb_toggleHighlighting("' + rowName + '", ' + i + ', "' + selTdClassName + '");');

		// console.log(cell[0]);
		// cell.style.bgColor = "#fff5c3";
		cell.classList.add(baseColor);

		maxCol = i + 1;
	}

	console.log("Max col is " + maxCol);
	if (isApLine == true){
		cell = rowAp.insertCell(dispColCounter++);
		cell.innerHTML = '<input type="checkbox" id="isPerfectSt"> (Only include complete STs)<button type="button" class="btn" data-toggle="modal" data-target="#exampleModal" data-whatever="@isoDetailOnlyComplSt" onclick="theHelpFns(this);"><span class=\'fas fa-info-circle\'> </span></button>';
		// cell.classList.add(baseColor);
	}

}


function clearHlSelection(className){
	clearAllHighlightingInTbl(table_iso, className);
	clearAllHighlighting(rowApId, className);
	clearAllHighlighting(rowCcId, className);
	clearAllHighlighting(rowEpiId, className);
	// clearAllHighlightingInTbl(table_loc, className);
	// clearAllHighlightingInTbl(table_isln, className);
	// clearAllHighlightingInTbl(table_proj, className);

	document.getElementById("isPerfectSt").checked = false;
}


function clearAllHighlightingInTbl(tblName, className){
	// console.log(tblName);

	if (! document.getElementById(tblName)){
		return;
	}
	var cells = document.getElementById(tblName).getElementsByTagName("td");

	// console.log(cells);
	for (var i=0; i < cells.length; i++){
		if(cells[i].classList.contains(className)){
			cells[i].classList.remove(className);
			cells[i].classList.add(baseColor);
		}
	}
}


function doSimHl(elemId, className){

	var cell = document.getElementById(elemId);
	cell.classList.remove(baseColor);
	cell.classList.add(className);
}

function removeSimHl(elemId, className){
	var cell = document.getElementById(elemId);
	cell.classList.remove(className);
	if (cell.classList.length == 0){
		cell.classList.add(baseColor);
	}


}

function doSmpToggle(elemId, className){
	var cell = document.getElementById(elemId);
	if(cell.classList.contains(className)){
		cell.classList.remove(className);
	}
	else {
		// cell.classList.remove(baseColor);
		cell.classList.add(className);
	}
}

function doHighlighting(rowName, colNum, className){
	var cells = document.getElementById(rowName).getElementsByTagName("td");
	cells[colNum+1].classList.remove(baseColor);
	cells[colNum+1].classList.add(className);
}

function clearAllHighlighting(rowName, className){
	var cells = document.getElementById(rowName).getElementsByTagName("td");



	for (var i = 1; i < cells.length; i++){
		// console.log(cells[i]);
		if (cells[i].classList.contains(className)){
			cells[i].classList.remove(className);
			cells[i].classList.add(baseColor);
		}
	}

}
function toggleHighlighting(rowName, colNum, className){
	// console.log(rowName);
	// console.log(colNum);
	var cells = document.getElementById(rowName).getElementsByTagName("td");

	if (cells[colNum+1].classList.contains(className)){
		cells[colNum+1].classList.remove(className);
		// cells[colNum+1].classList.add(baseColor);
	}
	else {
		cells[colNum+1].classList.remove(baseColor);
		cells[colNum+1].classList.add(className);
	}

}

function clearHighlighting(rowName, colNum, className){
	var cells = document.getElementById(rowName).getElementsByTagName("td");


	cells[colNum+1].classList.remove(className);

	if (cells[colNum+1].classList.length == 0){
		cells[colNum+1].classList.add(baseColor);
	}

}

/* Getting values of the individual cells */
function theApVal(idVal, stVal, dstVal){

	if (idVal == null){
		return "-";
	}
	else {
		var retStr =  stVal;

		if (dstVal != 0){
			retStr = retStr + "." + dstVal;
		}
	}

	return (retStr);
}

function theCcVal(idVal, mergeVal){

	if (idVal == null){
		return "-";
	}

	if (mergeVal < idVal){
		return mergeVal;
	}


	return (idVal) ;
}
