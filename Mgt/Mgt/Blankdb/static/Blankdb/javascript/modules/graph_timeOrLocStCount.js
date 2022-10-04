
export {handleGraphicalViewClick, get_timeStCount, plotLvl2_stCcOdc, plotLvl1_timeLoc};
export {drawButtons_init, ZoomBy, switchClassesForMultipleBtns, checkAndSendToPlotLvl3, getColsToBuildDict, getTheColsToAggrBy, getZoomByDisplayText, writeDownloadLink};
import {getRandomColor} from './generateColors.js';
import {ajaxCall} from './packageAndSend.js';


function handleGraphicalViewClick(){
	removeClassFromBtn("apView", "btn-default-spe");
	removeClassFromBtn("ccView", "btn-default-spe");
	addClassToBtn("graphicalView", "btn-default-spe");

	// Hide an overall div?
	$('#tabularViewDiv').hide();
	$('#graphicalViewDiv').show();
}

// Button/button-div names:
const lvl1_time = "graph_timeStCnt_btn_time";
const lvl1_loc = "graph_timeStCnt_btn_loc";
const lvl2_st = "graph_timeStCnt_btn_st";
const lvl2_cc = "graph_timeStCnt_btn_cc";
const lvl2_odc = "graph_timeStCnt_btn_odc";
const lvl3_btnsDivSt = "graph_timeStCnt_btnDiv_ap";
const lvl3_btnsDivCc = "graph_timeStCnt_btnDiv_cc";
const lvl3_btnsDivOdc = "graph_timeStCnt_btnDiv_odc";
const Lvl3_btn_pattern = "graph_timeStCnt_btn_";
const StackBy_isoCount = "stackBy_isoCount";
const StackBy_StNum = "stackBy_StNum";
const Btn_bgStrains = "btn_bgStrains";
const Btn_topN = "btn_topN";


const ZoomBy = {
	'time':
		{year: 'Year',
		month: 'Month',
		date: 'Date'},
	'location':
		{continent: 'Continent',
		country: 'Country',
		state: 'State',
		postcode: 'Postcode'}
	};
// var d3 = require("d3");

const limitForSingletons = 1000;
const Singletons = 'Singletons';
 
const limitForLegend = 10; 


// Send data and make ajax call.
function get_timeStCount(tabAps, tabCcsOdcs){

	// console.log(tabAps);
	// console.log(tabCcsOdcs);
	$("#loading_timeStCount").show();

	drawButtons_init(tabAps, tabCcsOdcs, lvl3_btnsDivSt, lvl3_btnsDivCc, lvl3_btnsDivOdc, Lvl3_btn_pattern);

	ajaxCall('/Blankdb/timeStCount', {}, handle_timeStCount);

	document.getElementById('btn_timeStCount').remove();
	// console.log("here?");
}

// Handle results from server
function handle_timeStCount(respData){

	console.log("The timeStCount response is");
	// console.log(respData);
	let parsedRespData = JSON.parse(respData);

	let response = [];
	let bgData = [];


	if (parsedRespData.hasOwnProperty('data')){
		response = parsedRespData.data;

		console.log(response);
	}
	if (parsedRespData.hasOwnProperty('background')){
		bgData = parsedRespData.background;
		// Attach events to bg button.
		attachEventsToBgBtn(response, bgData);
		attachEventsToTopNBtn(response);
	}
	else {
		attachEventsToTopNBtn(response);
	}
	// Handle when no data is present...

	// Attach data to onclick to the buttons;
	attachEventsToButtons_init(response, lvl3_btnsDivSt, []);
	attachEventsToButtons_init(response, lvl3_btnsDivCc, []);
	attachEventsToButtons_init(response, lvl3_btnsDivOdc, []);

	// Attach events to stackby buttons:
	attachEventsToStackByBtn(response, StackBy_isoCount, StackBy_StNum, []);
	attachEventsToStackByBtn(response, StackBy_StNum, StackBy_isoCount, []);
	// Default stackby is isoCount;
	addClassToBtn(StackBy_isoCount, "btn-default-spe");

	// Attach events to zoomby buttons:
	attachEventsToZoomByBtns(response, []);
	//Default zoomby is year;
	addClassToBtn("zoomBy_year", "btn-default-spe");

	// Show the buttons
	$('#graph_timeStCount_btns').show();
	$('#stackBy_zoomBy').show();
	// Do the time, St, Mgt2St plot.

	$("#loading_timeStCount").hide();
	$("#btnsAndPlot_timeStCount").show();

	// console.log('Total number of isolates: ' + JSON.parse(response).length);
	plotLvl1_timeLoc(lvl1_time);
}

/////////////////////////////////////// Highlight top N strains
/* function highlightTopN(respData){
	console.log("Highlight top N");
} */ 

/////////////////////////////////////// Background strains in projects
function toggleBgStrains(btnId, respData, bgData){


	let lvlChoices = readThe3LvlChoices();
	// let currentLvlChoice = document.getElementsByClassName('xAxisText')[0].id;
	// console.log(currentLvlChoice);
	let stackByChoice = getTheStackByChoice();
	let zoomByChoice = readTheZoomByChoice();

	let theTopNVal = checkAndGetTopNVal();

	if (document.getElementById(btnId).classList.contains('btn-default-outline-spe')){
		// alert('add bg strains');
		removeClassFromBtn(btnId, "btn-default-outline-spe");
		addClassToBtn(btnId, "btn-default-spe");

		transformTheDataForPlot(respData, lvlChoices.lvl1, lvlChoices.lvl2, lvlChoices.lvl3, zoomByChoice, stackByChoice, bgData, theTopNVal);
	}
	else{
		// alert('remove bg strains');
		removeClassFromBtn(btnId, "btn-default-spe");
		addClassToBtn(btnId, "btn-default-outline-spe");

		transformTheDataForPlot(respData, lvlChoices.lvl1, lvlChoices.lvl2, lvlChoices.lvl3, zoomByChoice, stackByChoice, [], theTopNVal);

	}

}


 ////////////////////////////////////// Buttons

function drawButtons_init(tabAps, tabCcsOdcs, divIdBtn_ap, divIdBtn_cc, divIdBtn_odc, lvl3BtnPtn){

	// console.log("in the draw buttons thingo");
	let div_btnAp = document.getElementById(divIdBtn_ap);
	let div_btnCc = document.getElementById(divIdBtn_cc);
	let div_btnOdc = document.getElementById(divIdBtn_odc);

	tabAps.forEach(function(ap, ap_i){
		div_btnAp.innerHTML += "<button id=\"" + lvl3BtnPtn + ap.table_name + "\" class=\"btn btn-sm btn-default-outline-spe\">" + ap.display_name + "</button>";
	});

	// if cc, odc, append, display_table in button id.
	tabCcsOdcs.forEach(function(ccOdc, ccOdc_i){
		if (ccOdc.display_table == 1){
			div_btnCc.innerHTML += "<button id=\"" + lvl3BtnPtn + ccOdc.table_name + "_" + ccOdc.display_table + "\" class=\"btn btn-sm btn-default-outline-spe\">" + ccOdc.display_name + "</button>";
		}
		else if (ccOdc.display_table == 2){
			div_btnOdc.innerHTML += "<button id=\"" + lvl3BtnPtn + ccOdc.table_name + "_" + ccOdc.display_table + "\" class=\"btn btn-sm btn-default-outline-spe\">" + ccOdc.display_name + "</button>";
		}
	});

}


function attachEventsToTopNBtn(response){
	document.getElementById(Btn_topN).onclick = function(){

		let theInputVal = checkAndGetTopNVal();

		if (theInputVal === null){
			return;
		}

		// getTheLvl3Choices()
		let lvlChoices = readThe3LvlChoices();

		// getTheZoomyChoice()
		let zoomByChoice = readTheZoomByChoice();

		// getTheStackByChoice()
		let stackByChoice = getTheStackByChoice();
		// bgData == [] // i.e. empty

		checkAndTurnOffBgBtn([]); 
		// transformTheDataForPlot(response, )
		transformTheDataForPlot(response, lvlChoices.lvl1, lvlChoices.lvl2, lvlChoices.lvl3, zoomByChoice, stackByChoice, [], theInputVal);
	};
}
function checkAndGetTopNVal(){
	let inputVal = document.getElementById('input_topN');

	if (!isOkNum(inputVal.value)){
		console.log("The provided input is not a number");
		return 0;
	}

	return inputVal.value;
}

