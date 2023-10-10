export {get_timeLocStCnt, g2_plotLvl1_stCcOdc};
import {drawButtons_init, ZoomBy, switchClassesForMultipleBtns, checkAndSendToPlotLvl3, getColsToBuildDict, getTheColsToAggrBy, getZoomByDisplayText, writeDownloadLink} from './graph_timeOrLocStCount.js';
import {ajaxCall} from './packageAndSend.js';

const G2_lvl2_btnsDivSt = "g2_timeStCnt_btnDiv_ap";
const G2_lvl2_btnsDivCc = "g2_timeStCnt_btnDiv_cc";
const G2_lvl2_btnsDivOdc = "g2_timeStCnt_btnDiv_odc";
const G2_lvl1_btnSt = "g2_timeLocStCnt_btn_st";
const G2_lvl1_btnCc = "g2_timeLocStCnt_btn_cc";
const G2_lvl1_btnOdc = "g2_timeLocStCnt_btn_odc";
const G2_lvl2_btn_pattern = "g2_timeLocStCnt_btn_";
const G2_colByBtns = ['g2_colBy_shannon', 'g2_colBy_stCnt', 'g2_colBy_isoCnt'];

function get_timeLocStCnt(tabAps, tabCcsOdcs, org){

	$("#loading_timeLocStCnt").show();

	drawButtons_init(tabAps, tabCcsOdcs, G2_lvl2_btnsDivSt, G2_lvl2_btnsDivCc, G2_lvl2_btnsDivOdc, G2_lvl2_btn_pattern);

	ajaxCall('/' + org + '/timeStCount', {}, handle_timeLocStCnt);

	document.getElementById('btn_timeLocStCnt').remove();
	// console.log("here?");
}



function handle_timeLocStCnt(respData){
	let parsedRespData = JSON.parse(respData);

	let response = [];
	if (parsedRespData.hasOwnProperty('data')){
		response = parsedRespData.data;

		console.log(response);
	}

	// attachEventsToButtons_init
	g2_attachEventsToBtns_init(response, G2_lvl2_btnsDivSt);
	g2_attachEventsToBtns_init(response, G2_lvl2_btnsDivCc);
	g2_attachEventsToBtns_init(response, G2_lvl2_btnsDivOdc);

	// g2_transformDataForPlot(response);

	$("#loading_timeLocStCnt").hide();
	$("#g2_btnsAndPlot").show();


	g2_attachEventsToTimeBtns_init(response, 'time');
	g2_attachEventsToTimeBtns_init(response, 'location');

	g2_attachEventsToColBy_init(response);

	g2_plotLvl1_stCcOdc(G2_lvl1_btnSt);
}
/////////////////////////////

function g2_attachEventsToBtns_init(respData, divIdBtn_apCcOdc){

	let apCcOdcBtns = document.getElementById(divIdBtn_apCcOdc).querySelectorAll("button");
	apCcOdcBtns.forEach(function(aBtn, aBtn_i){
		aBtn.onclick = function(){
			// console.log("Plot lvl 3");
			// plotLvl3(aBtn.id, divIdBtn_apCcOdc, respData, bgData, topN);

			g2_plotLvl2_mgt(aBtn.id, divIdBtn_apCcOdc, respData);
		};
	});

}


function g2_attachEventsToTimeBtns_init(respData, timeLoc){
	Object.keys(ZoomBy[timeLoc]).forEach(function(item, item_i){
		document.getElementById('g2_zoomBy_' + item).onclick = function(){
			g2_changeZoomLvl(respData, timeLoc, item);
			g2_zoomBy_switchBtns(item, timeLoc, 'g2_zoomBy_');
		};
	});
}


function g2_attachEventsToColBy_init(respData){
	let colByBtns = document.getElementById('g2_colBy').querySelectorAll('button');

	console.log(colByBtns);
	colByBtns.forEach(function(item, i){
		item.onclick = function(){
			g2_changeColBy(respData, item.id);
			g2_colBy_switchBtns(item.id);
		};
	});

}

