export {switchDisplayDst, switchDisplayColor};
// TOGGLE DST/MGT_COLOR

import {doApLayout, doCcLayout} from './layoutApCcTable.js'; 


function switchDisplayColor(btnId, isolates, searchVar, colsInfo, tabAps, tabCcs, serverStatusChoices, assignStatusChoices, privStatusChoices){
	var visualized = 'btn-default-spe';
	var notVisualized = 'btn-default-outline-spe';

	var btn = $("#" + btnId);

	// Toggle class on button.
	toggleClass(btnId, visualized, notVisualized);

	var isShowCol = btn.hasClass(visualized);

	var isApView = $("#apView").hasClass(visualized);

	if (isApView == true){
		var isShowDst = $("#btn_toggleDst").hasClass(visualized);
		// Call doApLayout()
		doApLayout(isolates, searchVar, isShowCol, isShowDst, colsInfo, tabAps, tabCcs, serverStatusChoices, assignStatusChoices, privStatusChoices);
	}
	else{
		// Call doCcLayout()
		doCcLayout(isolates, searchVar, isShowCol, colsInfo, tabAps, tabCcs, serverStatusChoices, assignStatusChoices, privStatusChoices);
	}

}

function switchDisplayDst(btnId, isolates, searchVar, colsInfo, tabAps, tabCcs, serverStatusChoices, assignStatusChoices, privStatusChoices){
	var visualized = 'btn-default-spe';
	var notVisualized = 'btn-default-outline-spe';

	var btn = $("#" + btnId);
	// Toggle class on button.
	toggleClass(btnId, visualized, notVisualized);

	var isShowDst = $(btn).hasClass(visualized);

	var isShowCol = $("#btn_toggleCol").hasClass(visualized);

	// Call doApLayout()
	doApLayout(isolates, searchVar, isShowCol, isShowDst, colsInfo, tabAps, tabCcs, serverStatusChoices, assignStatusChoices, privStatusChoices);

}