function attachEventsToBgBtn(response, bgData){

	document.getElementById(Btn_bgStrains).onclick = function(){
		toggleBgStrains(Btn_bgStrains, response, bgData);
	};
}


function attachEventsToZoomByBtns(respData, bgData){

	Object.keys(ZoomBy).forEach(function(timeLoc, timeLoc_i){
		Object.keys(ZoomBy[timeLoc]).forEach(function(item, i){
			document.getElementById('zoomBy_' + item).onclick = function(){
				let topN = 0;
				if (document.getElementById(Btn_topN)){
					topN = checkAndGetTopNVal();
				}
				changeZoomLvl(respData, item, bgData, topN);
				zoomBy_switchBtns(item, 'zoomBy_');
			};
		});
	});

}

function getZoomByDisplayText(zoomBy){
	let displayText = '';
	Object.keys(ZoomBy).forEach(function(timeLoc, timeLoc_i){
		Object.keys(ZoomBy[timeLoc]).forEach(function(item, i){
			if (item == zoomBy){
				displayText = ZoomBy[timeLoc][item];
			}
		});
	});
	return displayText;
}

function zoomBy_switchBtns(clickedBtn, zoomBy_btnPtn){
	Object.keys(ZoomBy).forEach(function(timeLoc, timeLoc_i){
		Object.keys(ZoomBy[timeLoc]).forEach(function(item, i){
			if (item == clickedBtn){
				removeClassFromBtn(zoomBy_btnPtn + item, "btn-default-outline-spe");
				addClassToBtn(zoomBy_btnPtn + item, "btn-default-spe");
			}
			else {
				removeClassFromBtn(zoomBy_btnPtn + item, "btn-default-spe");
				addClassToBtn(zoomBy_btnPtn + item, "btn-default-outline-spe");
			}
		});
	});
}

function readTheZoomByChoice(){
	let zoomByChoice = '';
	Object.keys(ZoomBy).forEach(function(timeLoc, timeLoc_i){
		Object.keys(ZoomBy[timeLoc]).forEach(function(item, i){
			if (document.getElementById("zoomBy_" + item).classList.contains('btn-default-spe')) {
				zoomByChoice = item;
			}
		});
	});

	return (zoomByChoice);
}

function attachEventsToStackByBtn(respData, btnId, otherBtnId, bgData){
	document.getElementById(btnId).onclick = function(){
		// console.log("weeehehhheeee");
		let lvlChoices = readThe3LvlChoices();
		let zoomByChoice = readTheZoomByChoice();

		// console.log("The zoombychoice is " + zoomByChoice);
		let topN = 0;
		if (document.getElementById(Btn_topN)){
			topN = checkAndGetTopNVal();
		}

		transformTheDataForPlot(respData, lvlChoices.lvl1, lvlChoices.lvl2, lvlChoices.lvl3, zoomByChoice, btnId, bgData, topN);

		removeClassFromBtn(btnId, "btn-default-outline-spe");
		addClassToBtn(btnId, "btn-default-spe");

		removeClassFromBtn(otherBtnId, "btn-default-spe");
		addClassToBtn(otherBtnId, "btn-default-outline-spe");

		checkAndTurnOffBgBtn(bgData);
	};
}


function attachEventsToButtons_init(respData, divIdBtn_apCcOdc, bgData, topN){

	// Attach events to ap buttons
	let apCcOdcBtns = document.getElementById(divIdBtn_apCcOdc).querySelectorAll("button");
	apCcOdcBtns.forEach(function(aBtn, aBtn_i){
		aBtn.onclick = function(){
			let topN = 0;
			if (document.getElementById(Btn_topN)){
				topN = checkAndGetTopNVal();
			}
			plotLvl3(aBtn.id, divIdBtn_apCcOdc, respData, bgData, topN);
		};
	});

}


////////////////////////////// Plotting functions

function plotLvl1_timeLoc(inputClickedBtn){

	let clickedBtn = inputClickedBtn;
	let notClickedBtn = undefined;
 	// Unselect loc. button; Select time button;
	if (inputClickedBtn == lvl1_time){
		notClickedBtn = lvl1_loc;
		$('#zoomBy_time').show();
		$('#zoomBy_location').hide();
		zoomBy_switchBtns('year', 'zoomBy_');
	}
	else {
		notClickedBtn = lvl1_time;
		$('#zoomBy_location').show();
		$('#zoomBy_time').hide();
		zoomBy_switchBtns('country', 'zoomBy_');
	}

	removeClassFromBtn(clickedBtn, "btn-default-outline-spe");
	addClassToBtn(clickedBtn, "btn-default-spe");

	removeClassFromBtn(notClickedBtn, "btn-default-spe");
	addClassToBtn(notClickedBtn, "btn-default-outline-spe");

	console.log("The input clicked button is " + inputClickedBtn);

	// then defer to lvl 2; which then defers to lvl 3;
	plotLvl2_stCcOdc();
}

function plotLvl2_stCcOdc(inputClickedBtn){


	let clickedBtn = inputClickedBtn;
	let otherBtns = [];

	let divToShow = '';
	let divsToHide = [];

	if (typeof inputClickedBtn == "undefined" || inputClickedBtn === undefined || inputClickedBtn == null || inputClickedBtn == ''){
		// check if any already selected ...
		if (isBtnSelected(lvl2_st, 'btn-default-spe') == true){
			document.getElementById("stackBy_StNum").innerHTML = 'ST identifier';
			clickedBtn = lvl2_st;
			otherBtns.push(lvl2_cc); otherBtns.push(lvl2_odc);
			divToShow = lvl3_btnsDivSt;
			divsToHide.push(lvl3_btnsDivCc); divsToHide.push(lvl3_btnsDivOdc);
			// console.log("Is it this case??? case 1");
		}
		else if (isBtnSelected(lvl2_cc, 'btn-default-spe') == true){
			document.getElementById("stackBy_StNum").innerHTML = 'CC identifier';
			clickedBtn = lvl2_cc;
			otherBtns.push(lvl2_st); otherBtns.push(lvl2_odc);
			divToShow = lvl3_btnsDivCc;
			divsToHide.push(lvl3_btnsDivSt); divsToHide.push(lvl3_btnsDivOdc);
			// console.log("Is it this case??? case 2");
		}
		else if (isBtnSelected(lvl2_odc, 'btn-default-spe') == true){
			document.getElementById("stackBy_StNum").innerHTML = 'ODC identifier';
			clickedBtn = lvl2_odc;
			otherBtns.push(lvl2_st); otherBtns.push(lvl2_cc);
			divToShow = lvl3_btnsDivOdc;
			divsToHide.push(lvl3_btnsDivSt); divsToHide.push(lvl3_btnsDivCc);
			// console.log("Is it this case??? case 3");
		}
		else { // else: if no button is selected
			document.getElementById("stackBy_StNum").innerHTML = 'ST identifier';
			clickedBtn = lvl2_st;
			otherBtns.push(lvl2_cc); otherBtns.push(lvl2_odc);
			divToShow = lvl3_btnsDivSt;
			divsToHide.push(lvl3_btnsDivCc); divsToHide.push(lvl3_btnsDivOdc);
			// console.log("Is it this case??? case 4");
		}

	}
	else{

		if (clickedBtn == lvl2_st){
			// clickedBtn = lvl2_st;
			document.getElementById("stackBy_StNum").innerHTML = 'ST identifier';
			otherBtns.push(lvl2_cc); otherBtns.push(lvl2_odc);
			divToShow = lvl3_btnsDivSt;
			divsToHide.push(lvl3_btnsDivCc); divsToHide.push(lvl3_btnsDivOdc);
			// console.log("Is it this case??? case 5");
		}
		else if (clickedBtn == lvl2_cc){
			// clickedBtn = lvl2_cc;
			document.getElementById("stackBy_StNum").innerHTML = 'CC identifier';
			otherBtns.push(lvl2_st); otherBtns.push(lvl2_odc);
			divToShow = lvl3_btnsDivCc;
			divsToHide.push(lvl3_btnsDivSt); divsToHide.push(lvl3_btnsDivOdc);
			// console.log("Is it this case??? case 6");
		}
		else {
			// clickedBtn = lvl2_odc;
			document.getElementById("stackBy_StNum").innerHTML = 'ODC identifier';
			otherBtns.push(lvl2_st); otherBtns.push(lvl2_cc);
			divToShow = lvl3_btnsDivOdc;
			divsToHide.push(lvl3_btnsDivSt); divsToHide.push(lvl3_btnsDivCc);
			// console.log("Is it this case??? case 7");
		}
	}

	// console.log("how about over here...?");
	if(clickedBtn){
		removeClassFromBtn(clickedBtn, "btn-default-outline-spe");
		addClassToBtn(clickedBtn, "btn-default-spe");
	}

	if (otherBtns.length > 0){
		switchClassesForMultipleBtns(otherBtns);
	}


	// switch the divs;
	if (divToShow){
		$("#" + divToShow).show();
	}

	divsToHide.forEach(function(divId, divId_i){
		$("#" + divId).hide();
	});

	console.log("The lvl 2 is "); 
	console.log(divToShow); 
	// handle level 3 here.
	// if something is already selected pass that on.
	// else manually click mgt2st || mgt2cc || odc1
	checkAndSendToPlotLvl3(divToShow);
}