function g2_colBy_switchBtns(clickedBtn){
	G2_colByBtns.forEach(function(aBtnId, i){
		if (aBtnId == clickedBtn){
			removeClassFromBtn(aBtnId, "btn-default-outline-spe");
			addClassToBtn(aBtnId, "btn-default-spe");
		}
		else{
			removeClassFromBtn(aBtnId, "btn-default-spe");
			addClassToBtn(aBtnId, "btn-default-outline-spe");
		}
	});
}


function g2_changeColBy(respData, clickedColBy){
	let lvlChoices = g2_readThe2LvlChoices();
	let zoomByChoice_time = g2_readTheZoomByChoice('time');
	let zoomByChoice_loc = g2_readTheZoomByChoice('location');

	g2_transformDataForPlot(respData, lvlChoices.lvl1, lvlChoices.lvl2, zoomByChoice_time, zoomByChoice_loc, clickedColBy);
}


function g2_changeZoomLvl(respData, timeLoc, zoomByClicked){
	let lvlChoices = g2_readThe2LvlChoices();
	let zoomByChoice_time = '';
	let zoomByChoice_loc = '';
	let colByChoice = g2_readTheColByChoice();

	if (timeLoc == 'time'){ // read the other zoom by choice;
		zoomByChoice_time = zoomByClicked;
		zoomByChoice_loc = g2_readTheZoomByChoice('location');

	}
	else{
		zoomByChoice_time = g2_readTheZoomByChoice('time');
		zoomByChoice_loc = zoomByClicked;
	}



	// console.log("Let the zoom by other choice " + zoomByChoiceOther);

	g2_transformDataForPlot(respData, lvlChoices.lvl1, lvlChoices.lvl2, zoomByChoice_time, zoomByChoice_loc, colByChoice);
}

function g2_readTheColByChoice(){
	let colByChoice = '';
	G2_colByBtns.forEach(function(aBtnId, i){
		if (document.getElementById(aBtnId).classList.contains('btn-default-spe')){
			colByChoice = aBtnId;
		}
	});
	return colByChoice;
}

function g2_readTheZoomByChoice(timeLoc){
	let zoomByChoice = '';
	Object.keys(ZoomBy[timeLoc]).forEach(function(item, i){
		if (document.getElementById("g2_zoomBy_" + item).classList.contains('btn-default-spe')) {
			zoomByChoice = item;
		}
	});

	return (zoomByChoice);
}


function g2_zoomBy_switchBtns(clickedBtn, timeLoc, zoomBy_btnPtn){
	Object.keys(ZoomBy[timeLoc]).forEach(function(item, item_i){
		if (item == clickedBtn){
			removeClassFromBtn(zoomBy_btnPtn + item, "btn-default-outline-spe");
			addClassToBtn(zoomBy_btnPtn + item, "btn-default-spe");
		}
		else {
			removeClassFromBtn(zoomBy_btnPtn + item, "btn-default-spe");
			addClassToBtn(zoomBy_btnPtn + item, "btn-default-outline-spe");
		}
	});
}

