export {printCcMergeInfo};

import {divMergedIdsDisplay} from './constants.js'; 

// [CC|EPI] MERGE INFO DISPLAY
function printCcMergeInfo(mergedInfo, tabCcs){
	// console.log(mergedInfo);
	console.log("Int he print CcMerge Info function");
	var isAnyMerged = false;
	var tableStr = "<div class=\"box\">  <h6 class=\"speHeading\"> Merged clonal and epidemeology complexes: <button type=\"button\" class=\"btn\" data-toggle=\"modal\" data-target=\"#exampleModal\" data-whatever=\"@mergedCcOdc\" onclick=\"theHelpFns(this)\"><span class='fas fa-info-circle'> </span></button></h6> <table class=\"table is-bordered is-small\">";

	for (var tn in mergedInfo){
		if (mergedInfo.hasOwnProperty(tn)){
			if (mergedInfo[tn].length > 1){
				var ccObj = tabCcs.find(x => x.table_name == tn);

				tableStr = tableStr + "<tr> <td>" + ccObj.display_name + "</td> <td> " + mergedInfo[tn] + " </td> </tr>";

				isAnyMerged = true;
			}
		}
	}

	tableStr = tableStr + "</table> </div>";

	console.log(isAnyMerged);
	if (isAnyMerged == true){
		document.getElementById(divMergedIdsDisplay).insertAdjacentHTML('beforeend', tableStr);

		// unhide the display;
		document.getElementById(divMergedIdsDisplay).style.display = "";
	}

}