function plotLvl3(inputClickedBtnId, divIdBtn, respData, bgData, topN){
	$("#loading_timeStCount").show();

	let theBtns = document.getElementById(divIdBtn).querySelectorAll("button");

	theBtns.forEach(function(aBtn, aBtn_i){
		if (aBtn.id == inputClickedBtnId){
			addClassToBtn(aBtn.id, 'btn-default-spe');
			removeClassFromBtn(aBtn.id, 'btn-default-outline-spe');
		}
		else if (aBtn.id != inputClickedBtnId){
			addClassToBtn(aBtn.id, 'btn-default-outline-spe');
			removeClassFromBtn(aBtn.id, 'btn-default-spe');
		}
	});

	// 1. transform the data.
	// 2. plot the transformed data.

	let lvl1_choice = lvl1_time;
	let lvl2_choice = lvl2_st;

	if  (document.getElementById(lvl1_loc).classList.contains('btn-default-spe')){
		lvl1_choice = lvl1_loc;
	}

	if (document.getElementById(lvl2_cc).classList.contains('btn-default-spe')){
		lvl2_choice = lvl2_cc;
	}
	else if (document.getElementById(lvl2_odc).classList.contains('btn-default-spe')){
		lvl2_choice = lvl2_odc;
	}


	let zoomByChoice = readTheZoomByChoice();
	let stackByChoice = getTheStackByChoice();

	let res_data_col = transformTheDataForPlot(respData, lvl1_choice, lvl2_choice, inputClickedBtnId, zoomByChoice, stackByChoice, bgData, topN);

	checkAndTurnOffBgBtn(bgData);
}

function checkAndTurnOffBgBtn(bgData){
	let btn_bg = document.getElementById(Btn_bgStrains);

	if (bgData.length == 0 && typeof(btn_bg) != undefined && btn_bg != null){

		removeClassFromBtn(Btn_bgStrains, "btn-default-spe");
		addClassToBtn(Btn_bgStrains, "btn-default-outline-spe");

	}
}


function transformTheDataForPlot(respData, lvl1_choice, lvl2_choice, lvl3_choice, zoomLvl, stackBy, bgData, topN){
	// console.log("The choices are: " + lvl1_choice + " " + lvl2_choice + " " + lvl3_choice);

	// Get colNums;
	let colNums = getColsToBuildDict(respData[0], lvl3_choice, Lvl3_btn_pattern);
	console.log("IS IT THIS ONE?? " + lvl1_choice + " " + zoomLvl); 

	// Get data;
	if (zoomLvl == null && lvl1_choice == lvl1_time){
		zoomLvl = 'year';
		zoomBy_switchBtns('year', 'zoomBy_');
	}
	else if (zoomLvl == null && lvl1_choice == lvl1_loc){
		zoomLvl = 'country';
		zoomBy_switchBtns('country', 'zoomBy_');
	}
	if (stackBy == null){
		removeClassFromBtn(StackBy_StNum, "btn-default-spe");
		addClassToBtn(StackBy_isoCount, "btn-default-spe");

		addClassToBtn(StackBy_StNum, "btn-default-outline-spe");
		removeClassFromBtn(StackBy_isoCount, "btn-default-outline-spe");
	}

	let aggByCols = getTheColsToAggrBy(zoomLvl);
	// let res_data_col = doTheTransformation(respData, colNums, aggByCols);

	// console.log("The agg by cols are:");
	// console.log(aggByCols);

	let res_data_col = {};
	if (bgData.length == 0){
		// i.e. no bgData
		let res_data_col = doTheTransformation(respData, colNums, aggByCols);
		let dataForPlot_singletons = convertToSingletons(res_data_col.data_forPlot, res_data_col.dict_colors); 
		let highestTotal = addTotalToObjs(dataForPlot_singletons, res_data_col.dict_colors);
		doThePlot_timeStCount(dataForPlot_singletons, res_data_col.dict_colors, zoomLvl, respData, stackBy, topN, highestTotal);
		plotTheLegend(res_data_col.dict_colors, limitForLegend);
	}
	else if (bgData.length > 0){
		let res_data_col = doTheTransformation_bg(respData, colNums, aggByCols, bgData);
		let highestTotal = addTotalToObjs_bg(res_data_col.data_forPlot);
		doThePlot_timeStCount_bg(res_data_col.data_forPlot, res_data_col.dict_colors, zoomLvl, respData, stackBy, highestTotal, topN);
	}
	// Minor modifications for plot


	// console.log(data_forPlot);
	// let listOfKeyNames = buildDictForColor(data_forPlot);
	// console.log(data_forPlot);

	// doThePlot_timeStCount(data_forPlot, listOfKeyNames);

	return(res_data_col);
}

function doTheStackBy_bg(stackBy, keys){
	if (stackBy == StackBy_StNum){
		let sortedKeys = doTheStackBy_(stackBy, keys);
		return (sortedKeys);
	}
	else {
		let sortedKeys = Object.keys(keys).sort(function(a,b){

			return keys[b].total - keys[a].total;

		});
		// sortedKeys.push('name');
		// sortedKeys.push('total');
		return sortedKeys;

	}
}

function doTheStackBy_(stackBy, keys){
	if (stackBy == StackBy_StNum){
		let sortedKeys = Object.keys(keys).sort(function(a,b){
			//console.log(a + " ... " + b);
			if (a == 'name' || a == 'total'){
				return b;
			}
			else if (b == 'name' || b == 'total'){
				return a;
			}
			else if (a == Singletons){
				return 1;
			}
			else if (b == Singletons){
				return -1;
			}
			else {
				let c = a.replace(/(ST|CC|ODC)/, '');
				let d = b.replace(/(ST|CC|ODC)/, '');
				// console.log(c + ' ... ... ... ' + d);
				return c - d;

			}

		});
		// console.log("sorted by stnum");
		return sortedKeys;
	}
	else {
		// console.log("In the other function stNum");
		// delete sortedKeys.name;
		// delete sortedKeys.total;
		let sortedKeys = Object.keys(keys).sort(function(a,b){

			if (a == Singletons){
				return 1;
			}
			else if (b == Singletons){
				return -1;
			}
			else {
				return keys[b] - keys[a];
			}
			

		});
		// sortedKeys.push('name');
		// sortedKeys.push('total');
		return sortedKeys;
	}
}