function g2_plotLvl1_stCcOdc(inputClickedBtn){
	let clickedBtn = inputClickedBtn;
	let otherBtns = [];

	let divToShow = '';
	let divsToHide = [];

	if (typeof inputClickedBtn == "undefined" || inputClickedBtn == undefined || inputClickedBtn == null || inputClickedBtn == ''){
		// console.log("what else did he say to you");
		// check if any already selected ...
		if (isBtnSelected(G2_lvl1_btnSt, 'btn-default-spe') == true){
			// document.getElementById("stackBy_StNum").innerHTML = 'ST identifier';
			clickedBtn = G2_lvl1_btnSt;
			otherBtns.push(G2_lvl1_btnCc); otherBtns.push(G2_lvl1_btnOdc);
			divToShow = G2_lvl2_btnsDivSt;
			divsToHide.push(G2_lvl2_btnsDivCc); divsToHide.push(G2_lvl2_btnsDivOdc);
		}
		else if (isBtnSelected(G2_lvl1_btnCc, 'btn-default-spe') == true){
			// document.getElementById("stackBy_StNum").innerHTML = 'CC identifier';
			clickedBtn = G2_lvl1_btnCc;
			otherBtns.push(G2_lvl1_btnSt); otherBtns.push(G2_lvl1_btnOdc);
			divToShow = G2_lvl2_btnsDivCc;
			divsToHide.push(G2_lvl2_btnsDivSt); divsToHide.push(G2_lvl2_btnsDivOdc);
		}
		else if (isBtnSelected(G2_lvl1_btnOdc, 'btn-default-spe') == true){
			// document.getElementById("stackBy_StNum").innerHTML = 'ODC identifier';
			clickedBtn = G2_lvl1_btnOdc;
			otherBtns.push(G2_lvl1_btnSt); otherBtns.push(G2_lvl1_btnCc);
			divToShow = G2_lvl2_btnsDivOdc;
			divsToHide.push(G2_lvl2_btnsDivSt); divsToHide.push(G2_lvl2_btnsDivCc);
		}
		else { // else: if no button is selected
			// document.getElementById("stackBy_StNum").innerHTML = 'ST identifier';
			clickedBtn = G2_lvl1_btnSt;
			otherBtns.push(G2_lvl1_btnCc); otherBtns.push(G2_lvl1_btnOdc);
			divToShow = G2_lvl2_btnsDivSt;
			divsToHide.push(G2_lvl2_btnsDivCc); divsToHide.push(G2_lvl2_btnsDivOdc);
		}
	}
	else{

		if (clickedBtn == G2_lvl1_btnSt){
			// clickedBtn = lvl2_st;
			// document.getElementById("stackBy_StNum").innerHTML = 'ST identifier';
			otherBtns.push(G2_lvl1_btnCc); otherBtns.push(G2_lvl1_btnOdc);
			divToShow = G2_lvl2_btnsDivSt;
			divsToHide.push(G2_lvl2_btnsDivCc); divsToHide.push(G2_lvl2_btnsDivOdc);
		}
		else if (clickedBtn == G2_lvl1_btnCc){
			// clickedBtn = lvl2_cc;
			// document.getElementById("stackBy_StNum").innerHTML = 'CC identifier';
			otherBtns.push(G2_lvl1_btnSt); otherBtns.push(G2_lvl1_btnOdc);
			divToShow = G2_lvl2_btnsDivCc;
			divsToHide.push(G2_lvl2_btnsDivSt); divsToHide.push(G2_lvl2_btnsDivOdc);
		}
		else {
			// clickedBtn = lvl2_odc;
			// document.getElementById("stackBy_StNum").innerHTML = 'ODC identifier';
			otherBtns.push(G2_lvl1_btnSt); otherBtns.push(G2_lvl1_btnCc);
			divToShow = G2_lvl2_btnsDivOdc;
			divsToHide.push(G2_lvl2_btnsDivSt); divsToHide.push(G2_lvl2_btnsDivCc);
		}
	}

	// console.log("how about over here...?");
	console.log("The clicked btn is ");
	console.log(clickedBtn);

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


	// handle level 3 here.
	// if something is already selected pass that on.
	// else manually click mgt2st || mgt2cc || odc1
	// checkAndSendToPlotLvl3(divToShow);

	checkAndSendToPlotLvl3(divToShow);
}