function readThe3LvlChoices(){
	let lvlChoices = {lvl1: lvl1_time, lvl2: lvl2_st, lvl3: ''};
	let lvl3BtnDiv = lvl3_btnsDivSt;

	if (document.getElementById(lvl1_loc).classList.contains('btn-default-spe')){
		lvlChoices.lvl1 = lvl1_loc;
	}

	if (document.getElementById(lvl2_cc).classList.contains('btn-default-spe')){
		lvlChoices.lvl2 = lvl2_cc;
		lvl3BtnDiv = lvl3_btnsDivCc;
	}
	else if (document.getElementById(lvl2_odc).classList.contains('btn-default-spe')){
		lvlChoices.lvl2 = lvl2_odc;
		lvl3BtnDiv = lvl3_btnsDivOdc;
	}

	let lvl3Btns = document.getElementById(lvl3BtnDiv).querySelectorAll("button");

	lvl3Btns.forEach(function(aBtn, aBtn_i){
		if (aBtn.classList.contains('btn-default-spe')){
			lvlChoices.lvl3 = aBtn.id;
		}
	});

	// console.log(lvlChoices);

	return (lvlChoices);
}

function buildDictForColor(data_forPlot){
	let series_forPlot = [];

	data_forPlot.forEach(function(item, i){
		for (var [key_, val_] of Object.entries(item)){
			if (key_ != 'name' && key_ != 'total'){
				// let found = series_forPlot.some(el => el.key == key_);
				if (!series_forPlot.includes(key_)){
					series_forPlot.push(key_);
				}
			}
		}
	});
	// console.log("Array for color");
	// console.log(series_forPlot);
	return (series_forPlot);
}

function plotTheLegend(dict_colors, totalToPlot){

	console.log(dict_colors); 

	let sortedKeys = Object.keys(dict_colors).sort(function(a, b){
		return dict_colors[b].total - dict_colors[a].total;
	});


	document.getElementById('legend_timeStCount_plot').innerHTML = "";
	if (sortedKeys.length == 0){
		document.getElementById('legend_timeStCount').style.visibility = "hidden";	
		return;
	}
	else {
		document.getElementById('legend_timeStCount').style.visibility = "";	
	}


	console.log('Legend sortedKeys are:');
	console.log(sortedKeys);

	let theChart_svg = d3.select("#legend_timeStCount_plot")
	.style("overflow-x", "scroll")
	// .style("overflow-y", "scroll")
    .style("-webkit-overflow-scrolling", "touch")
	.append("svg")
	.style("display", "block")
	.attr('id', 'legend_timeStCount_svg')
	.attr("xmlns", "http://www.w3.org/2000/svg");

	let g = theChart_svg.append("g");
	let xPos = 0; 
	let x_incr = 100; 
	for (let i=0; i<totalToPlot && i < sortedKeys.length; i++){
		console.log(sortedKeys[i] + ' (' + dict_colors[sortedKeys[i]].total + ')');

		let box = g.append('rect')
		.attr('width', 10)
		.attr('height', 10)
		.attr('x', xPos + 'px')
		.attr('y', 30)
		.style('fill', function(){
			if (dict_colors.hasOwnProperty(sortedKeys[i])){
				return (dict_colors[sortedKeys[i]].color);
			}
			return ('white');
		})
		.style('stroke', function(){
			if (dict_colors.hasOwnProperty(sortedKeys[i])){
				return (dict_colors[sortedKeys[i]].color);
			}
			return ('white');
		})
		.style('stroke-width', 1)
		.style('stroke-opacity', 0.75)
		.style('opacity', 0.75);

		let legendStr = sortedKeys[i] + ' (' + dict_colors[sortedKeys[i]].total + ')'; 

		g.append("text")
		.attr('x', xPos + 12 + 'px')
		.attr('y', 40)
		// .attr('dy', '.5em')
		.attr('font-size', '10px')
		.attr('font-family', "monospace")
		.style('text-anchor', 'left')
		.text(legendStr)
		.attr("class", "xAxisText");

		xPos = xPos + legendStr.length * 10; 


		// xPos = xPos + x_incr; 

		
	}

	xPos = xPos + 100;
	theChart_svg.attr("width", xPos + 'px');// .attr("viewBox", "0,0,150,420");

}

function doThePlot_timeStCount(data_forPlot, dict_colors, zoomLvl, respData, stackBy, topN, highestTotal){

	// console.log("The heads of the department " + topN);
	$("#loading_timeStCount").hide();
	if (data_forPlot.length == 0){
		document.getElementById("plot_timeStCount").innerHTML = "No data available.";
		return;
	}
	document.getElementById("plot_timeStCount").innerHTML = "";
	$('#g1_tooltip').remove();
	// const svg = d3.create('svg')
	// .attr("viewBox", [0, 0, width, height]);
	// console.log(data_forPlot);
	// console.log(dict_colors);

	let maxPlotHeight = 650;

	let margin = {top: 30, right: 20, bottom: 80, left: 20};
	let barX_incr = 25 + 10;


	var minX = 0;
	var maxX = data_forPlot.length * barX_incr;
	let barX_start = 60;
	var overwidthX = maxX - minX + margin.left + margin.right + barX_start;
	let maxY = 0;

	// get max in Y dir using total in dict
	data_forPlot.forEach(function(anObj, anObj_i){
		if (anObj.total > maxY){
			maxY = anObj.total;
		}
	});

	var overwidthY = maxPlotHeight + margin.top + margin.bottom; // maxY + margin.top + margin.bottom;

	// Chart
	// let height = 500 - margin.top - margin.bottom;

	let theChart_svg = d3.select("#plot_timeStCount")
	//.style("overflow-x", "scroll")
	//.style("overflow-y", "scroll")
    .style("-webkit-overflow-scrolling", "touch")
	.append("svg")
	.style("display", "block")
	.attr('id', 'svg_timeStCount');


	theChart_svg.attr("width", overwidthX)
		.attr("height", overwidthY);

	let toolTip = d3.select("#btnsAndPlot_timeStCount")
		.append("div")
		.attr('id', 'g1_tooltip')
	    .attr("class", "tooltip")
		.style('background', 'beige')
		.style('border-radius', '8px')
		.style('padding', '2px')
		.style('border-color', '#cabfd9')
		.style('border-style', 'solid')
		.style('text-align', 'center');
    //.style("opacity", 0.2);
	let xAxisArr = [];

	let g = theChart_svg.append("g");


	let barX = barX_start; // start position
 	let barX_width = 20 + 10;
	sortXAxisLabelData(zoomLvl, data_forPlot);


	if (topN > 0){
		dict_colors = restrictColorsByTopN(dict_colors, topN, data_forPlot, false);
	}

	for (let i = 0; i < data_forPlot.length; i++){ // xaxis sorting (i.e sorting on name. )
		let barY = maxPlotHeight;
		let sortedKeys = doTheStackBy_(stackBy, data_forPlot[i]);
		// Object.keys(data_forPlot[i]).sort().forEach(function(key){

		sortedKeys.forEach(function(key, key_i){


		// for (let key in data_forPlot[i]){
			// let barY = maxY;
			if (key == 'name'){
				xAxisArr.push(data_forPlot[i][key]);
			}
			if (key != 'name' && key != 'total'){
				let scaledHeight = (data_forPlot[i][key]/highestTotal) * maxPlotHeight;
				barY = barY - scaledHeight;
				let bar = g.append('rect')
					.attr('width', barX_width)
					.attr('height', scaledHeight)
					.attr('x', barX)
					.attr('y', barY)
					.style('fill', function(){
						if (dict_colors.hasOwnProperty(key)){
							return (dict_colors[key].color);
						}
						return ('white');
					})
					.style('opacity', function(){
						if (dict_colors.hasOwnProperty(key)){
							return 0.75;
						}
						return 0.3;
					})
					.style('stroke', function(){
						if (dict_colors.hasOwnProperty(key)){
							return (dict_colors[key].color);
						}
						return ('white');
					})
					.style('stroke-width', 1)
					.style('stroke-opacity', 0.75);

				bar.data([data_forPlot[i]])
					.on("mouseenter", function(d){
						d3.select(this)
							// .classed('active', true);
							// .style('opacity', 1)
							.style('stroke-width', 5);


						toolTip.transition()
							///.duration(200)
							.style("opacity", 1);
							toolTip.html("<b>" + key + "</b> <br> Count: "+ data_forPlot[i][key])
								.style("left", event.pageX + "px")
								.style("top", event.pageY + "px");
					})
					.on("mouseleave", function(d) {
						// d3.select(this)
						// 	.classed('active', false);
						d3.select(this)
							// .classed('active', true);
							// .style('opacity', 1)
							.style('stroke-width', 1);

						toolTip.transition()
						// .duration(500)
						.style("opacity", 0);
					});


				// barY = barY - data_forPlot[i][key];
			}
		});
		barX = barX + barX_incr;
	}
	// console.log(xAxisArr);
	// X-axis
	// Create scale
	let x_scale = d3.scaleBand()
		.domain(xAxisArr)
		.range([0, maxX]);

	let y_scale = d3.scaleLinear()
		.domain([0, maxY])
		.range([maxPlotHeight, 0]);
		// .ticks().concat([0, maxY+1]);
		// .nice();



   // Add scales to axis
	let x_axis = d3.axisBottom()
	//	.attr("transform", "translate(0,50)")
		.scale(x_scale);

	let y_axis = d3.axisLeft()
	//	.attr("transform", "translate(0,50)")
		.scale(y_scale);

	if (maxY < 100){
		y_axis.tickValues(d3.range(0, maxY, maxY/10));
	}


	let xAxis = g.append('g')
		.call(x_axis);

	xAxis.attr("transform", "translate(" + barX_start + ", " + maxPlotHeight + ")")
		.selectAll("text")
		.style("text-anchor", "end")
		.attr("dx", "-.8em")
		.attr("dy", "-.5em")
		.attr("transform", "rotate(-60)");
	// xAxis.on('dblclick', changeZoomLvl);

	// X-axis label:
	// text label for the x axis
	 theChart_svg.append("text")
		.attr("transform",
			   "translate(" + (overwidthX/2) + " ," +
							  (overwidthY - margin.top + 5) + ")")
		.style("text-anchor", "middle")
		.text(getZoomByDisplayText(zoomLvl))
		.attr("class", "xAxisText")
		.attr("id", zoomLvl);
		/* .on('dblclick', function(){
			changeZoomLvl(respData);
	}); */
	theChart_svg.append("text")
		.attr('x', maxPlotHeight/2 * -1)
		.attr('dy', '.75em')
		.attr('transform', "rotate(-90)")						
		.style("text-anchor", "middle")
		.text('Isolate count')
		.attr("class", "xAxisText");



	let yAxis = g.append('g')
		.call(y_axis);
	yAxis.attr("transform", "translate(" + Number(barX_start) + ",0)");


	// $("#loading_timeStCount").hide();

	let colObj_ypos = 0;


	Object.keys(dict_colors).forEach(function(colObj, colObj_i){
		/* g.append('circle')
			.attr('cx', maxX + 50)
			.attr('cy', colObj_ypos)
			.attr("r", 5)
			.style("fill", dict_colors[colObj].color); */
		g.append('rect')
			.attr('x', maxX + 45 + barX_start)
			.attr('y', colObj_ypos - 5)
			.attr("width", 5)
			.attr('height', 5)
			.style("fill", dict_colors[colObj].color);


		g.append("text")
			.attr("x", maxX + 50 + barX_start)
			.attr("y", colObj_ypos)
			.text(colObj)
			.style("font-size", "10px")
			.attr("alignment-baseline","middle");

		colObj_ypos = colObj_ypos + 12;
	});


	d3.select("#downloadAsSvg")
	    .on("mouseover", writeDownloadLink("#downloadAsSvg", "#svg_timeStCount"));

}