function g2_plotLvl2_mgt(inputClickedBtnId, divIdBtn, respData){
	let theBtns = document.getElementById(divIdBtn).querySelectorAll("button");

	theBtns.forEach(function(aBtn, aBtn_i){
		// console.log(aBtn.id);
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


	let lvlChoices = g2_readThe2LvlChoices();
	g2_transformDataForPlot(respData, lvlChoices.lvl1, lvlChoices.lvl2, null, null, null);
}
///////////////////////////// Transform and plot

function g2_transformDataForPlot(respData, lvl1_choice, lvl2_choice, zoomLvl_time, zoomLvl_loc, colBy_choice){

	console.log(lvl1_choice + " " + lvl2_choice + " " + colBy_choice);

	let colNums = getColsToBuildDict(respData[0], lvl2_choice, G2_lvl2_btn_pattern);

	// Get choices;
	if (zoomLvl_time == null){
		zoomLvl_time = 'year';
		g2_zoomBy_switchBtns('year', 'time', 'g2_zoomBy_');
	}
	if (zoomLvl_loc == null){
		zoomLvl_loc = 'country';
		g2_zoomBy_switchBtns('country', 'location', 'g2_zoomBy_');
	}
	if (colBy_choice == null){
		colBy_choice = G2_colByBtns[0];
		g2_colBy_switchBtns(G2_colByBtns[0]);
	}



	let aggByCols_time = getTheColsToAggrBy(zoomLvl_time);
	let aggByCols_loc = getTheColsToAggrBy(zoomLvl_loc);



	let dict_ = g2_doTheTransformation(respData, colNums, aggByCols_time, aggByCols_loc);


	g2_convertToMergedStFormat(dict_.data_forPlot);

	g2_doThePlot_timeAndLocStCnt(dict_.data_forPlot, colBy_choice);
}


function g2_getSortedXAxisKeys(dataForPlot){
	// Note: not sorted yet!
	let result = dataForPlot.map(a => a.x_name).filter((value, index, self) => self.indexOf(value) === index);

	return result;
}

function g2_doThePlot_timeAndLocStCnt(data_forPlot, colBy_choice){

	if (data_forPlot.length == 0){
		console.log("Data for plotting is empty, nothing to show!");
		document.getElementById("g2_plot_timeLocStCnt").innerHTML = "No data to show!";
		return;
	}

	document.getElementById("g2_plot_timeLocStCnt").innerHTML = "";

	let keys_xAxisSorted = g2_getSortedXAxisKeys(data_forPlot); // time

	g2_sortDataByLocation(data_forPlot);

	// console.log("The data for plot is, now: ");
	// console.log(data_forPlot);

	let maxShannonVal = getMaxShannon(data_forPlot, 'shannon');
	let minShannonVal = getMinShannon(data_forPlot, 'shannon', maxShannonVal);

	let maxValForNorm = -1;
	let minValForNorm = -1;
	if (colBy_choice == G2_colByBtns[1]){
		maxValForNorm = getMaxShannon(data_forPlot, 'stDist');
		minValForNorm = getMinShannon(data_forPlot, 'stDist', maxValForNorm);
	}
	else if (colBy_choice == G2_colByBtns[2]){
		maxValForNorm = getMaxShannon(data_forPlot, 'isoCount');
		minValForNorm = getMinShannon(data_forPlot, 'isoCount', maxValForNorm);
	}
	// console.log(maxShannonVal);

	let theChart_svg = d3.select("#g2_plot_timeLocStCnt")
		.style("-webkit-overflow-scrolling", "touch")
		.append("svg")
		.style("display", "block")
		.attr('id', 'svg_g2_');

	let toolTip = d3.select("#g2_btnsAndPlot")
	    .append("div")
	    .style("opacity", 0)
		.attr('id', 'g2_tooltip')
	    .attr("class", "tooltip")
	    .style("background-color", "beige")
		.style('border-radius', '8px')
		.style('padding', '2px')
	    .style("border", "solid")
		.style('border-color', '#cabfd9');

	let g = theChart_svg.append("g");


	let keys_yAxis = [];
	keys_yAxis.push(data_forPlot[0].y_name);
	let xIncr = 20; let yIncr = 20; let xOffset = 100;
	let yPos = 0; let xPos_max = 0;


	for (let i=0; i < data_forPlot.length; i++){
		// let xPos = // find the .x_name in (arr_pos * 10)


		if (keys_yAxis.indexOf(data_forPlot[i].y_name) == -1){
			yPos = yPos + yIncr;
			keys_yAxis.push(data_forPlot[i].y_name);
		}


		let equitability = 0;
		if (maxShannonVal > 0 || maxShannonVal < 0){ // i.e. not equal to 0.
			equitability = data_forPlot[i].shannon/maxShannonVal
		};
		let colorOfRect = 'black';
		if (colBy_choice == G2_colByBtns[0]){
			colorOfRect = getColor_bet0And1(equitability);
		}
		else if (colBy_choice == G2_colByBtns[1]){
			colorOfRect = getColor_bet0And1(data_forPlot[i]['stDist']/maxValForNorm);
		}
		else if (colBy_choice == G2_colByBtns[2]){
			colorOfRect = getColor_bet0And1(data_forPlot[i]['isoCount']/maxValForNorm);
		}

		let xPos = keys_xAxisSorted.indexOf(data_forPlot[i].x_name) * xIncr + xOffset;

		if (xPos > xPos_max){
			xPos_max = xPos;
		}

		let rect = g.append('rect')
			.attr("width", xIncr)
			.attr("height", yIncr)
			.attr('x', xPos)
			.attr('y', yPos)
			.style('fill', colorOfRect)
			.style('stroke', colorOfRect);



		rect.data([data_forPlot[i]])
		.on("mouseover", function(d){
			d3.select(this)
				.style('stroke-width', 5);

			toolTip.transition()
				///.duration(200)
				.style("opacity", 1);
			toolTip.html("<b>" +  data_forPlot[i].y_name + ", " + data_forPlot[i].x_name + "</b>"  + "<br>" + "<i>Isolates</i>: " + data_forPlot[i].isoCount + " <br> <i>Number of STs</i>: " + data_forPlot[i].stDist + " <br> <i> Shannon index</i>: " + data_forPlot[i].shannon + " <br> <i> Equitability</i>: " + equitability.toFixed(3))
				.style("left", event.pageX + "px")
				.style("top", event.pageY + "px");
		})
		.on("mouseout", function(d) {
			d3.select(this)
				.style('stroke-width', 1);

			toolTip.transition()
			.style("opacity", 0);
		});

	}



	yPos = yPos + yIncr;

	theChart_svg.attr("width", keys_xAxisSorted.length * xIncr + xOffset + 400)
		.attr("height", yPos + 200);

	// console.log(keys_xAxisSorted);
	// console.log(keys_yAxis);

	// Plotting the axis
	let x_scale = d3.scaleBand()
		.domain(keys_xAxisSorted)
		.range([0, keys_xAxisSorted.length * xIncr]);

	let y_scale = d3.scaleBand()
		.domain(keys_yAxis)
		.range([0, yPos]);
		// .ticks().concat([0, maxY+1]);
		// .nice();

   // Add scales to axis
	let x_axis = d3.axisBottom()
	// 	.attr("transform", "translate(0," + xOffset + ")")
		.scale(x_scale);


	let y_axis = d3.axisLeft()
	//	.attr("transform", "translate(0,50)")
		.scale(y_scale);

	/*
	if (maxY < 100){
		y_axis.tickValues(maxY);
	}
	*/
	let xAxis = g.append('g')
		.call(x_axis);


	xAxis.attr("transform", "translate(" + xOffset + ", " + yPos + ")")
		.selectAll("text")
		.style("text-anchor", "end")
		.attr("dx", "-.8em")
		.attr("dy", "-.5em")
		.attr("transform", "rotate(-60)");

	// X-axis label:
	// text label for the x axis
	 theChart_svg.append("text")
		//.attr("transform",
		//	   "translate(" + (overwidthX/2) + " ," +
		//					  (overwidthY - margin.top + 5) + //")")
		.style("text-anchor", "middle")
		.text(getZoomByDisplayText('Year'))
		.attr("class", "xAxisText")
		.attr("id", 'g2_year');
		/* .on('dblclick', function(){
			changeZoomLvl(respData);
		}); */


	let yAxis = g.append('g')
		.call(y_axis);
	yAxis.attr("transform", "translate(" + 100 + ",0)");

	theChart_svg.selectAll('defs').remove();

	var defs = theChart_svg.append("defs");

	//Append a linearGradient element to the defs and give it a unique id
	var linearGradient = defs.append("linearGradient")
	    .attr("id", "linear-gradient");



	let textToShow_max = maxValForNorm;
	let textToShow_min = minValForNorm;
	if (colBy_choice == G2_colByBtns[0]){
		textToShow_max = maxShannonVal;
		textToShow_min = minShannonVal;
	}

	let minRatio_legend = textToShow_min; let maxRatio_legend = textToShow_max;
	if (textToShow_max != 0){
		minRatio_legend = textToShow_min/textToShow_max;
		maxRatio_legend = textToShow_max/textToShow_max;
	}

	linearGradient
	    .attr("x1", "0%")
	    .attr("y1", "0%")
	    .attr("x2", "0%")
	    .attr("y2", "100%");

	linearGradient.append("stop")
		.attr("offset", "0%")
		.attr("stop-color", getColor_bet0And1(minRatio_legend)); //light blue

	//Set the color for the end (100%)
	linearGradient.append("stop")
		.attr("offset", "100%")
		.attr("stop-color", getColor_bet0And1(maxRatio_legend)); //dark blue


	xPos_max = xPos_max + xIncr + xIncr;

	theChart_svg.append("rect")
	    .attr("width", 20)
	    .attr("height", 150)
		.attr('x', xPos_max)
		.attr('y', 10)
	    .style("fill", "url(#linear-gradient)");



	console.log("Min " + textToShow_min + " Max " + textToShow_max);
	console.log(colBy_choice);

	if (colBy_choice == G2_colByBtns[0]){
		theChart_svg.append("text")
		.attr('x', xPos_max + 20 )
	 .attr('y', 20)
		.style("text-anchor", "right")
		.text(minRatio_legend.toFixed(2))
		.attr("class", "xAxisText");

 theChart_svg.append("text")
		.attr('x', xPos_max + 20)
	 .attr('y', 160)
		.style("text-anchor", "right")
		.text(maxRatio_legend.toFixed(2))
		.attr("class", "xAxisText");

	}
	else {
		theChart_svg.append("text")
			.attr('x', xPos_max + 20 )
			.attr('y', 20)
			.style("text-anchor", "right")
			.text(textToShow_min)
			.attr("class", "xAxisText");

		theChart_svg.append("text")
			.attr('x', xPos_max + 20)
			.attr('y', 160)
			.style("text-anchor", "right")
			.text(textToShow_max)
			.attr("class", "xAxisText");
	}	
	

	d3.select('#g2_downloadAsSvg').on('mouseover', writeDownloadLink("#g2_downloadAsSvg", "#svg_g2_"));
}


function g2_doTheTransformation(respData, colNums, aggByCols_time, aggByCols_loc){
	console.log("respData: ");
	console.log(respData);



	let data_forPlot = []; // dict_{stCcOdc, loc, year} = {count};
	// let dict_colors = {};

	let total = 0;
	let shown = 0;

	respData.forEach(function(item, i){
		if (i != 0){
			total = total + item[colNums['count']];
			if (item[colNums['stCcOdc']] != null){
			//} && item[colNums[aggByCol]] != null) {
				let isAnyNull = false;
				let x_nameInObjVal = '';
				let y_nameInObjVal = '';
				aggByCols_time.forEach(function(aggByCol, aggByCol_i){
					if (item[colNums[aggByCol]] == null){
						isAnyNull = true;
					}
					if (x_nameInObjVal == ''){
						x_nameInObjVal = item[colNums[aggByCol]];
					}
					else {
						x_nameInObjVal = item[colNums[aggByCol]] + '-' + x_nameInObjVal;
					}

				});

				aggByCols_loc.forEach(function(aggByCol, aggByCol_i){
					if (item[colNums[aggByCol]] == null){
						isAnyNull = true;
					}
					if (y_nameInObjVal == ''){
						y_nameInObjVal = item[colNums[aggByCol]];
					}
					else {
						y_nameInObjVal = item[colNums[aggByCol]] + '-' + y_nameInObjVal;
					}

				});

				// console.log(nameInObjVal);

				if (isAnyNull == false){
					shown = shown + item[colNums['count']];
					let anObj = data_forPlot.find(el => el.x_name == x_nameInObjVal && el.y_name == y_nameInObjVal);

					let theStCcOdcKey = colNums['stCcOdc_type'] + String(item[colNums['stCcOdc']]);
					// console.log(theStCcOdcKey);
					if (anObj && anObj.hasOwnProperty(theStCcOdcKey)){
						anObj[theStCcOdcKey] = Number(anObj[theStCcOdcKey]) + Number(item[colNums['count']]);


					}
					else if (anObj){
						anObj[theStCcOdcKey] =  item[colNums['count']]; // assuming by reference;
					}
					else{
						let objToAdd = {'x_name': x_nameInObjVal, 'y_name': y_nameInObjVal};
						objToAdd[theStCcOdcKey] = Number(item[colNums['count']]);

						data_forPlot.push(objToAdd);
					}

				}

			}

		}
	});

	document.getElementById('g2_summaryLine_totalNum').innerHTML = total;
	document.getElementById('g2_summaryLine_shownNum').innerHTML = shown;
	return ({data_forPlot: data_forPlot});
}

function g2_sortDataByLocation(dataForPlot){
	dataForPlot.sort(function(a, b){
		// console.log(a.y_name + " ... " + b.y_name);
		if (a.y_name == b.y_name){
			return a.x_name - b.x_name;
		}
		else {
			return a.y_name > b.y_name ? 1: -1;
		}

	});
}

/*
function g2_getTheColsToAggrBy(){
	return ({time: ['year'], location: ['country']});
}
*/

function g2_convertToMergedStFormat(data_forPlot){
	// assuming by reference;

	console.log("previous to mergedSt format");
	console.log(data_forPlot);


	data_forPlot.forEach(function(anObj, anObj_i){
		let isoCount = 0;
		let stDist = 0;

		// Calculate totals
		Object.keys(anObj).forEach(function(item, i){
			if (item !== 'x_name' && item !== 'y_name'){
				isoCount = isoCount + anObj[item];
				stDist = stDist + 1;
				// delete anObj[item];
			}
		});


		// Calculate shannon index;
		let totalLogVal = 0;
		Object.keys(anObj).forEach(function(item, i){
			if (item !== 'x_name' && item !== 'y_name' ){
				let p = parseInt(anObj[item]) / isoCount;
				let q = Math.log(p) * p;

				totalLogVal = totalLogVal + q;

				delete anObj[item];
			}
		});


		anObj['shannon'] = (totalLogVal * -1).toFixed(3);
		anObj['isoCount'] = isoCount;
		anObj['stDist'] = stDist;


	});


	// console.log('merged St format: ');
	// console.log(data_forPlot);


}

function getMaxShannon(data_forPlot, key){
	let maxVal = 0;
	data_forPlot.forEach(function(item, i){
		if (item[key] > maxVal){
			maxVal = item[key];
		}
	});

	return maxVal;
}

function getMinShannon(data_forPlot, key, maxVal){
	let minVal = maxVal;
	data_forPlot.forEach(function(item, i){
		if (item[key] < minVal && item[key] >= 0){
			minVal = item[key];
		}
	});

	return minVal;
}



function getColor_bet0And1(value){
    //value from 0 to 1
    var hue=(value * 100).toString(10);
	// console.log("hue is " + hue + "%");
    return ["hsl(0," + hue + "%,50%)"].join("");
}


function g2_readThe2LvlChoices(){

	let lvlChoices = {lvl1: G2_lvl1_btnSt, lvl2: ''};
	let lvl2BtnDiv = G2_lvl2_btnsDivSt;


	if (document.getElementById(G2_lvl1_btnCc).classList.contains('btn-default-spe')){
		lvlChoices.lvl1 = G2_lvl1_btnCc;
	}
	else if (document.getElementById(G2_lvl1_btnOdc).classList.contains('btn-default-spe')) {
		lvlChoices.lvl1 = G2_lvl1_btnOdc;
	}


	let lvl2Btns = document.getElementById(lvl2BtnDiv).querySelectorAll("button");

	lvl2Btns.forEach(function(aBtn, aBtn_i){
		if (aBtn.classList.contains('btn-default-spe')){
			lvlChoices.lvl2 = aBtn.id;
		}
	});

	// console.log(lvlChoices);

	return (lvlChoices);
}