function doThePlot_timeStCount_bg(data_forPlot, dict_colors, zoomLvl, respData, stackBy, highestTotal, topN){

	let maxPlotHeight = 650;

	if (data_forPlot.length == 0){
		document.getElementById("plot_timeStCount").innerHTML = "No data available.";
		return;
	}
	document.getElementById("plot_timeStCount").innerHTML = "";
	$('.tooltip').remove();
	// var svg = d3.create('svg')
	// .attr("viewBox", [0, 0, width, height]);
	// console.log(data_forPlot);
	// console.log(dict_colors);

	let margin = {top: 30, right: 20, bottom: 80, left: 20};
	let barX_incr = 25 + 10;


	var minX = 0;
	var maxX = data_forPlot.length * barX_incr;
	var overwidthX = maxX - minX + margin.left + margin.right;
	let maxY = 0;

	// get max in Y dir using total in dict
	data_forPlot.forEach(function(anObj, anObj_i){
		if (anObj.total > maxY){
			maxY = anObj.total;
		}
	});

	var overwidthY = maxPlotHeight + margin.top + margin.bottom;

	// Chart
	// let height = 500 - margin.top - margin.bottom;

	let theChart_svg = d3.select("#plot_timeStCount")
	//.style("overflow-x", "scroll")
	//.style("overflow-y", "scroll")
    .style("-webkit-overflow-scrolling", "touch")
	.append("svg")
	.style("display", "block")
	.attr('id', 'svg_timeStCount');


	theChart_svg.attr("width", overwidthX)
		.attr("height", overwidthY);

	var toolTip = d3.select("body").append("div")
    .attr("class", "tooltip")
	.style('background', 'beige')
	.style('border-radius', '8px')
	.style('padding', '2px')
	.style('border-color', '#cabfd9')
	.style('border-style', 'solid')
	.style('text-align', 'center');
    //.style("opacity", 0.2);
	let xAxisArr = [];

	let g = theChart_svg.append("g");

	let barX_start = 40;
	let barX = barX_start; // start position
 	let barX_width = 20 + 10;
	sortXAxisLabelData(zoomLvl, data_forPlot);
	// console.log("The zoom lvl is " + zoomLvl);

	if (topN > 0){
		dict_colors = restrictColorsByTopN(dict_colors, topN, data_forPlot, true);
	}

	for (let i = 0; i < data_forPlot.length; i++){ // xaxis sorting (i.e sorting on name. )
		let barY = maxPlotHeight;
		let sortedKeys = doTheStackBy_bg(stackBy, data_forPlot[i]);

		// Object.keys(data_forPlot[i]).sort().forEach(function(key){


		sortedKeys.forEach(function(key, key_i){


		// for (let key in data_forPlot[i]){
			// let barY = maxY;
			if (key == 'name'){
				xAxisArr.push(data_forPlot[i][key]);
			}
			if (key != 'name' && key != 'total'){
				let scaledHeight = (data_forPlot[i][key].proj/highestTotal) * maxPlotHeight;
				// console.log(data_forPlot[i][key]);
				barY = barY - (data_forPlot[i][key].total/highestTotal) * maxPlotHeight;

				let bar_proj = g.append('rect')
					.attr('width', barX_width)
					.attr('height', scaledHeight)
					.attr('x', barX)
					.attr('y', barY)
					.style('fill', function(){
						if (dict_colors.hasOwnProperty(key)){
							return (dict_colors[key]);
						}
						return ('white');
					})
					// .style('opacity', 1)
					.style('stroke', function(){
						if (dict_colors.hasOwnProperty(key)){
							return (dict_colors[key]);
						}
						return ('black');
					})
					.style('stroke-width', 1)
					.style('stroke-opacity', 0.75);

				let bar = g.append('rect')
					.attr('width', barX_width)
					.attr('height', (data_forPlot[i][key].total/highestTotal) * maxPlotHeight)
					.attr('x', barX)
					.attr('y', barY)
					.style('fill', function(){
							if (dict_colors.hasOwnProperty(key)){
								return (dict_colors[key]);
							}

							return ('white');
						}
					)
					.style('fill-opacity', 0.2)
					.style('stroke', function(){
						if (dict_colors.hasOwnProperty(key)){
							return (dict_colors[key]);
						}
						return ('white');
					})
					.style('stroke-width', 1)
					.style('stroke-opacity', 0.75);

				bar.data([data_forPlot[i]])
					.on("mouseover", function(d){
						d3.select(this)
							// .classed('active', true);
							// .style('opacity', 1)
							.style('stroke-width', 5);


						toolTip.transition()
							///.duration(200)
							.style("opacity", 1);
							toolTip.html("<b>" + key + "</b> <br> Proj count: "+ data_forPlot[i][key].proj + " Database count: " + data_forPlot[i][key].bg)
								.style("left", event.pageX + "px")
								.style("top", event.pageY + "px");
					})
					.on("mouseout", function(d) {
						// d3.select(this)
						// 	.classed('active', false);
						d3.select(this)
							// .classed('active', true);
							// .style('opacity', 1)
							.style('stroke-width', 1);

						toolTip.transition()
						// .duration(500)
						.style("opacity", 0);
					});


				// barY = barY - data_forPlot[i][key];
			}
		});
		barX = barX + barX_incr;
	}
	// console.log(xAxisArr);
	// X-axis
	// Create scale
	let x_scale = d3.scaleBand()
		.domain(xAxisArr)
		.range([0, maxX]);

	let y_scale = d3.scaleLinear()
		.domain([0, maxY])
		.range([maxPlotHeight, 0]);
		// .ticks().concat([0, maxY+1]);
		// .nice();



   // Add scales to axis
	let x_axis = d3.axisBottom()
	//	.attr("transform", "translate(0,50)")
		.scale(x_scale);

	let y_axis = d3.axisLeft()
	//	.attr("transform", "translate(0,50)")
		.scale(y_scale);

	if (maxY < 100){
		y_axis.tickValues(d3.range(0, maxY, maxY/10));
	}

	let xAxis = g.append('g')
		.call(x_axis);

	xAxis.attr("transform", "translate(" + barX_start + ", " + maxPlotHeight + ")")
		.selectAll("text")
		.style("text-anchor", "end")
		.attr("dx", "-.8em")
		.attr("dy", "-.5em")
		.attr("transform", "rotate(-60)");
	// xAxis.on('dblclick', changeZoomLvl);

	// X-axis label:
	// text label for the x axis
	 theChart_svg.append("text")
		.attr("transform",
			   "translate(" + (overwidthX/2) + " ," +
							  (overwidthY - margin.top + 5) + ")")
		.style("text-anchor", "middle")
		.text(getZoomByDisplayText(zoomLvl))
		.attr("class", "xAxisText")
		.attr("id", zoomLvl);
		/* .on('dblclick', function(){
			changeZoomLvl(respData);
		}); */


	let yAxis = g.append('g')
		.call(y_axis);
	yAxis.attr("transform", "translate(" + Number(barX_start) + ",0)");


	$("#loading_timeStCount").hide();

	let colObj_ypos = 0;
	Object.keys(dict_colors).forEach(function(colObj, colObj_i){
		/* g.append('circle')
			.attr('cx', maxX + 50)
			.attr('cy', colObj_ypos)
			.attr("r", 5)
			.style("fill", dict_colors[colObj].color); */

		g.append('rect')
			.attr('x', maxX + 45)
			.attr('y', colObj_ypos - 5)
			.attr("width", 5)
			.attr('height', 5)
			.style("fill", dict_colors[colObj]);


		g.append("text")
			.attr("x", maxX + 50)
			.attr("y", colObj_ypos)
			.text(colObj)
			.style("font-size", "10px")
			.attr("alignment-baseline","middle");

		colObj_ypos = colObj_ypos + 12;
	});


	d3.select("#downloadAsSvg")
	    .on("mouseover", writeDownloadLink("#downloadAsSvg", "#svg_timeStCount"));

}


function writeDownloadLink(downloadBtnId, svgId){
	var html = d3.select(svgId)
		.attr("title", "svg_title")
		.attr("version", 1.1)
		.attr("xmlns", "http://www.w3.org/2000/svg")
		.node().parentNode.innerHTML;


	d3.select(downloadBtnId)
		.attr("href-lang", "image/svg+xml")
		.attr("href", "data:image/svg+xml;base64,\n" + btoa(html))
		.attr('download', 'graph.svg');



};

function sortXAxisLabelData(zoomLvl, dataForPlot){
	if (zoomLvl == 'year'){ // numeric sort
		dataForPlot.sort(function(a, b){
			return a.name - b.name;
		});
	}
	else if (zoomLvl == 'month'){
		dataForPlot.sort(function(a, b){
			let c = a.name.split('-');
			let d = b.name.split('-');

			if (c[0] != d[0]){
				return c[0] -  d[0];
			}
			else {
				return c[1] - d[1];
			}
			// return b.name - a.name;
		});
	}
	else if (zoomLvl == 'date'){
		dataForPlot.sort(function(a, b){
			let c = a.name.split("-");
			let d = b.name.split("-");

			if (c[0] != d[0]){
				return c[0] - d[0];
			}
			else {
				// check month
				if (c[1] != d[1]){
					return c[1] - d[1];
				}
				else{
					// check date
					return c[2] - d[2];

				}

			}
		});
	}
	else if (zoomLvl == 'continent'){
		dataForPlot.sort(function(a, b){
		// 	console.log(b.total + " " + a.total);
			return (b.total - a.total);
			/* if (a.name > b.name){ // alphabetically
				return 1;
			}
			else {
				return -1;
			} */
		});
	}
	else if (zoomLvl == 'country'){
		dataForPlot.sort(function(a, b){
			// console.log(b.total + " " + a.total);
			return (b.total - a.total);
			/* if (a.name > b.name){ // alphabetically
				return 1;
			}
			else {
				return -1;
			} */
		});
	}
	else if (zoomLvl == 'state'){
		dataForPlot.sort(function(a, b){
			let c = a.name.split('-');
			let d = b.name.split('-');

			// console.log(c + " ... " + d);
			if (c[0] != d[0]){
				return d[0] > c[0] ? 1 : -1 ;
			}
			else {
				// return c[1] > d[1] ? 1 : -1 ;
				return (b.total - a.total);
			}
		});
	}
	else if (zoomLvl == 'postcode'){
		dataForPlot.sort(function(a, b){
			let c = a.name.split('-');
			let d = b.name.split('-');

			// console.log(c + " ... " + c);
			if (c[0] != d[0]){
				return d[0] > c[0] ? 1 : -1 ;
			}
			else if (c[1] != d[1]){
				return c[1] > d[1] ? 1 : -1 ;
			}
			else{
				return c[2] > d[2] ? 1 : -1 ;
			}
		});

	}
	// return dataForPlot;
}

function convertToSingletons(dataForPlot, dict_colors){
	if (parseInt(document.getElementById('graph_timeStCount_shownNum').innerHTML) < limitForSingletons){
		return dataForPlot; 
	}

	console.log('In convertToSingletons');
	console.log(dataForPlot); 

	let tenPercentCeil = 1; // Math.ceil(parseInt(document.getElementById('graph_timeStCount_shownNum').innerHTML) * 0.01);

	// console.log("The 10% count is " + tenPercentCeil);
	let dataForPlot_singletons = []; 
	let totalSingletons = 0; 
	dataForPlot.forEach(function(obj, obj_i){
		let newObj = {}; 
		for (let key in obj){
			if (key == 'name' || key == 'total' || obj[key] > tenPercentCeil){
				newObj[key] = obj[key];  
			}
			else {
				if (!newObj.hasOwnProperty(Singletons)){
					newObj[Singletons] = 0; 
				}

				
				newObj[Singletons] = newObj[Singletons] + parseInt(obj[key]); 
				console.log('=== ' + key + ' ' + obj[key] + ' ' + newObj[Singletons]); 
			}

		}

		totalSingletons = totalSingletons + newObj[Singletons];
		console.log('= ' + totalSingletons);
		dataForPlot_singletons.push(newObj); 
	}); 

	dict_colors[Singletons] = {color: "rgb(245,245,245)", total: totalSingletons}; 

	// console.log('dict_colors ' + dict_colors[Singletons].total);
	/* 
	console.log("The data for plot before singletons is "); 
	console.log(dataForPlot); 
	console.log('dataForPlot_singletons'); 
	console.log(dataForPlot_singletons); 
	*/ 
	return (dataForPlot_singletons); 
}

function getTheStackByChoice(){

	if (document.getElementById(StackBy_isoCount).classList.contains('btn-default-spe')){
		return StackBy_isoCount;
	}
	else{
		return StackBy_StNum;
	}
}

function changeZoomLvl(respData, zoomBy, bgData, topN){
	// alert("Hello world! - change zoom lvl");

	let lvlChoices = readThe3LvlChoices();
	// let currentLvlChoice = document.getElementsByClassName('xAxisText')[0].id;
	// console.log(currentLvlChoice);
	let stackByChoice = getTheStackByChoice();
	transformTheDataForPlot(respData, lvlChoices.lvl1, lvlChoices.lvl2, lvlChoices.lvl3, zoomBy, stackByChoice, bgData, topN);

	checkAndTurnOffBgBtn(bgData);
}

function convertToSortFmt(data_forPlot, isBg){
	/**
	 *  This function excludes keys Singleton, name & total (so only CC and ODC) keys should be present in dict_. 
	 */
	let dict_sortFmt = {}; // dict_{STVal|Other|Singleton} => cnt
	
	data_forPlot.forEach(function(dataObj, dataObj_i){
		for (let key in dataObj){
			if (key != Singletons && key != 'name' && key != 'total' && key != 'Other'){
				if (isBg == false) {
					if (!dict_sortFmt.hasOwnProperty(key)){
						dict_sortFmt[key] = 0; 
					}
					dict_sortFmt[key] = dict_sortFmt[key] + dataObj[key];
				}
				else if (isBg == true && dataObj[key].hasOwnProperty('proj')) {
					if (!dict_sortFmt.hasOwnProperty(key)){
						dict_sortFmt[key] = 0; 
					}
					dict_sortFmt[key] = dict_sortFmt[key] + dataObj[key]['proj'];
				}
					
				
			}
			// console.log ("Key is " + key); 
		}
	})

	return dict_sortFmt; 
}

function restrictColorsByTopN(dict_colors, topN, data_forPlot, isBg){
	// console.log("Over here!");
	if (topN > 0){
		let dict_colorsTopN = {};

		let dict_sortFmt = convertToSortFmt(data_forPlot, isBg);

		let sortedKeys = Object.keys(dict_sortFmt).sort(function(a, b){
			return dict_sortFmt[b] - dict_sortFmt[a];
		});

		let counter = 0;

		while (counter < topN){
			dict_colorsTopN[sortedKeys[counter]] = dict_colors[sortedKeys[counter]];
			counter = counter + 1;
		}
		
		return dict_colorsTopN;
	}


}


function addTotalToObjs(data_forPlot, dict_colors){

	let highestTotal = 0;

	data_forPlot.forEach(function(item, i){
		let total = 0;
		for (let [key, val] of Object.entries(item)){
			if (key != 'name'){
				total = total + val;

				if (dict_colors.hasOwnProperty(key) && key != Singletons){
					dict_colors[key].total = dict_colors[key].total + val;
				}
			}


		}
		item['total'] = total;
		if (total > highestTotal){
			highestTotal = total;
		}
	});

	return (highestTotal)
	// console.log(data_forPlot);
}

function addTotalToObjs_bg(data_forPlot){

	let highestTotal = 0;

	data_forPlot.forEach(function(item, i){
		let total = 0;
		for (let [key, val] of Object.entries(item)){
			if (key != 'name'){
				total = total + val.proj + val.bg;
				item[key].total = val.proj + val.bg;
			}
		}
		item['total'] = total;
		if (total > highestTotal){
			highestTotal = total;
		}
	});

	return (highestTotal);

}

function getTheColsToAggrBy(zoomLvl){
	let aggByCols = [zoomLvl];

	if (zoomLvl == 'month'){
		aggByCols.push('year');
	}
	else if (zoomLvl == 'state'){
		aggByCols.push('country');
	}
	else if (zoomLvl == 'postcode'){
		aggByCols.push('state');
		aggByCols.push('country');
	}

	// console.log("did larry call dibs");
	// console.log(aggByCols);
	return (aggByCols);
}


function doTheTransformation_bg(respData, colNums, aggByCols, bgData){
	// console.log("doTheTransformation_bg");
	// console.log(bgData);


	let data_forPlot = []; // dict_{stCcOdc, year} = count
	let dict_colors = {}; // dict_{stCcOdc} = theColor

	let total = 0;
	let shown = 0;

	respData.forEach(function(item, i){
		if (i != 0){
			total = total + item[colNums['count']];
			if (item[colNums['stCcOdc']] != null){
			//} && item[colNums[aggByCol]] != null) {
				let isAnyNull = false;
				let nameInObjVal = '';
				aggByCols.forEach(function(aggByCol, aggByCol_i){
					if (item[colNums[aggByCol]] == null){
						isAnyNull = true;
					}
					if (nameInObjVal == ''){
						nameInObjVal = item[colNums[aggByCol]];
					}
					else {
						nameInObjVal = item[colNums[aggByCol]] + '-' + nameInObjVal;
					}

				});

				// console.log(nameInObjVal);

				if (isAnyNull == false){
					// let theVal =
					shown = shown + item[colNums['count']];
					let anObj = data_forPlot.find(el => el.name == nameInObjVal);

					let theStCcOdcKey = colNums['stCcOdc_type'] + String(item[colNums['stCcOdc']]);
					// console.log(theStCcOdcKey);
					if (anObj && anObj.hasOwnProperty(theStCcOdcKey)){
						anObj[theStCcOdcKey]['proj'] = Number(anObj[theStCcOdcKey]['proj']) + Number(item[colNums['count']]);

					}
					else if (anObj){
						anObj[theStCcOdcKey] = {bg: 0};
						anObj[theStCcOdcKey]['proj'] = item[colNums['count']]; // assuming by reference;
					}
					else{
						let objToAdd = {'name': nameInObjVal};
						objToAdd[theStCcOdcKey] = {bg: 0};
						objToAdd[theStCcOdcKey]['proj'] = Number(item[colNums['count']]);

						data_forPlot.push(objToAdd);
					}

					if (!dict_colors.hasOwnProperty(theStCcOdcKey)){
						dict_colors[theStCcOdcKey] = getRandomColor(item[colNums['stCcOdc']], 0, 0.75).replace("rgba", "rgb").replace("\,0.75\)", "\)");
						// console.log(dict_colors[theStCcOdcKey]);

					}
				}

			}

		}

	});


	// console.log(dict_colors
	// console.log("Agg by cols");
	// console.log(aggByCols);

	document.getElementById('graph_timeStCount_totalNum').innerHTML = total;
	document.getElementById('graph_timeStCount_shownNum').innerHTML = shown;

	// Only show bg for the available md?
	// console.log(data_forPlot);

	if (data_forPlot.length > 0){
		// attach data from the background.
		bgData.forEach(function(item, item_i){
			if (item[colNums['stCcOdc']] != null){
				let isAnyNull = false;
				let nameInObjVal = '';
				aggByCols.forEach(function(aggByCol, aggByCol_i){
					if (item[colNums[aggByCol]] == null){
						isAnyNull = true;
					}

					if (nameInObjVal == ''){
						nameInObjVal = item[colNums[aggByCol]];
						// console.log(nameInObjVal);
					}
					else {
						nameInObjVal = item[colNums[aggByCol]] + '-' + nameInObjVal;
						// console.log(nameInObjVal);
					}

					/* else{
						// Get name of column e.g In location, australia;
						if (nameInObjVal == ''){
							nameInObjVal = item[colNums[aggByCol]];
							console.log(nameInObjVal);
						}
						else {
							nameInObjVal = item[colNums[aggByCol]] + '-' + nameInObjVal;
							console.log(nameInObjVal);
						}

					} */

				});


				if (isAnyNull == false){
					let anObj = data_forPlot.find(el => el.name == nameInObjVal);

					if (anObj !== undefined){
						// console.log("Found an Obj");
						// console.log(anObj);

						let theStCcOdcKey = colNums['stCcOdc_type'] + String(item[colNums['stCcOdc']]);

						// console.log(theStCcOdcKey);

						if (anObj && anObj.hasOwnProperty(theStCcOdcKey)){
							anObj[theStCcOdcKey]['bg'] = Number(anObj[theStCcOdcKey]['bg']) + Number(item[colNums['count']]);

						}
						else if (anObj){
							if (anObj.hasOwnProperty('Other')){
								anObj['Other']['bg'] = anObj['Other']['bg'] + item[colNums['count']]; // assuming by reference;
							}
							else{
								anObj['Other'] = {proj: 0};
								anObj['Other']['bg'] = item[colNums['count']]; // assuming by reference;
							}
						}
						/* To not add any new element; else{
							let objToAdd = {'name': nameInObjVal};
							objToAdd[theStCcOdcKey] = Number(item[colNums['count']]);

							data_forPlot.push(objToAdd);
						} */

						if (!dict_colors.hasOwnProperty(theStCcOdcKey)){
							dict_colors[theStCcOdcKey] = "rgb(128, 128, 128)"; // grayish.
							// console.log(dict_colors[theStCcOdcKey]);

						}
					}

				}
			}
		});

	}

	// console.log("The new data for plot");
	// console.log(data_forPlot);

	return ({data_forPlot: data_forPlot, dict_colors: dict_colors});
}


function doTheTransformation(respData, colNums, aggByCols){

	let data_forPlot = []; // dict_{stCcOdc, year} = count
	let dict_colors = {}; // dict_{stCcOdc} = {color: theColor, count: theCount};

	let total = 0;
	let shown = 0;

	respData.forEach(function(item, i){
		if (i != 0){
			total = total + item[colNums['count']];
			if (item[colNums['stCcOdc']] != null){
			//} && item[colNums[aggByCol]] != null) {
				let isAnyNull = false;
				let nameInObjVal = '';
				aggByCols.forEach(function(aggByCol, aggByCol_i){
					if (item[colNums[aggByCol]] == null){
						isAnyNull = true;
					}
					if (nameInObjVal == ''){
						nameInObjVal = item[colNums[aggByCol]];
					}
					else {
						nameInObjVal = item[colNums[aggByCol]] + '-' + nameInObjVal;
					}

				});

				// console.log(nameInObjVal);

				if (isAnyNull == false){
					// let theVal =
					shown = shown + item[colNums['count']];
					let anObj = data_forPlot.find(el => el.name == nameInObjVal);

					let theStCcOdcKey = colNums['stCcOdc_type'] + String(item[colNums['stCcOdc']]);
					// console.log(theStCcOdcKey);
					if (anObj && anObj.hasOwnProperty(theStCcOdcKey)){
						anObj[theStCcOdcKey] = Number(anObj[theStCcOdcKey]) + Number(item[colNums['count']]);


					}
					else if (anObj){
						anObj[theStCcOdcKey] =  item[colNums['count']]; // assuming by reference;
					}
					else{
						let objToAdd = {'name': nameInObjVal};
						objToAdd[theStCcOdcKey] = Number(item[colNums['count']]);

						data_forPlot.push(objToAdd);
					}

					if (!dict_colors.hasOwnProperty(theStCcOdcKey)){
						dict_colors[theStCcOdcKey] = {
							color: getRandomColor(item[colNums['stCcOdc']], 0, 0.75).replace("rgba", "rgb").replace("\,0.75\)", "\)"),
							total: 0
						};
						// console.log(dict_colors[theStCcOdcKey]);

					}
				}

			}

		}

	});


	// dict_color[Singletons] = '#F5F5F5'; 
	document.getElementById('graph_timeStCount_totalNum').innerHTML = total;
	document.getElementById('graph_timeStCount_shownNum').innerHTML = shown;
	return ({data_forPlot: data_forPlot, dict_colors: dict_colors});
}

function getColsToBuildDict(headerArr, lvl3_choice, lvl3BtnPtn){
	// console.log("The header arr is ");
	// console.log(headerArr);
	let colNums = {
		year: -1,
		month: -1,
		date: -1,
		continent: -1,
		country: -1,
		state: -1,
		postcode: -1,
		count: -1,
		stCcOdc: -1,
		stCcOdc_type: '',
	};

	// let theRegex = new RegExp(lvl3BtnPtn);
	let tn_stCcOdc = lvl3_choice.replace(lvl3BtnPtn, '');
	// console.log("Over here: " + tn_stCcOdc);

	// cc, odc
	if (tn_stCcOdc.match(/\_[0-9]+\_[0-9]+$/)){
		if (tn_stCcOdc.match(/\_1$/)){
			colNums.stCcOdc_type = 'CC';
		}
		else{
			colNums.stCcOdc_type = 'ODC';
		}
		tn_stCcOdc = tn_stCcOdc.replace(/\_[0-9]+$/, '');
	}
	else{ // st
		tn_stCcOdc = tn_stCcOdc + "_st";
		colNums.stCcOdc_type = 'ST';
	}

	headerArr.forEach(function(item, i){
		if (item == 'count'){
			colNums.count = i;
		}

		if (item == tn_stCcOdc){
			colNums.stCcOdc = i;
		}

		if (item == 'year'){
			colNums.year = i;
		}

		if (item == 'month'){
			colNums.month = i;
		}

		if (item == 'date'){
			colNums.date = i;
		}

		if (item == 'continent'){
			colNums.continent = i;
		}

		if (item == 'country'){
			colNums.country = i;
		}

		if (item == 'state'){
			colNums.state = i;
		}

		if (item == 'postcode'){
			colNums.postcode = i;
		}

	});

	// console.log("ColNums: ");
	// console.log(colNums);
	return (colNums);
}


function switchClassesForMultipleBtns(list_ids){
	list_ids.forEach(function(btnId, btnId_i){
		removeClassFromBtn(btnId, "btn-default-spe");
		addClassToBtn(btnId, "btn-default-outline-spe");
	});
}


function checkAndSendToPlotLvl3(lvl3_divToShow){
	let theBtns = document.getElementById(lvl3_divToShow).querySelectorAll("button");
	let isBtnSel = false;
	theBtns.forEach(function(aBtn, aBtn_i){
		if (aBtn.classList.contains('btn-default-spe')){
			isBtnSel = true;
			aBtn.click();
		}
	});



	if (isBtnSel == false){
		theBtns[0].click();
	}
	// document.getElementById('id').click();
}



function isBtnSelected(btnId, classId){
	if (document.getElementById(btnId).classList.contains(classId)){
		return (true);
	}
	else{
		return (false);
	}
}



function downloadSvg(svgId){
	let svgEl = document.getElementById(svgId);
	let name = 'timeStCount.svg';
	// let svgEl = document.getElement();
	svgEl.setAttribute("xmlns", "http://www.w3.org/2000/svg");
	var svgData = svgEl.outerHTML;
	var preface = '<?xml version="1.0" standalone="no"?>\r\n';
	var svgBlob = new Blob([preface, svgData], {type:"image/svg+xml;charset=utf-32"});
	var svgUrl = URL.createObjectURL(svgBlob);
	var downloadLink = document.createElement("a");
	downloadLink.href = svgUrl;
	downloadLink.download = name;
	document.body.appendChild(downloadLink);
	downloadLink.click();
	document.body.removeChild(downloadLink);
}
