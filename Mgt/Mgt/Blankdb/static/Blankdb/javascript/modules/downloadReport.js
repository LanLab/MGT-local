export {checkAndGetData, downloadTheReport_4};
import {ajaxCall} from './packageAndSend.js';
import {getRandomColor} from './generateColors.js';


function checkAndGetData(url){


	let sel_country = document.getElementById('id_country').value;
	let sel_project = document.getElementById('id_project');

	let sel_yearStart = document.getElementById('id_year_start').value;
	let sel_yearEnd = document.getElementById('id_year_end').value;

	sel_yearStart = parseInt(sel_yearStart); 
	sel_yearEnd = parseInt(sel_yearEnd); 

	// console.log("Year start and end is " + sel_yearStart + ' ' + sel_yearEnd);


	if (sel_country == '' && sel_project == ''){
		document.getElementById('noteToShow_inside').innerText = 'Please select a country or a project';
		return;
	}
	else if (sel_project) {
		sel_project = sel_project.value;
	}
	else if (!sel_country) {
		document.getElementById('noteToShow_inside').innerText = 'Error: Please select a country!';
		return;
	}

	if (sel_yearStart > sel_yearEnd) {
		document.getElementById('noteToShow_inside').innerText = 'Error: starting year should be smaller-than, or equal-to, the ending year.';
		return;
	}

	document.getElementById('noteToShow_inside').innerText = '';

	let data = {
		'country': sel_country,
		'project': sel_project,
		'yearStart': sel_yearStart,
		'yearEnd': sel_yearEnd,
	};

	document.getElementById('div_report').style.visibility = "hidden";
	ajaxCall(url, data, transformAndBuildRep)
}


function transformAndBuildRep(response){
	document.getElementById('div_report').style.visibility = "";


	console.log("The response is ");
	console.log(response);

	if (response.hasOwnProperty('isolates') && response['isolates'].length > 0 && response.hasOwnProperty('yearCurr')){
		// Build the report

		let yearCurr = parseInt(response['yearCurr']);
		let dict_isoCounts = [];
		let year_10Ago = parseInt(response['year_10Ago'])


		// Chart 1
		if (response.hasOwnProperty('tabAps') && response.hasOwnProperty('cols') && response.hasOwnProperty('yearCurr') && response.hasOwnProperty('year_10Ago')){
			dict_isoCounts = buildChart1(response['isolates'], response.tabAps, response.cols, year_10Ago, parseInt(response['yearCurr']), response.country , response.project_name);

			// console.log(response.project_name);
		}


		let year_3Ago = yearCurr - 3 + 1;

		console.log('Year calculations are: ' + yearCurr + " " + year_3Ago + " " + parseInt(response['year_10Ago']));
		
		if (year_3Ago < year_10Ago){
			year_3Ago = year_10Ago;
		}


		// Chart 2
		if (response.hasOwnProperty('isSelCountry') && response.hasOwnProperty('tabAps') && response.hasOwnProperty('cols')){
			buildChart2(response['isolates'], response.tabAps, response['isSelCountry'], response['cols'], year_3Ago,  parseInt(response['yearCurr']), response.country, response.project_name);

		}

		// Chart 3 (table)
		if (response.hasOwnProperty('tabAps')){
			buildChart3(response['isolates'], response['tabAps'], year_3Ago, yearCurr, response['cols'], dict_isoCounts, response.country, response.project_name);
		}

		// }


		// Chart 4
		if (response.hasOwnProperty('tabAps')){
			buildChart4(response['isolates'], response['cols'], response['tabAps'], response.country, response.project_name);
		}

		// Charts for each MGT level
		let table_start = 2;
		let figure_start = 4;
		if (response.hasOwnProperty('tabAps') && response.hasOwnProperty('tabCcs') && response.hasOwnProperty('cols')){
			// Setup the divs
			setupDivs(response['tabAps']);

			for (let i=0; i<response['tabAps'].length; i++){
				let tabCcsForanAp = getCcsForAp(response['tabAps'][i], response['tabCcs']);

				let prevApObj = {}; let nextApObj = {};
				if (i > 0){
					prevApObj = response['tabAps'][i-1];
				}
				if (i < response['tabAps'].length-1){
					nextApObj = response['tabAps'][i+1];
				}

				if (i == 0){
					document.getElementById('chart_mgtLvl'+ i + '_4prev_svg').style.display = 'none';
				}
				if (i == response['tabAps'].length-1){
					document.getElementById('chart_mgtLvl' + i + '_4next_svg').style.display = 'none';
				}
				// console.log("Butters ");
				// console.log(response['tabAps'][i]);

				handleCharts_oneMgtLvl(response['tabAps'][i], tabCcsForanAp, response['isolates'], response['cols'], i, yearCurr, year_10Ago, prevApObj, nextApObj, response.country, table_start, figure_start, response.project_name);
				table_start = table_start + 1;
				figure_start = figure_start + 4;
			}
		}
		// console.log("The response is ");
		// console.log(response);

		printReportIntro(response.country, response.project_name, parseInt(response['year_10Ago']), yearCurr);

		document.getElementById('noteToShow_outside').innerHTML = "";

		document.getElementById('btn_doTheDownload').disabled = false;
	}
	else{
		// Print no data to show.

		document.getElementById('noteToShow_outside').innerHTML = "No data to show.";

		document.getElementById('btn_doTheDownload').disabled = true;
		document.getElementById('noteToShow').innerHTML = "No data to show.";
		clearAllDivs();
		document.getElementById('div_report').style.visibility = "hidden";
	}
}

function clearAllDivs(){

	for (let i =1; i<=4; i++){
		if (i != 3){
			document.getElementById('chart' + i + "_svg").innerHTML = "";
		}
		else {
			document.getElementById('chart' + i + "_table").innerHTML = "";
		}
		document.getElementById('chart' + i + "_p").innerHTML = "";
	}

	document.getElementById('chart_mgtLvls').querySelectorAll('[id^="chart"]').forEach(function(aSvg, aSvg_i){
		aSvg.innerHTML = "";
	});
}


function printReportIntro(country, project, yearStart, yearCurr){
	let innerHTML = "This report sumarizes isolates deposited in <a href='" + window.location.origin + "' target='_blank'> MGTdb </a> over the past " + (yearCurr - yearStart + 1) + " years with "

	if (String(country) != 'null'){
		innerHTML = innerHTML + " <i>country</i> '" + country + "'"
	}

	if (String(country) != 'null' && String(project) != 'null'){
		innerHTML = innerHTML + " and ";
	}

	if (String(project) != "null"){
		innerHTML = innerHTML + " <i>project</i> '" + project + "'";
	}

	innerHTML = innerHTML + ". <br> <br>";


	innerHTML = innerHTML + "As described in <a href='https://doi.org/10.2807/1560-7917.ES.2020.25.20.1900519' target='_blank'> our paper</a>, analysis of isolates using smaller MGTs are recommended for longer-term epidemiological investigations and larger MGTs are recommended for shorter-term epidemiological investigations. <br><br> ";

	innerHTML = innerHTML + "The various MGT levels are listed below. MGT1 which is equivalent to the 7-gene MLST is not included in this report, but the assignments to the isolates can be explored on the <a href='" + window.location.origin + "' target='_blank'>MGT website</a>. <br><br>"

	document.getElementById('noteToShow').innerHTML = innerHTML;


	document.getElementById('genTimeStamp').innerHTML = "<i> Report generated on " + new Date() + ".</i>"
	// console.log(window.location.origin);


}


//////////////////// NEW

function buildChart1(isolates, tabAps, colNames, yearStart, yearCurr, country, project){
	// 1. Get largest tabAp (+ its display name) (tabAps is already ordered)
	// 2. Get col num of tabAp, and isoId, then count.

	let largestMgt = tabAps[tabAps.length-1];


	// let colNum_iso = getColNum('identifier', colNames);
	let colNum_largestMgt = getColNum(largestMgt['table_name']+"_st", colNames);
	let colNum_year = getColNum('year', colNames);

	let res = extractData_1(isolates, yearStart, yearCurr, colNum_year, colNum_largestMgt);

	// console.log('Extracted data is ');
	// console.log(res);

	console.log("The largest MGT is ");
	console.log(largestMgt); 

	plotChart_1(res.arr_isoCounts, yearStart, yearCurr, res.arr_uniqLargestMgtCnt, country, project, largestMgt.display_name);

	return (res.dict_isoCounts);

}

function buildChart2(isolates, tabAps, isSelCountry, colNames, yearStart, yearCurr, country, project){

	let colNameOfInt = '';

	if (isSelCountry){
		colNameOfInt = 'state';
	}
	else {
		colNameOfInt = 'country';
	}

	let colNum_ofInt = getColNum(colNameOfInt, colNames);
	let colNum_year = getColNum('year', colNames);

	let arr_counts = extractData_2(isolates, colNum_ofInt, yearStart, yearCurr, colNum_year);
	
	console.log("Testing 123 " + colNum_ofInt);
	console.log(arr_counts);

	
	plotChart_2(arr_counts, yearCurr, yearStart);
	writeCaption_2(yearCurr, yearStart, country, project);

}

function buildChart3(isolates, tabAps, yearStart, yearCurr, colNames, dict_isoCounts, country, project){
	let colNums_mgts = []; // corresponds, in order, -1 when value not in cols
	let colNum_year =  getColNum('year', colNames);

	for (let i=0; i<tabAps.length; i++){
		let colNum = getColNum(tabAps[i]['table_name'] + "_st", colNames);
		colNums_mgts.push(getColNum(tabAps[i]['table_name'] + "_st", colNames));
	}

	let res = extractData_3(isolates, colNum_year, colNums_mgts, yearStart, yearCurr);
	writeToTable_3(dict_isoCounts, res.counts3Year, res.countsAll, yearStart, yearCurr, tabAps);
	writeCaption_3(yearStart, yearCurr, country, project)
}

function buildChart4(isolates, colNames, tabAps, country, project){
	let colNums_mgts = []; // corresponds, in order, -1 when value not in cols

	for (let i=0; i<tabAps.length; i++){
		let colNum = getColNum(tabAps[i]['table_name'] + "_st", colNames);
		colNums_mgts.push(getColNum(tabAps[i]['table_name'] + "_st", colNames));
	}

	let dict_counts = extractData_4(isolates, colNums_mgts);
	transformAndPlot_4(dict_counts, tabAps, isolates.length);
	writeCaption_4(country, project);
}


function extractData_4(isolates, colNums_mgts){
	let dict_counts = {}; // dict_{mgtLvl} => {stVal} => count

	for (let i=0; i < isolates.length; i++){
		for (let j=0; j < colNums_mgts.length; j++){
			if (!dict_counts.hasOwnProperty(j)){
				dict_counts[j] = {};
			}
			if (isolates[i][colNums_mgts[j]]){
				if (!dict_counts[j].hasOwnProperty(isolates[i][colNums_mgts[j]])){
					dict_counts[j][isolates[i][colNums_mgts[j]]] = 1;
				}
				else {
					dict_counts[j][isolates[i][colNums_mgts[j]]] = dict_counts[j][isolates[i][colNums_mgts[j]]] + 1;
				}
			}
		}
	}

	return (dict_counts);
}


function extractData_3(isolates, colNum_year, colNums_mgts, yearStart, yearCurr){

	// 1. Extraction

	let dict_counts_3year = {}; let dict_counts_all = {}; // dict_{year} => {colNumMgtIdx} => [mgtStVal, ...]

	// Number of MGT sts at each level

	for (let i=0; i < isolates.length; i++){
	 	let isoYear = isolates[i][colNum_year];

		if (isoYear >= yearStart && isoYear <= yearCurr){
			for(let j=0; j<= colNums_mgts.length; j++){

				addMgtStDataToDict(colNums_mgts, isolates[i], isoYear, dict_counts_3year); // Not efficient but faster to program!
			}
		}


		addMgtStDataToDict(colNums_mgts, isolates[i], isoYear, dict_counts_all);
	}

	// 2. Formatting and interpolation



	return ({'counts3Year': dict_counts_3year, 'countsAll': dict_counts_all});
}

function getNumStsNotInPrev(arr_yearSts, dict_countsAll, year, mgtLvl){

	let allPrevSts = []; // []
	let uniqSts = [];

	for (let year_all in dict_countsAll){
		if (year_all < year){
			allPrevSts = allPrevSts.concat(dict_countsAll[year_all][mgtLvl])
		}
	}

	// console.log(allPrevSts);

	for (let i = 0; i < arr_yearSts.length; i++){
		if (!allPrevSts.includes(arr_yearSts[i])){
			uniqSts.push(arr_yearSts[i]);
		}
	}

	// console.log(uniqSts);

	return (uniqSts.length)
}

function addMgtStDataToDict(colNums_mgts, isolate, isoYear, dict_counts){
	for(let j=0; j<= colNums_mgts.length; j++){
		if (isolate[colNums_mgts[j]]) {
			// console.log(isolates[i][colNums_mgts[j]]);

			if ( !dict_counts.hasOwnProperty(isoYear) ){
				dict_counts[isoYear] = {};
			}

			if ( !dict_counts[isoYear].hasOwnProperty(j)){
				dict_counts[isoYear][j] = [];
			}


			if (!dict_counts[isoYear][j].includes(isolate[colNums_mgts[j]])) {
				dict_counts[isoYear][j].push(isolate[colNums_mgts[j]]);
			}
		}
	}
}


function extractData_2(isolates, colNum_ofInt, yearStart, yearCurr, colNum_year){
	let dict_counts = {}; let arr_counts = [];

	// console.log(yearStart + " " + yearCurr);

	for (let i=0; i<isolates.length; i++){
		let isoYear = parseInt(isolates[i][colNum_year]);

		if (isoYear >= yearStart && isoYear <= yearCurr){
			let intColVal = isolates[i][colNum_ofInt];

			if (!dict_counts.hasOwnProperty(isoYear)){
				dict_counts[isoYear] = {};
			}
			if (!dict_counts[isoYear].hasOwnProperty(intColVal)){
				dict_counts[isoYear][intColVal] = 0
			}
			dict_counts[isoYear][intColVal] = dict_counts[isoYear][intColVal] + 1;
		}
	}

	// console.log("The dict_counts value in _2 is ");
	// console.log(dict_counts);

	// convert to array
	for (let year in dict_counts){
		for (let countryOrState in dict_counts[year]){
			arr_counts.push([year, dict_counts[year][countryOrState], countryOrState]);
		}
	}


	return (arr_counts);
}

// This one interpolates (and data is in right order also);
function extractData_1(isolates, yearStart, yearCurr, colNum_year, colNum_largestMgt){
	let dict_isoCounts = {}; let dict_uniqMgt9Ids = {}; // dict{year} => [list of sts] (can .includes() to check)
	let arr_isoCounts = [];
	let arr_uniqLargestMgtCnt = [];

	for (let i=0; i<isolates.length ; i++){
		let isoYear = parseInt(isolates[i][colNum_year]);
		// console.log(isoYear );
		let stVal = isolates[i][colNum_largestMgt];
		// console.log("Year val is " + isoYear + ' ' + yearStart + ' ' + yearCurr);
		if (isoYear >= yearStart && isoYear <= yearCurr){
			if (!dict_isoCounts.hasOwnProperty(isoYear)){
				dict_isoCounts[isoYear] = 0;
			}


			if (!dict_uniqMgt9Ids.hasOwnProperty(isoYear)){
				dict_uniqMgt9Ids[isoYear] = [];
			}
			if (!dict_uniqMgt9Ids[isoYear].includes(stVal)) {
				dict_uniqMgt9Ids[isoYear].push(stVal);
			}

			dict_isoCounts[isoYear] = dict_isoCounts[isoYear]  + 1;
		}

	}

	// console.log (dict_isoCounts);
	// console.log (dict_uniqMgt9Ids);

	for (let i = yearStart; i<=yearCurr; i++){
		if (!dict_isoCounts.hasOwnProperty(i)){
			arr_isoCounts.push([i, 0]);
		}
		else {
			arr_isoCounts.push([i, dict_isoCounts[i]]);
		}

		if (!dict_uniqMgt9Ids.hasOwnProperty(i)){
			arr_uniqLargestMgtCnt.push([i, 0]);
		}
		else {
			arr_uniqLargestMgtCnt.push([i, dict_uniqMgt9Ids[i].length]);
		}
	}



	// console.log (arr_isoCounts);
	// console.log(arr_uniqLargestMgtCnt);
	return ({dict_isoCounts: dict_isoCounts, dict_uniqMgt9Ids: dict_uniqMgt9Ids, arr_isoCounts: arr_isoCounts, arr_uniqLargestMgtCnt: arr_uniqLargestMgtCnt});
}


function getColNum(key, colNames){
	// console.log("colname is " + key);
	for (let i=0; i<colNames.length; i++){
		if (key == colNames[i]){
			return i;
		}
	}

	return -1;
}

































////////////////// CHART PLOTTING FUNCTIONS

function transformAndPlot_4(dict_counts, tabAps, numIsolates){

	document.getElementById("chart4_svg").innerHTML = "";
	let maxPlotHeight = 300;


	// Scale
	let dict_scaledCounts = {}; // dict{maxVal} => [scaledCount1, scaledCount2 ...];
	let arr_numOfSts = [];

	// 1. Find max
	for (let mgtLvl in dict_counts){

		let totalVal = findTotalVal_4(dict_counts[mgtLvl]);
		dict_scaledCounts[mgtLvl] = [];
		scale_4(dict_scaledCounts, mgtLvl, dict_counts[mgtLvl], totalVal, maxPlotHeight);

		arr_numOfSts.push(dict_scaledCounts[mgtLvl].length);
	}

	// console.log(arr_numOfSts);

	sumLessThanOneAndSort_4(dict_scaledCounts);
	// console.log(dict_scaledCounts);

	d3.selectAll("#chart4_svg > *").remove();
	
	let theChart_svg = d3.select("#chart4_svg");
	let g = theChart_svg.append("g");

	// Now the plotting
	let xOffset = 60; let yOffset = 50;
	let xPos = xOffset; let barWidth = 20; let xIncr = 30;
	for (let mgtLvl in dict_scaledCounts){
		if (!mgtLvl.match(/other$/)){

			let yPos =  maxPlotHeight - yOffset - dict_scaledCounts[mgtLvl + "_other"];

			for (let i=0; i< dict_scaledCounts[mgtLvl].length; i++){
				let rect = g.append('rect')
					.attr('width', barWidth)
					.attr('height',   dict_scaledCounts[mgtLvl][i])
					.attr('x', xPos)
					.attr('y', (maxPlotHeight - yPos) )
					.style('fill', getRandomColor(i, i, 1))
					.style('stroke', getRandomColor(i, i, 1))
					.style('stroke-width', 0.2);

				yPos = yPos - dict_scaledCounts[mgtLvl][i];
			}

			yPos = maxPlotHeight - yOffset;
			let rect = g.append('rect')
				.attr('width', barWidth)
				.attr('height',   dict_scaledCounts[mgtLvl + "_other"])
				.attr('x', xPos)
				.attr('y', (maxPlotHeight - yPos) )
				.style('fill', 'white')
				.style('stroke', '#FAF9F6')
				.style('stroke-width', 0.2);

			xPos = xPos + xIncr;
			// console.log("xPos is " + xPos);
		}

	}

	let xBottomNames = getListOfMgtNames_4(tabAps);

	let x_scale = d3.scaleBand()
		.domain(xBottomNames)
		.range([xOffset, (xOffset + xBottomNames.length * xIncr)]);
	let x_scale_top = d3.scaleBand()
		.domain(arr_numOfSts)
		.range([xOffset, (xOffset + arr_numOfSts.length * xIncr)]);
	let y_scale = d3.scaleLinear()
		.domain([0, numIsolates])
		.range([maxPlotHeight, 0]);




	let x_axis = d3.axisBottom()
	// 	.attr("transform", "translate(0," + xOffset + ")")
		.scale(x_scale);
	let x_axis_top = d3.axisTop()
	// 	.attr("transform", "translate(0," + xOffset + ")")
		.scale(x_scale_top);
	let y_axis = d3.axisLeft()
 	//	.attr("transform", "translate(0,50)")
 		.scale(y_scale);


	let xAxis = theChart_svg.append('g')
		.call(x_axis);
	let xAxis_top = theChart_svg.append('g')
		.call(x_axis_top);

	xAxis.attr("transform", "translate(" + -5 + ", " + (maxPlotHeight + yOffset) + ")")
		.selectAll("text")
		.style("text-anchor", "end")
		.attr("dx", "-.8em")
		.attr("dy", "-.5em")
		.attr("transform", "rotate(-60)");


	xAxis_top.attr("transform", "translate(" + -5 + ", " + yOffset + ")")
		.selectAll("text")
		.style("text-anchor", "middle");


	let yAxis = g.append('g')
		.call(y_axis);
	yAxis.attr("transform", "translate(" + xOffset + ", " + yOffset + ")");


	xAxisLabel("MGT level", xPos/2, maxPlotHeight+ 80 + yOffset, theChart_svg);
	xAxisLabel("Number of STs", xPos/2, 15, theChart_svg);

	yAxisLabel("Number of isolates", xOffset, ((yOffset+maxPlotHeight)/2), g, 'chart1_yLabel');
}

function getListOfMgtNames_4(tabAps){
	let xBottomNames = [];

	for (let i = 0; i < tabAps.length; i++){
		xBottomNames.push(tabAps[i]['display_name']);
	}

	return xBottomNames;
}

function sumLessThanOneAndSort_4(dict_scaledCounts){

	for (let mgtLvl in dict_scaledCounts){
		// Adding those with < 1 to otherVal
		let otherVal = 0;	let keyOtherVal = mgtLvl+"_other";
		let idxToRm = [];
		for (let i=0; i < dict_scaledCounts[mgtLvl].length; i++){
			if (dict_scaledCounts[mgtLvl][i] < 1){
				otherVal = otherVal + dict_scaledCounts[mgtLvl][i];
				idxToRm.push(i);
			}
		}

		// Removing those with < 1
		idxToRm = idxToRm.reverse();

		for (let i=0; i < idxToRm.length; i++){
			dict_scaledCounts[mgtLvl].splice(idxToRm[i],1);
		}

		// Sorting each of the arrays
		dict_scaledCounts[mgtLvl] = dict_scaledCounts[mgtLvl].sort((a,b) => a-b);


		dict_scaledCounts[keyOtherVal] = otherVal;
		// dict_scaledCounts[mgtLvl].unshift(otherVal);
		// dict_scaledCounts[mgtLvl] = dict_scaledCounts[mgtLvl].reverse();

	}
}

function scale_4(dict_scaledCounts, mgtLvl, dict_counts_mgtLvl, totalVal, maxPlotHeight){

	for (let stVal in dict_counts_mgtLvl){
		let scaledVal = (dict_counts_mgtLvl[stVal]/totalVal) * maxPlotHeight;
		dict_scaledCounts[mgtLvl].push(scaledVal);
	}
}

function findTotalVal_4(dict_stValCnt){
	let total = 0;

	for (let stVal in dict_stValCnt){
		// if (dict_stValCnt[stVal] > max){
		total = total + dict_stValCnt[stVal];
		// }
	}

	return total;
}

function writeToTable_3(dict_isoCounts, dict_counts3Year, dict_countsAll, yearStart, yearCurr, tabAps){
	let innerHTML = '';

	// print the header
	innerHTML = innerHTML + "<tr><th>Year</th> <th> Number of isolates </th>";
	for (let h=0; h <tabAps.length; h++){

		innerHTML = innerHTML + "<th> Number of " + tabAps[h]['display_name'] + "s</th>";
	}
	innerHTML = innerHTML + "</tr>";

	// Actual rows
	for (let year = yearStart; year <= yearCurr; year++){
		innerHTML = innerHTML + "<tr> <td>" + year + "</td>";
		// Num of isolate
		let isoCount = 0;
		if (dict_isoCounts.hasOwnProperty(year)){
			isoCount = dict_isoCounts[year];
 		}

		innerHTML = innerHTML + "<td>" + isoCount + "</td>"

		// Each st num, and num new
		if (dict_counts3Year.hasOwnProperty(year)){
			let numSts = 0; let numNewSts = 0;
			for (let i=0; i < tabAps.length; i++){
				if (dict_counts3Year[year].hasOwnProperty(i)){
					numSts = dict_counts3Year[year][i].length;
					numNewSts = getNumStsNotInPrev(dict_counts3Year[year][i], dict_countsAll, year, i);
				}
				else {
					// console.log(dict_counts3Year[year][i]);
				}
				innerHTML = innerHTML + " <td> " + numSts + "(" + numNewSts + ")</td>";
			}
		}
		else { // Print 0's.
			for (let i=0; i < tabAps.length; i++){
				innerHTML = innerHTML + " <td> 0 (0)</td>";
			}
		}


		innerHTML = innerHTML + "</tr>";
	}

	// console.log(innerHTML);

	document.getElementById('chart3_table').innerHTML = innerHTML;
}


function plotChart_mgtLvl1(keysSorted, theCounts, tableName_st, tableNames_cc, chartId_stNum, country, project){

	let total = getTotalStCount(theCounts.stCounts);

	let innerHTML = '';

	innerHTML = innerHTML + "<tr> <th> " + tableName_st + "</th> <th> Count </th> <th> Percentage in " + getProjCountryStr(country, project) + " isolates </th> ";

	for (let c =0; c<tableNames_cc.length; c++){
		innerHTML = innerHTML + "<th>" + tableNames_cc[c]  + " </th>";
	}
	innerHTML = innerHTML + "</tr>";

	for (let i=0; i< 10 && i<keysSorted.length; i++){
		innerHTML = innerHTML + "<tr>";
		// St val
		innerHTML = innerHTML + "<td>" + keysSorted[i] + "</td>";

		// St count
		innerHTML = innerHTML + "<td>" + theCounts.stCounts[keysSorted[i]] + "</td>";

		// Percentage
		let percentIn10Year = (theCounts.stCounts[keysSorted[i]]/total) * 100;
		innerHTML = innerHTML + "<td> " + percentIn10Year.toFixed(2) + "% </td>";

		// Cc vals (printing only the smallest ccVal)


		for (let j = 0; j<tableNames_cc.length; j++){
			theCounts.ccForSt[keysSorted[i]][j].sort(function(a, b){
				return a-b;
			});

			let smallestVal = '-';
			if (theCounts.ccForSt[keysSorted[i]][j].length > 0){
				smallestVal = theCounts.ccForSt[keysSorted[i]][j][0];
			}


			innerHTML = innerHTML + "<td>" + smallestVal +  "</td>";
		}

		innerHTML = innerHTML + "</tr>";
	}

	document.getElementById('chart_mgtLvl' + chartId_stNum + "_0_table").innerHTML = innerHTML;

	// document.getElementById('chart_mgtLvl' + chartId_stNum + "_0_p").innerHTML = "Table Y: % calculated for past 10 years.";
}

function getValOr0FromArr(year, arr_isoCounts){
	for (let i=0; i<arr_isoCounts.length; i++){
		if (arr_isoCounts[i][0] == year){
			return arr_isoCounts[i][1];
		}
	}
	return 0;
}




function plotChart_2(dataForPlot, currYear, yearStart, country){
	// let yearStart = currYear - 3 ;


	let maxPlotHeight = 300;


	let dataObj = transformTheData_2(dataForPlot, currYear, yearStart);
	let maxCount = scale_2(dataObj, maxPlotHeight);

	d3.selectAll("#chart2_svg > *").remove();
	
	let theChart_svg = d3.select("#chart2_svg");
	let g = theChart_svg.append("g");

	let yOffset = 10;

	let xOffset = 60;
	let xPos = xOffset; let barWidth = 15; let xIncr_inner = 5; let xIncr_outer = 15;
	let locNames =  Object.keys(dataObj).sort();

	if (Object.keys(dataObj).length == 0){
		let str_noData = g.append('text')
		.attr('x', xPos + 12 + 'px')
		.attr('y', maxPlotHeight - 100)
		// .attr('dy', '.5em')
		.attr('font-size', '12px')
		// .attr('font-family', "monospace")
		.style('text-anchor', 'left')
		.text("No data to show.");

		return;
	}
	for (let k=0; k<locNames.length; k++){
		// console.log("Tumore " + keys[k]);
		for (let i=0; i<dataObj[locNames[k]].length; i++){

			// console.log("Length is " + dataObj[locNames[k]].length + " " + dataObj[locNames[k]]);
			let rect = g.append('rect')
				.attr('width', barWidth)
				.attr('height', dataObj[locNames[k]][i])
				.attr('x', xPos)
				.attr('y', (yOffset + maxPlotHeight - parseFloat(dataObj[locNames[k]][i])))
				.style('fill', getRandomColor(i, i, 1))
				.style('stroke', 'black');


			xPos = xPos + barWidth + xIncr_inner;
		}

		xPos = xPos + xIncr_outer;
	}
	theChart_svg.attr("width", (xPos + 200) + 'px');


	// Legend
	for (let y=yearStart ; y <= currYear; y++){
		let idx = y - yearStart;
		squareLegendAndText(g, (xPos + 10),  (maxPlotHeight - 205 + (15 * idx)), getRandomColor(idx, idx, 1), (xPos+30), (maxPlotHeight - 205 + (15 * idx)) + 10, y);
	}


	// X-axis labels
	let numOfYears = (currYear - yearStart + 1);
	let x_scale = d3.scaleBand()
		.domain(locNames)
		.range([xOffset, xOffset + (barWidth * numOfYears * locNames.length) + ((numOfYears * locNames.length-1) * xIncr_inner) + ((locNames.length-1) * xIncr_outer)]);
		// .range([0, (barWidth * numOfYears * locNames.length) + ((numOfYears) * xIncr_inner) + ((locNames.length) * xIncr_outer)]);

	let y_scale = d3.scaleLinear()
		.domain([0, maxCount])
		.range([maxPlotHeight+yOffset, yOffset]);



	let x_axis = d3.axisBottom()
	// 	.attr("transform", "translate(0," + xOffset + ")")
		.scale(x_scale);
	let y_axis = d3.axisLeft()
	//	.attr("transform", "translate(0,50)")
		.scale(y_scale);


	let xAxis = theChart_svg.append('g')
		.call(x_axis);

	xAxis.attr("transform", "translate(" + 0 + ", " + (maxPlotHeight + yOffset) + ")")
		.selectAll("text")
		.style("text-anchor", "end")
		.attr("dx", "-.8em")
		.attr("dy", "-.5em")
		.attr("transform", "rotate(-60)");

	xAxisLabel("Location", (xPos + xOffset)/2, maxPlotHeight+ 80,g);
	yAxisLabel("Isolate count", 20, (maxPlotHeight/2), g, 'chart2_yLabel');

	let yAxis = g.append('g')
		.call(y_axis);
	yAxis.attr("transform", "translate(" + xOffset + ",0)");


}

function plotChart_mgtLvl_5(dict_countsByYear, dict_countsSt, topStVal, yearCurr, year_3Ago, chartId_stNum, prevNext, title){
	// console.log('chart_mgtLvl' + chartId_stNum + "_4" + prevNext + "_svg");
	document.getElementById('chart_mgtLvl' + chartId_stNum + "_4" + prevNext + "_svg").innerHTML = '';


	let height_offset = 60;
	let maxPlotHeight = 300;
	let topNtoShow = 10;

	let res = scale_mgtLvl5(dict_countsByYear, dict_countsSt, yearCurr, year_3Ago, maxPlotHeight, topNtoShow);
	// console.log(dict_countsByYear);
	let top10Sts = res.top10Sts;

	let xIncr_inner = 10;
	let barWidth = 20;

	let theChart_svg = d3.select("#chart_mgtLvl" + chartId_stNum + "_4" + prevNext + "_svg");

	let g = theChart_svg.append('g');

	let xOffset = 60;
	let xPos = xOffset;



	if (res.maxCountSummed == 0){
		let str_noData = g.append('text')
			.attr('x', xPos + 12 + 'px')
			.attr('y', maxPlotHeight - 100)
			// .attr('dy', '.5em')
			.attr('font-size', '12px')
			// .attr('font-family', "monospace")
			.style('text-anchor', 'left')
			.text("No data to show.");

		return;
	}

	for (let year = year_3Ago; year <= yearCurr; year++){
		let yPos = height_offset + maxPlotHeight;
		top10Sts.forEach(function(st, st_i){


			if (dict_countsByYear[year].hasOwnProperty(st)){
				let rect = g.append('rect')
					.attr('width', barWidth)
					.attr('height', dict_countsByYear[year][st])
					.attr('x', xPos)
					.attr('y', (yPos - parseFloat(dict_countsByYear[year][st])))
					.style('fill', getRandomColor(st, (st+5), 1))
					.style('stroke', getRandomColor(st, (st+5), 1));

				yPos = yPos - parseFloat(dict_countsByYear[year][st]);
			}


		});

		if (dict_countsByYear[year].hasOwnProperty('other')){
			if (dict_countsByYear[year].hasOwnProperty('other')){

				let rect = g.append('rect')
					.attr('width', barWidth)
					.attr('height', dict_countsByYear[year]['other'])
					.attr('x', xPos)
					.attr('y', (yPos - parseFloat(dict_countsByYear[year]['other'])))
					.style('fill', 'white')
					.style('stroke', 'grey');

				yPos = yPos - parseFloat(dict_countsByYear[year]['other']);
			}
		}

		xPos = xPos + barWidth + xIncr_inner;
	}


	// Legend
	for (let i=0; i < top10Sts.length; i++){
		squareLegendAndText(g, (xPos + 10), (height_offset + maxPlotHeight - 205 + (15 * i)), getRandomColor(top10Sts[i], (top10Sts[i]+5), 1), (xPos+30), (height_offset + maxPlotHeight - 205 + (15 * i)) + 10, ('ST' +top10Sts[i]));
	}


	// X-axis (STs)

	let x_scale = d3.scaleBand()
		.domain(Object.keys(dict_countsByYear))
		.range([xOffset, xOffset + ((Object.keys(dict_countsByYear).length * barWidth) + ((Object.keys(dict_countsByYear).length -1) * xIncr_inner))]); // + ((xLabels.length-1) * xIncr_inner)


	let x_axis = d3.axisBottom()
	// 	.attr("transform", "translate(0," + xOffset + ")")
		.scale(x_scale);


	let xAxis = theChart_svg.append('g')
		.call(x_axis);


	xAxis.attr("transform", "translate(" + 0 + ", " + height_offset + maxPlotHeight + ")")
		.selectAll("text")
		.style("text-anchor", "end")
		.attr("dx", "-.8em")
		.attr("dy", "-.5em")
		.attr("transform", "rotate(-60)");

	let ticks = xAxis.attr("transform", "translate(" + 0 + ", " + (height_offset + maxPlotHeight) + ")")
		.selectAll("text");

	xAxisLabel("Year", (xPos + xOffset)/2, height_offset + maxPlotHeight+ 80,g);


	// Y-axis (Count)
	let y_scale = d3.scaleLinear()
		.domain([0, res.maxCountSummed])
		.range([height_offset + maxPlotHeight, height_offset]);

	let y_axis = d3.axisLeft()
	//	.attr("transform", "translate(0,50)")
		.scale(y_scale);

	let yAxis = g.append('g')
		.call(y_axis);
	yAxis.attr("transform", "translate(" + xOffset + ",0)");
	yAxisLabel("Isolate count", 20, height_offset + (maxPlotHeight/2), g, 'mgtlvl_5_yLabel');


	// Chart title
	xAxisLabel(title, (xPos + xOffset)/2, (height_offset/2),g);

}


function plotChart_mgtLvl_4(dict_countsPerMonth, top5Sts, yearCurr, year_10Ago, chartId_stNum){
	document.getElementById('chart_mgtLvl' + chartId_stNum + "_3_svg").innerHTML = '';

	let maxPlotHeight = 300;

	let dataLinesAndMaxCnt = scale_mgtLvl4(dict_countsPerMonth, yearCurr, year_10Ago, top5Sts, maxPlotHeight);

	let xIncr_inner = 2.5;
	let barWidth = 7;
	let yOffset = 10;


	let theChart_svg = d3.select('#chart_mgtLvl' + chartId_stNum + '_3_svg');

	let g = theChart_svg.append('g');

	let xOffset = 60;
	let xPos = xOffset;


	if (dataLinesAndMaxCnt.maxCount == 0){
		let str_noData = g.append('text')
		.attr('x', xPos + 12 + 'px')
		.attr('y', maxPlotHeight - 100)
		// .attr('dy', '.5em')
		.attr('font-size', '12px')
		// .attr('font-family', "monospace")
		.style('text-anchor', 'left')
		.text("No data to show.");

		return;
	}

	dataLinesAndMaxCnt.xlabels.forEach(function(xKey, xKey_i){

		let yPos = maxPlotHeight + yOffset;
		top5Sts.forEach(function(stVal, stVal_i){
			let rect = g.append('rect')
				.attr('width', barWidth)
				.attr('height', dataLinesAndMaxCnt.data_lines[xKey][stVal])
				.attr('x', xPos)
				.attr('y', (yPos - parseFloat(dataLinesAndMaxCnt.data_lines[xKey][stVal])))
				.style('fill', getRandomColor(stVal, (stVal +5), 1))
				.style('stroke', getRandomColor(stVal, (stVal+5), 1));

			yPos = yPos - parseFloat(dataLinesAndMaxCnt.data_lines[xKey][stVal]);
		});
		xPos = xPos + barWidth + xIncr_inner;
	});
	theChart_svg.attr('width', (xPos + 200) + 'px');

	// Legend

	for (let i=0; i < top5Sts.length; i++){
		squareLegendAndText(g, (xPos + 10), (maxPlotHeight - 205 + (15 * i)), getRandomColor(top5Sts[i], (top5Sts[i]+5), 1), (xPos+30), (maxPlotHeight - 205 + (15 * i)) + 10, ('ST' + top5Sts[i]));
	}

	/*
	for (let i=0; i<top5Sts.length; i++){
		g.append('line')
			.attr("x1", (xPos) + 10)
			.attr("x2", (xPos) + 20)
			.attr('y1', ()
			.attr('y2', (maxPlotHeight - 205 + (15 * i)))
			.style('stroke-width', 2)
			.style('stroke', getRandomColor(i, i, 1));

		 theChart_svg.append("text")
			.attr('x', (xPos) + 30)
			.attr('y', maxPlotHeight - 200 + (15 * i))
			.style("text-anchor", "left")
			.text('ST ' + top5Sts[i]);
	}
	*/

	// X-axis (STs)

	let xlabels = [];
	for (let i=0; i<dataLinesAndMaxCnt.xlabels.length; i++){
		if (i%2 == 0){
			// console.log('here');
			xlabels.push(dataLinesAndMaxCnt.xlabels[i]);
		}
		else{
			xlabels.push();
		}
	}
	// console.log(xlabels);
	let x_scale = d3.scaleBand()
		.domain(dataLinesAndMaxCnt.xlabels)
		.range([xOffset, xOffset + ((dataLinesAndMaxCnt.xlabels.length * barWidth) + ((dataLinesAndMaxCnt.xlabels.length -1) * xIncr_inner))]); // + ((xLabels.length-1) * xIncr_inner)


	let x_axis = d3.axisBottom()
	// 	.attr("transform", "translate(0," + xOffset + ")")
		.scale(x_scale);


	let xAxis = theChart_svg.append('g')
		.call(x_axis);


	xAxis.attr("transform", "translate(" + 0 + ", " + (maxPlotHeight + yOffset) + ")")
		.selectAll("text")
		.style("text-anchor", "end")
		.attr("dx", "-.8em")
		.attr("dy", "-.5em")
		.attr("transform", "rotate(-60)");

	let ticks = xAxis.attr("transform", "translate(" + 0 + ", " + (maxPlotHeight + yOffset) + ")")
		.selectAll("text");

	ticks.each(function(_, i){
		if(i%2 !== 0) d3.select(this).remove();
	});


	xAxisLabel("Year/Month", (xPos + xOffset)/2, yOffset + maxPlotHeight+ 80,g);


	// Y-axis (Count)
	let y_scale = d3.scaleLinear()
		.domain([0, dataLinesAndMaxCnt.maxCount])
		.range([maxPlotHeight + yOffset, yOffset]);

	let y_axis = d3.axisLeft()
	//	.attr("transform", "translate(0,50)")
		.scale(y_scale);

	let yAxis = g.append('g')
		.call(y_axis);
	yAxis.attr("transform", "translate(" + xOffset + ",0)");
	yAxisLabel("Isolate count", 20, (maxPlotHeight/2), g, 'mgtlvl_4_yLabel');

}


function scale_mgtLvl5(dict_countsYear, dict_countsSt, yearCurr, year_3Ago, plotHeight, topNtoShow){

	let dict_scaledCounts = {}; // dict_{year} => {st|other} => count
	let maxCountSummed = 0;

	// Add 'other' if needed;
	let keysSorted = Object.keys(dict_countsSt).sort(function(a,b){return dict_countsSt[b]-dict_countsSt[a]});
	let top10Sts = keysSorted.slice(0, 10);

	for (let year in dict_countsYear){

		for (let st in dict_countsYear[year]) {
			if (!top10Sts.includes(st)){

				// Add to other
				if (!dict_countsYear[year].hasOwnProperty('other')){
					dict_countsYear[year]['other'] = 0;
				}
				dict_countsYear[year]['other'] = dict_countsYear[year]['other'] + dict_countsYear[year][st];


				delete dict_countsYear[year][st];
			}
		}
	}

	// Calculate summedMaxCount
	for (let year in dict_countsYear){

		let total = 0;
		for (let st in dict_countsYear[year]){
			total = total + dict_countsYear[year][st];
		}

		if (total > maxCountSummed){
			maxCountSummed = total;
		}
	}

	// keysSorted = Object.keys(list).sort(function(a,b){return list[a]-list[b]})
	// console.log(keysSorted);

	// Scaling the data
	for (let year = year_3Ago; year <= yearCurr; year++){
		if (!dict_countsYear.hasOwnProperty(year)){
			dict_countsYear[year] = {};
		}
		for (let st in dict_countsYear[year]){
			dict_countsYear[year][st] = dict_countsYear[year][st]/maxCountSummed * plotHeight;


		}
	}


	// console.log(dict_countsYear);
	return ({top10Sts: top10Sts, maxCountSummed: maxCountSummed});

}

function scale_mgtLvl4(dict_countsPerMonth, yearCurr, year_10Ago, top5Sts, plotHeight){

	let maxCountSummed = 0;
	let data_lines = {}; // dict_{"Year/month"} => {st} => count
	let xlabels = [];

	// Finding the max
	for (let year in dict_countsPerMonth){
		for (let month in dict_countsPerMonth[year]){
			let total = 0;
			for (let stNum in dict_countsPerMonth[year][month]){
				total = total + dict_countsPerMonth[year][month][stNum];
			}
			if (total > maxCountSummed){
				maxCountSummed = total;
			}
		}
	}

	// Scale
	for (let year=year_10Ago; year<= yearCurr; year++){
		for (let month=1; month<=12; month++){
			let xKey = year + '/' + month;
			if (!xlabels.includes(xKey)){
				xlabels.push(xKey);
			}
			for (let i=0; i<top5Sts.length; i++){


				if (!data_lines.hasOwnProperty(xKey)){
					data_lines[xKey] = {};
				}
				if (!data_lines[xKey].hasOwnProperty(top5Sts[i])){
					data_lines[xKey][top5Sts[i]] = 0;
				}

				if (dict_countsPerMonth.hasOwnProperty(year) && dict_countsPerMonth[year].hasOwnProperty(month) && dict_countsPerMonth[year][month].hasOwnProperty(top5Sts[i])){
					data_lines[xKey][top5Sts[i]] = (dict_countsPerMonth[year][month][top5Sts[i]]/maxCountSummed) * plotHeight;
				}
			}
		}
	}

	// console.log("The data lines are")
	// console.log(data_lines);
	return ({data_lines: data_lines, maxCount: maxCountSummed, xlabels: xlabels})
}

function plotChart_mgtLvl6(dict_countsPerYear, yearCurr, year_4Ago, top10Sts, chartId_stNum, numTopNSts){
	document.getElementById('chart_mgtLvl' + chartId_stNum + "_5_svg").innerHTML = '';

	let maxPlotHeight = 300;
	// let  = 4;
	let dataLinesAndMaxCnt = scale_mgtLvl6(dict_countsPerYear, yearCurr, year_4Ago, top10Sts, numTopNSts, maxPlotHeight);



	let xIncr_inner = 10;
	let xIncr_outer = 15;
	let xOffset_withinSt = 10;
	let barWidth = 15;

	let yOffset = 10;


	let theChart_svg = d3.select('#chart_mgtLvl' + chartId_stNum + '_5_svg');

	let g = theChart_svg.append('g');

	let xOffset = 60;
	let xPos = xOffset;

	let xLabels = [];

	console.log('In plotChart_mgtLvl_6');
	console.log(dataLinesAndMaxCnt);

	if (dataLinesAndMaxCnt.maxCount == 0){
		let str_noData = g.append('text')
			.attr('x', xPos + 12 + 'px')
			.attr('y', maxPlotHeight - 100)
			// .attr('dy', '.5em')
			.attr('font-size', '12px')
			// .attr('font-family', "monospace")
			.style('text-anchor', 'left')
			.text("No data to show.");

		return;
	}

	// console.log('The top N Sts is ' + numTopNSts);
	for (let i=0; i<numTopNSts; i++){
		// console.log("Tumore " + keys[k]);
		for (let year=year_4Ago; year<=yearCurr; year++){

			// console.log("Length is " + dataObj[locNames[k]].length + " " + dataObj[locNames[k]]);
			let rect = g.append('rect')
				.attr('width', barWidth)
				.attr('height', dataLinesAndMaxCnt.data_lines[top10Sts[i]][year])
				.attr('x', xPos)
				.attr('y', (yOffset + maxPlotHeight - parseFloat(dataLinesAndMaxCnt.data_lines[top10Sts[i]][year])))
				.style('fill', getRandomColor(year, year, 1))
				.style('stroke', 'black');


			xPos = xPos + barWidth + xIncr_inner;
		}

		xLabels.push('ST'+ top10Sts[i])
		xPos = xPos + xIncr_outer;
	}

	// Legend
	for (let y=year_4Ago ; y <= yearCurr; y++){
		let idx = y - year_4Ago;
		squareLegendAndText(g, (xPos + 10), (maxPlotHeight - 205 + (15 * idx)), getRandomColor(y, y, 1), (xPos+30), (maxPlotHeight - 205 + (15 * idx)) + 10, y);
	}

	// X-axis (STs)
	let numOfYears = (yearCurr - year_4Ago + 1);
	let x_scale = d3.scaleBand()
		.domain(xLabels)
		.range([xOffset, xOffset + (barWidth * numOfYears * xLabels.length) + ((numOfYears * xLabels.length-1) * xIncr_inner) + ((xLabels.length-1) * xIncr_outer)]);

	let x_axis = d3.axisBottom()
	// 	.attr("transform", "translate(0," + xOffset + ")")
		.scale(x_scale);

	let xAxis = theChart_svg.append('g')
		.call(x_axis);

	xAxis.attr("transform", "translate(" + 0 + ", " + (yOffset + maxPlotHeight) + ")")
		.selectAll("text")
		.style("text-anchor", "end")
		.attr("dx", "-.8em")
		.attr("dy", "-.5em")
		.attr("transform", "rotate(-60)");

	xAxisLabel("STs", (xPos + xOffset)/2, maxPlotHeight+ 80,g);


	// Y-axis (Count)
	let y_scale = d3.scaleLinear()
		.domain([0, dataLinesAndMaxCnt.maxCount])
		.range([yOffset + maxPlotHeight, yOffset]);

	let y_axis = d3.axisLeft()
	//	.attr("transform", "translate(0,50)")
		.scale(y_scale);

	let yAxis = g.append('g')
		.call(y_axis);
	yAxis.attr("transform", "translate(" + xOffset + ",0)");
	yAxisLabel("Isolate count", 20, (maxPlotHeight/2), g, 'chart2_yLabel');

}

function scale_mgtLvl6(dict_countsPerYear, yearCurr, year_4Ago, top10Sts, numTopNSts, plotHeight) {
	let maxCount = 0;
	let data_lines = {}; // dict_{st} => {year} => count

	// Finding the max
	for (let year=year_4Ago; year <= yearCurr; year++){
		for (let i = 0; i < numTopNSts; i++){
			if (dict_countsPerYear.hasOwnProperty(year) && dict_countsPerYear[year].hasOwnProperty(top10Sts[i])){
				let count = dict_countsPerYear[year][top10Sts[i]];

				if (count > maxCount){
					maxCount = count;
				}
			}
		}
	}



	// Scaled
	for (let j = 0; j < numTopNSts; j++){
		data_lines[top10Sts[j]] = {};
		for (let year = year_4Ago; year <= yearCurr; year++){
			let scaledCount = 0;
			if (dict_countsPerYear.hasOwnProperty(year) && dict_countsPerYear[year].hasOwnProperty(top10Sts[j])){
				scaledCount = (dict_countsPerYear[year][top10Sts[j]]/maxCount) * plotHeight;

				// console.log("The scaled count is " + maxCount + " " + year + " " + scaledCount  + " " + dict_countsPerYear[year][top10Sts[j]]);

			}
			data_lines[top10Sts[j]][year] = scaledCount;
		}
	}


	return ({data_lines: data_lines, maxCount: maxCount});
}


function plotChart_1(dataForPlot, yearStart, currYear, data_line, country, project, display_name){

	document.getElementById("chart1_svg").innerHTML = "";
	let maxPlotHeight = 300;

	d3.selectAll("#chart1_svg > *").remove();

	let theChart_svg = d3.select("#chart1_svg"); // .append('svg');
	let g = theChart_svg.append("g");
	//let g = theChart_svg.append("g");
	let computedData = scaleAndInterpolate_1(dataForPlot, yearStart, currYear, maxPlotHeight, data_line);


	let xOffset = 60;
	let xPos = xOffset + 2.5; let barWidth = 20; let xIncr = 25;
	let yOffset = 10;

	for (let i=0; i < dataForPlot.length; i++){
		let rect = g.append('rect')
			.attr("width", barWidth)
			.attr("height", parseFloat(dataForPlot[i][1]))
			.attr('x', xPos)
			.attr('y', (maxPlotHeight + yOffset - parseFloat(dataForPlot[i][1])))
			.style('fill', 'orange')
			.style('stroke', 'black');

		// console.log(dataForPlot[i][1]);

		xPos = xPos + xIncr;
	}

	theChart_svg.attr("width", (xPos + 200) + 'px');

	let x_scale = d3.scaleBand()
		.domain(computedData.keys_xAxis)
		.range([0, computedData.keys_xAxis.length * xIncr]);
	/* let y_scale = d3.scaleBand()
		.domain(yArr)
		.range([0, maxPlotHeight]); */
	let y_scale = d3.scaleLinear()
		.domain([0, computedData.maxCount])
		.range([maxPlotHeight+yOffset, yOffset]);





	theChart_svg.append("path")
      .datum(data_line)
      .attr("fill", "none")
      .attr("stroke", "red")
      .attr("stroke-width", 2)
      .attr("d", d3.line()
        .x(function(d) { return (x_scale(d[0]) + xOffset + 2.5 + barWidth/2) })
        .y(function(d) { return (maxPlotHeight + yOffset - d[1]) })
	  );

	squareLegendAndText(g, (xPos+10), (maxPlotHeight - 20), 'orange', (xPos + 30), (maxPlotHeight - 10), "Isolate count");


	g.append('line')
		.attr("x1", xPos + 10)
		.attr("x2", xPos + 20)
		.attr('y1', (maxPlotHeight - 35))
		.attr('y2', (maxPlotHeight - 35))
		.style('stroke-width', 2)
		.style('stroke', 'red');

   theChart_svg.append("text")
	 	.attr('x', xPos + 30)
		.attr('y', maxPlotHeight - 30)
		.style("text-anchor", "left")
		.text('Unique MGT9s');




	let x_axis = d3.axisBottom()
	// 	.attr("transform", "translate(0," + xOffset + ")")
		.scale(x_scale);
	let y_axis = d3.axisLeft()
	//	.attr("transform", "translate(0,50)")
		.scale(y_scale);

	let xAxis = theChart_svg.append('g')
		.call(x_axis);


	xAxis.attr("transform", "translate(" + xOffset + ", " + (maxPlotHeight + yOffset) + ")")
		.selectAll("text")
		.style("text-anchor", "end")
		.attr("dx", "-.8em")
		.attr("dy", "-.5em")
		.attr("transform", "rotate(-60)");

	 xAxisLabel("Year", (xPos + xOffset)/2, maxPlotHeight + yOffset + 50, theChart_svg);
		// .attr("id", 'g2_year');


	let yAxis = g.append('g')
		.call(y_axis);
	yAxis.attr("transform", "translate(" + xOffset + ",0)");


	yAxisLabel("Count", 0, (maxPlotHeight/2), g, 'chart1_yLabel');
	// Legend


	var svgElements = document.body.querySelectorAll('svg');
	svgElements.forEach(function(item) {
	    item.setAttribute("width", item.getBoundingClientRect().width);
	    item.setAttribute("height", item.getBoundingClientRect().height);
	    item.style.width = null;
	    item.style.height= null;
	});

	writeCaption_1(currYear, (currYear - dataForPlot.length +1), country, project, display_name);
}


///// MGT lvl charts
function getCcsForAp(tabAp, tabCcs){
	let tabCcsForanAp = [];
	for (let i=0; i<tabCcs.length; i++){
		if (tabAp['scheme_id'] == tabCcs[i]['scheme_id']){
			tabCcsForanAp.push(tabCcs[i]);
		}
	}
	return (tabCcsForanAp);
}

function handleCharts_oneMgtLvl(aTabApObj, apCcObjs, isolates, colNames, chartId_stNum, yearCurr, year_10Ago, prevApObj, nextApObj, country, table_start, figure_start, project){
	let colNum_st = getColNum(aTabApObj['table_name'] + "_st", colNames); let tableName_st = aTabApObj['display_name'];
	let colNums_cc = []; let tableNames_cc = [];

	for (let i=0; i < apCcObjs.length; i++){
		colNums_cc.push(getColNum(apCcObjs[i]['table_name'], colNames));
		tableNames_cc.push(apCcObjs[i]['display_name']);
	}

	// console.log("colNum_ap " + aTabApObj['table_name'] + " " + colNum_ap);
	// MgtLvl chart 1));
	let tableNum = (table_start + (1 * chartId_stNum));
	let countsAndSortedKeys = buildChart_mgtLvl_1(isolates, colNum_st, tableName_st, colNums_cc, tableNames_cc, chartId_stNum, country, (yearCurr - year_10Ago + 1), tableNum, project);


	// MgtLvl chart 2
	let colNum_year = getColNum('year', colNames);

	let figureNum = (figure_start + (1 * chartId_stNum));
	let countsAndTop10Sts = buildChart_mgtLvl_2(countsAndSortedKeys.theCounts.stCounts, countsAndSortedKeys.keysSorted, chartId_stNum, isolates, yearCurr, year_10Ago, colNum_year, colNum_st, country, tableName_st, figureNum, project);

	// MgtLvl chart 3
	figureNum = figureNum + 1;
	buildChart_mgtLvl_3(countsAndTop10Sts.countsPerYear, yearCurr, year_10Ago, countsAndTop10Sts.top10Sts, chartId_stNum, country, tableName_st, figureNum, project);


	// MgtLvl chart 4 (top 5 St distribution per month for past 10 years).
	figureNum = figureNum + 1;
	let colNum_month = getColNum('month', colNames);
	buildChart_mgtLvl_4(countsAndSortedKeys.keysSorted, isolates, colNum_year, colNum_month, colNum_st, yearCurr, year_10Ago, chartId_stNum, country, figureNum, project);


	// MgtLvl chart 5 (top 10 Sts of MGT level + 1 and -1)
	figureNum = figureNum + 1;
	let year_3Ago = yearCurr - 3 + 1;

	if (year_3Ago < year_10Ago){
		year_3Ago = year_10Ago;
	}

	buildChart_mgtLvl_5(countsAndSortedKeys.keysSorted[0], isolates, yearCurr, year_3Ago, colNum_st, colNum_year, prevApObj, nextApObj, colNames, chartId_stNum, country, aTabApObj, figureNum, project);

	// MgtLvl chart 6 (top 4 Sts distributed over 4 years)
	figureNum = figureNum + 1;
	let year_4Ago = yearCurr - 4 + 1;
	
	if (year_4Ago < year_10Ago){
		year_4Ago = year_10Ago;
	}
	buildChart_mgtLvl_6(countsAndTop10Sts.countsPerYear, yearCurr, year_4Ago, countsAndTop10Sts.top10Sts, chartId_stNum, country, figureNum, project);

}

function buildChart_mgtLvl_6(dict_countsPerYear, yearCurr, year_4Ago, top10Sts, chartId_stNum, country, figureNum, project){
	let numTopNSts = 4;

	if (top10Sts.length < numTopNSts){
		numTopNSts = top10Sts.length;
	}
	plotChart_mgtLvl6(dict_countsPerYear, yearCurr, year_4Ago, top10Sts, chartId_stNum, numTopNSts);

	writeCaption_mgtLvl_6(country, yearCurr, year_4Ago, chartId_stNum, numTopNSts, figureNum, project);
}

function buildChart_mgtLvl_5(topStVal, isolates, yearCurr, year_3Ago, colNum_currSt, colNum_year, prevApObj, nextApObj, colNames, chartId_stNum, country, currTableObj, figureNum, project){

	let counts = extractData_mgtLvl_5(isolates, topStVal, yearCurr, year_3Ago, colNum_currSt, colNum_year, prevApObj, nextApObj, colNames);
	let prevTableName = ""; let nextTableName = "";

	if (counts.hasOwnProperty('prevByYear') && counts.hasOwnProperty('prevBySt')){
		prevTableName = prevApObj['display_name'];
		plotChart_mgtLvl_5(counts.prevByYear, counts.prevBySt, topStVal, yearCurr, year_3Ago, chartId_stNum, 'prev', prevTableName);
	}

	if (counts.hasOwnProperty('nextByYear') && counts.hasOwnProperty('nextBySt')){
		nextTableName = nextApObj['display_name'];
		plotChart_mgtLvl_5(counts.nextByYear, counts.nextBySt, topStVal, yearCurr, year_3Ago, chartId_stNum, 'next', nextTableName);
	}

	// console.log(prevTableName + " " + nextTableName + " " + tableName_st);
	writeCaption_mgtLvl_5(country, topStVal, yearCurr, year_3Ago, chartId_stNum, prevTableName, nextTableName, currTableObj, figureNum, project);

}

function buildChart_mgtLvl_4(allStsSorted, isolates, colNum_year, colNum_month, colNum_st, yearCurr, year_10Ago, chartId_stNum, country, figureNum, project){
	let top5Sts = allStsSorted.slice(0, 5);

	let dict_countsPerMonth = extractData_mgtLvl_4(isolates, top5Sts, colNum_year, colNum_month, colNum_st, yearCurr, year_10Ago);

	plotChart_mgtLvl_4(dict_countsPerMonth, top5Sts, yearCurr, year_10Ago, chartId_stNum);

	writeCaption_mgtLvl_4(country, chartId_stNum, yearCurr, year_10Ago, figureNum, project);
}


function buildChart_mgtLvl_3(dict_countsPerYear, yearCurr, year_10Ago, top10Sts, chartId_stNum, country, tableName_st, figureNum, project){
	let dict_scaledCounts = scaleByMax_mgtLvl_3(dict_countsPerYear, yearCurr, year_10Ago, top10Sts)





	// (prev. line graph) plotChart_mgtLvl_2(chartId_stNum, 2, dict_scaledCounts, yearCurr, year_10Ago, top10Sts, 'Scaled count')

	// (prev. line graph) writeCaption_mgtLvl_3(country, chartId_stNum, yearCurr, year_10Ago, tableName_st, figureNum, project);


	plotChart_mgtLvl_3_v2(chartId_stNum, 2, dict_countsPerYear, yearCurr, year_10Ago, top10Sts, 'Count');

	writeCaption_mgtLvl_3_v2(country, chartId_stNum, yearCurr, year_10Ago, tableName_st, (figureNum), project);


}

function scaleByMax_mgtLvl_3(dict_countsPerYear, yearCurr, year_10Ago, top10Sts){
	let dict_scaledCounts = {};
	let dict_maxCountPerYear = {} // dict_{year} => maxVal

	for (let i =0; i < top10Sts.length; i++){
		let maxVal = 0;
		for (let year = year_10Ago+1; year <= yearCurr; year++){
			if (dict_countsPerYear[year].hasOwnProperty(top10Sts[i]) && dict_countsPerYear[year][top10Sts[i]] > maxVal){
				maxVal = dict_countsPerYear[year][top10Sts[i]];
			}
		}
		dict_maxCountPerYear[top10Sts[i]] = maxVal;
	}

	// Just scaling the same object.
	for (let year = year_10Ago + 1; year <= yearCurr; year++){
		dict_scaledCounts[year] = {};
		for (let i =0; i< top10Sts.length; i++){
			if (dict_countsPerYear.hasOwnProperty(year) && dict_countsPerYear[year].hasOwnProperty(top10Sts[i])){


				dict_scaledCounts[year][top10Sts[i]] = dict_countsPerYear[year][top10Sts[i]]/dict_maxCountPerYear[top10Sts[i]];
			}
		}
	}

	return (dict_scaledCounts)
}


function buildChart_mgtLvl_2(dict_stCounts, keysSorted, chartId_stNum, isolates, yearCurr, year_10Ago, colNum_year, colNum_st, country, tableName_st, figureNum, project){


	let top10Sts = keysSorted.slice(0, 10);


	let dict_countsPerYear = extractData_mgtLvl_2(isolates, top10Sts, colNum_year, colNum_st, yearCurr, year_10Ago);

	plotChart_mgtLvl_2_v2(chartId_stNum, 1, dict_countsPerYear, yearCurr, year_10Ago, top10Sts, 'Count');

	writeCaption_mgtLvl_2_v2(country, chartId_stNum, yearCurr, year_10Ago, tableName_st, (figureNum), project);


	// (old line graph) plotChart_mgtLvl_2(chartId_stNum, 1, dict_countsPerYear, yearCurr, year_10Ago, top10Sts, 'Count');



	// (old line graph) writeCaption_mgtLvl_2(country, chartId_stNum, yearCurr, year_10Ago, tableName_st, figureNum, project);
	/*
	let svgId = 'chart_mgtLvl' + chartId_stNum + "_1_svg";
	document.getElementById(svgId).innerHTML = "";
	let maxPlotHeight = 300;

	let theChart_svg = d3.select("#" + svgId);
	let g = theChart_svg.append("g");
	*/

	return ({countsPerYear: dict_countsPerYear, top10Sts: top10Sts})
}


function plotChart_mgtLvl_3_v2(chartId_stNum, mgtLvl_chartNum, dict_countsPerYear, yearCurr, year_10Ago, top10Sts, ylabel){

	document.getElementById('chart_mgtLvl' + chartId_stNum + '_' + mgtLvl_chartNum + '_v2_svg').innerHTML = '';

	let maxPlotHeight = 300;
	let yOffset = 10;
	let xOffset = 60;
	let spacing = 50;

	let barWidth = 20;
	let xIncr_inner = 5;


	let computedData = convertAndScale_mgtLvl2_v3(dict_countsPerYear, year_10Ago, yearCurr, top10Sts, maxPlotHeight);
	let data_lines = computedData.data_lines;


	let theChart_svg = d3.select('#' + 'chart_mgtLvl' + chartId_stNum + '_' + mgtLvl_chartNum + '_v2_svg');

	let g = theChart_svg.append('g');

	let xPos = xOffset;
	let xLabels = []

	for (let year = year_10Ago; year <= yearCurr; year++){
		xLabels.push(year);

		let yPos = maxPlotHeight + yOffset;
		for (let j = 0; j < top10Sts.length; j++){

			let rect = g.append('rect')
				.attr('width', barWidth)
				.attr('height', parseFloat(data_lines[year][top10Sts[j]]))
				.attr('x', xPos)
				.attr('y', (yPos - parseFloat(data_lines[year][top10Sts[j]])))
				.style('fill', getRandomColor(top10Sts[j],(top10Sts[j] + 5), 1))
				.style('stroke', getRandomColor(top10Sts[j],(top10Sts[j] + 5), 1));

			yPos = yPos - parseFloat(data_lines[year][top10Sts[j]]);
		}

		xPos = xPos + barWidth + xIncr_inner;
	}
	theChart_svg.attr('width', (xPos + 200) + 'px');

	// Legend
	for (let i=0; i < top10Sts.length; i++){
		squareLegendAndText(g, (xPos + 10), (maxPlotHeight - 205 + (15 * i)), getRandomColor(top10Sts[i], (top10Sts[i] + 5), 1), (xPos+30), (maxPlotHeight - 205 + (15 * i)) + 10, ('ST' + top10Sts[i]));
	}


	// X-axis (STs)
	let x_scale = d3.scaleBand()
		.domain(xLabels)
		.range([xOffset, xOffset + (xLabels.length * barWidth) + ((xLabels.length -1) * xIncr_inner) ]);


	let x_axis = d3.axisBottom()
	// 	.attr("transform", "translate(0," + xOffset + ")")
		.scale(x_scale);


	let xAxis = theChart_svg.append('g')
		.call(x_axis);



	xAxis.attr("transform", "translate(" + 0 + ", " + yOffset + maxPlotHeight + ")")
		.selectAll("text")
		.style("text-anchor", "end")
		.attr("dx", "-.8em")
		.attr("dy", "-.5em")
		.attr("transform", "rotate(-60)");

	let ticks = xAxis.attr("transform", "translate(" + 0 + ", " + (yOffset + maxPlotHeight) + ")")
		.selectAll("text");

	xAxisLabel("Year", (xPos + xOffset)/2, yOffset + maxPlotHeight+ 60,g);


	// Y-axis (Count)
	let y_scale = d3.scaleLinear()
		.domain([0, computedData.maxCount])
		.range([yOffset + maxPlotHeight, yOffset]);

	let y_axis = d3.axisLeft()
	//	.attr("transform", "translate(0,50)")
		.scale(y_scale);

	let yAxis = g.append('g')
		.call(y_axis);
	yAxis.attr("transform", "translate(" + xOffset + ",0)");
	yAxisLabel("Percentage isolates", 20, yOffset + (maxPlotHeight/2), g, 'mgtlvl_5_yLabel');


	// Chart title
	// xAxisLabel(title, (xPos + xOffset)/2, (height_offset/2),g);

}


function plotChart_mgtLvl_2_v2(chartId_stNum, mgtLvl_chartNum, dict_countsPerYear, yearCurr, year_10Ago, top10Sts, ylabel){

	document.getElementById('chart_mgtLvl' + chartId_stNum + '_' + mgtLvl_chartNum + '_v2_svg').innerHTML = '';

	let maxPlotHeight = 300;
	let yOffset = 10;
	let xOffset = 60;
	let spacing = 50;

	let barWidth = 20;
	let xIncr_inner = 5;


	let computedData = convertAndScale_mgtLvl2_v2(dict_countsPerYear, year_10Ago, yearCurr, top10Sts, maxPlotHeight);
	let data_lines = computedData.data_lines;

	// console.log('In plotChart_mgtLvl_2_v2');
	// console.log(data_lines);

	let theChart_svg = d3.select('#' + 'chart_mgtLvl' + chartId_stNum + '_' + mgtLvl_chartNum + '_v2_svg');

	let g = theChart_svg.append('g');

	let xPos = xOffset;
	let xLabels = []

	for (let year = year_10Ago; year <= yearCurr; year++){
		xLabels.push(year);

		let yPos = maxPlotHeight + yOffset;
		for (let j = 0; j < top10Sts.length; j++){

			let rect = g.append('rect')
				.attr('width', barWidth)
				.attr('height', parseFloat(data_lines[year][top10Sts[j]]))
				.attr('x', xPos)
				.attr('y', (yPos - parseFloat(data_lines[year][top10Sts[j]])))
				.style('fill', getRandomColor(top10Sts[j],(top10Sts[j] + 5), 1))
				.style('stroke', getRandomColor(top10Sts[j],(top10Sts[j] + 5), 1));

			yPos = yPos - parseFloat(data_lines[year][top10Sts[j]]);
		}

		xPos = xPos + barWidth + xIncr_inner;
	}
	theChart_svg.attr('width', (xPos + 200) + 'px');

	// Legend
	for (let i=0; i < top10Sts.length; i++){
		squareLegendAndText(g, (xPos + 10), (maxPlotHeight - 205 + (15 * i)), getRandomColor(top10Sts[i], (top10Sts[i] + 5), 1), (xPos+30), (maxPlotHeight - 205 + (15 * i)) + 10, ('ST' + top10Sts[i]));
	}


	// X-axis (STs)
	let x_scale = d3.scaleBand()
		.domain(xLabels)
		.range([xOffset, xOffset + (xLabels.length * barWidth) + ((xLabels.length -1) * xIncr_inner) ]);


	let x_axis = d3.axisBottom()
	// 	.attr("transform", "translate(0," + xOffset + ")")
		.scale(x_scale);


	let xAxis = theChart_svg.append('g')
		.call(x_axis);



	xAxis.attr("transform", "translate(" + 0 + ", " + yOffset + maxPlotHeight + ")")
		.selectAll("text")
		.style("text-anchor", "end")
		.attr("dx", "-.8em")
		.attr("dy", "-.5em")
		.attr("transform", "rotate(-60)");

	let ticks = xAxis.attr("transform", "translate(" + 0 + ", " + (yOffset + maxPlotHeight) + ")")
		.selectAll("text");

	xAxisLabel("Year", (xPos + xOffset)/2, yOffset + maxPlotHeight+ 60,g);


	// Y-axis (Count)
	let y_scale = d3.scaleLinear()
		.domain([0, computedData.maxCount])
		.range([yOffset + maxPlotHeight, yOffset]);

	let y_axis = d3.axisLeft()
	//	.attr("transform", "translate(0,50)")
		.scale(y_scale);

	let yAxis = g.append('g')
		.call(y_axis);
	yAxis.attr("transform", "translate(" + xOffset + ",0)");
	yAxisLabel("Isolate count", 20, yOffset + (maxPlotHeight/2), g, 'mgtlvl_5_yLabel');


	// Chart title
	// xAxisLabel(title, (xPos + xOffset)/2, (height_offset/2),g);

}

function plotChart_mgtLvl_2(chartId_stNum, mgtLvl_chartNum, dict_countsPerYear, yearCurr, year_10Ago, top10Sts, ylabel){
	// console.log("The chartId_stNum is " + chartId_stNum);
	document.getElementById('chart_mgtLvl' + chartId_stNum + '_' + mgtLvl_chartNum + '_svg').innerHTML = '';
	let maxPlotHeight = 300;
	let yOffset = 10;
	let xOffset = 60;
	let spacing = 50;

	let computedData = convertAndScale_mgtLvl2(dict_countsPerYear, year_10Ago, yearCurr, top10Sts, maxPlotHeight);
	let data_lines = computedData.data_lines;

	let theChart_svg = d3.select('#chart_mgtLvl' + chartId_stNum + '_' + mgtLvl_chartNum + '_svg');

	let g = theChart_svg.append('g');

	for (let i=0; i<top10Sts.length; i++){
		for (let j=1; j<data_lines[top10Sts[i]].length; j++){
			g.append('line')
				.attr("x1", (xOffset + ((j-1) * spacing)))
				.attr("x2", (xOffset + (j * spacing)))
				.attr('y1', (yOffset + maxPlotHeight) - data_lines[top10Sts[i]][j-1][1])// (maxPlotHeight - 35))
				.attr('y2', (yOffset + maxPlotHeight) - data_lines[top10Sts[i]][j][1])// (maxPlotHeight - 35))
				.style('stroke-width', 2)
				.style('stroke', getRandomColor(i, i, 1));
		}
	}

	// X-axis
	let keys_xAxis = numberRange(year_10Ago+1, yearCurr+1);
	// console.log("It is liberating ");
	// console.log(keys_xAxis);
	let x_scale = d3.scaleLinear()
		.domain([year_10Ago, yearCurr])
		.range([0, (keys_xAxis.length * spacing) - spacing]);

	let x_axis = d3.axisBottom()
	// 	.attr("transform", "translate(0," + xOffset + ")")
		.scale(x_scale).tickFormat(d3.format("d"));

	let xAxis = theChart_svg.append('g')
		.call(x_axis);

	xAxis.attr("transform", "translate(" + xOffset + ", " + (maxPlotHeight + yOffset) + ")")
		.selectAll("text")
		.style("text-anchor", "end")
		.attr("dx", "-.8em")
		.attr("dy", "-.5em")
		.attr("transform", "rotate(-60)");

	xAxisLabel("Year", ((keys_xAxis.length * spacing) - spacing + xOffset)/2, maxPlotHeight+ 50 + yOffset, theChart_svg);

	// Y-axis
	let y_scale = d3.scaleLinear()
		.domain([0, computedData.maxCount])
		.range([maxPlotHeight+ yOffset, yOffset]);

	let y_axis = d3.axisLeft()
	//	.attr("transform", "translate(0,50)")
		.scale(y_scale);

	let yAxis = g.append('g')
		.call(y_axis);
	yAxis.attr("transform", "translate(" + xOffset + ",0)");

	yAxisLabel(ylabel, 0, (maxPlotHeight/2), g, 'chart1_yLabel');

	// Legend
	for (let i=0; i<top10Sts.length; i++){
		g.append('line')
			.attr("x1", (keys_xAxis.length * spacing) + 10)
			.attr("x2", (keys_xAxis.length * spacing) + 20)
			.attr('y1', (maxPlotHeight - 205 + (15 * i)))
			.attr('y2', (maxPlotHeight - 205 + (15 * i)))
			.style('stroke-width', 2)
			.style('stroke', getRandomColor(i, i, 1));

		 theChart_svg.append("text")
			.attr('x', (keys_xAxis.length * spacing) + 30)
			.attr('y', maxPlotHeight - 200 + (15 * i))
			.style("text-anchor", "left")
			.text('ST ' + top10Sts[i]);
	}


	// Applying the styles to SVG.
	var svgElements = document.body.querySelectorAll('svg');
	svgElements.forEach(function(item) {
		item.setAttribute("width", item.getBoundingClientRect().width);
		item.setAttribute("height", item.getBoundingClientRect().height);
		item.style.width = null;
		item.style.height= null;
	});

}

function numberRange (start, end) {
  return new Array(end - start).fill().map((d, i) => i + start);
}


function convertAndScale_mgtLvl2_v2(dict_countsPerYear, year_10Ago, yearCurr, top10Sts, plotHeight){
	let data_lines = {}; // dict_{year} => {st} => cnt
	let summedMaxCount = 0;


	for (let i= year_10Ago; i <= yearCurr; i++){
		let totalPerYear = 0;
		for (let j=0; j< top10Sts.length; j++){
			if (dict_countsPerYear.hasOwnProperty(i) && dict_countsPerYear[i].hasOwnProperty(top10Sts[j])){
				totalPerYear = totalPerYear + dict_countsPerYear[i][top10Sts[j]];
			}

			if (totalPerYear > summedMaxCount){
				summedMaxCount = totalPerYear;
			}
		}
	}

	for (let year = year_10Ago; year <= yearCurr; year++){
		data_lines[year] = [];
		for (let j = 0; j < top10Sts.length; j++){
			data_lines[year][top10Sts[j]] = 0;
			let scaledCount = 0;
			if (dict_countsPerYear.hasOwnProperty(year) && dict_countsPerYear[year].hasOwnProperty(top10Sts[j])){
				scaledCount = (dict_countsPerYear[year][top10Sts[j]]/summedMaxCount) * plotHeight;
			}
			data_lines[year][top10Sts[j]] = scaledCount;
		}
	}


	return ({data_lines: data_lines, maxCount: summedMaxCount});
}



function convertAndScale_mgtLvl2_v3(dict_countsPerYear, year_10Ago, yearCurr, top10Sts, plotHeight){
	let data_lines = {}; // dict_{year} => {st} => cnt


	for (let year= year_10Ago; year <= yearCurr; year++){
		let total = 0;
		for (let j=0; j< top10Sts.length; j++){
			if (dict_countsPerYear.hasOwnProperty(year) && dict_countsPerYear[year].hasOwnProperty(top10Sts[j])){
				total = total + dict_countsPerYear[year][top10Sts[j]];
			}
		}

		data_lines[year] = [];
		for (let j=0; j< top10Sts.length; j++){
			let scaledCount = 0;
			if (dict_countsPerYear.hasOwnProperty(year) && dict_countsPerYear[year].hasOwnProperty(top10Sts[j]) && total > 0){
				scaledCount = (dict_countsPerYear[year][top10Sts[j]]/total) * plotHeight;
			}

			data_lines[year][top10Sts[j]] = scaledCount;
		}
	}


	return ({data_lines: data_lines, maxCount: 100});
}


function convertAndScale_mgtLvl2(dict_countsPerYear, year_10Ago, yearCurr, top10Sts, plotHeight){
	let data_lines = {}; // dict_{st} => [[year, count], [yeear, count], ...]
	let maxCount = 0;

	for (let j = 0; j < top10Sts.length; j++){
		data_lines[top10Sts[j]] = [];
		for (let i = year_10Ago + 1; i <= yearCurr; i++){
			let count = 0;
			if (dict_countsPerYear.hasOwnProperty(i) && dict_countsPerYear[i].hasOwnProperty(top10Sts[j])){
				count = dict_countsPerYear[i][top10Sts[j]];

				if (count > maxCount){
					maxCount = count;
				}
			}
			// data_lines[top10Sts[j]].push([i, count]);
		}
	}

	for (let j = 0; j < top10Sts.length; j++){
		data_lines[top10Sts[j]] = [];
		for (let i = year_10Ago + 1; i <= yearCurr; i++){
			let scaledCount = 0;
			if (dict_countsPerYear.hasOwnProperty(i) && dict_countsPerYear[i].hasOwnProperty(top10Sts[j])){
				scaledCount = (dict_countsPerYear[i][top10Sts[j]]/maxCount) * plotHeight;

			}
			data_lines[top10Sts[j]].push([i, scaledCount]);
		}
	}


	return ({data_lines: data_lines, maxCount: maxCount});
}
function extractData_mgtLvl_5(isolates, topStVal, yearCurr, year_3Ago, colNum_currSt, colNum_year, prevApObj, nextApObj, colNames){

	let toRet = {}

	if (prevApObj.hasOwnProperty('table_name')){
		let prevColNum = getColNum(prevApObj['table_name']+"_st", colNames);
		let res = getCountsForOneSide(isolates, topStVal, yearCurr, year_3Ago, colNum_currSt, colNum_year, prevColNum);

		toRet.prevByYear = res.dict_countsByYear;
		toRet.prevBySt = res.dict_countsSt;
	}

	if (nextApObj.hasOwnProperty('table_name')){
		let nextColNum = getColNum(nextApObj['table_name']+"_st", colNames);
		let res = getCountsForOneSide(isolates, topStVal, yearCurr, year_3Ago, colNum_currSt, colNum_year, nextColNum);

		toRet.nextByYear = res.dict_countsByYear;
		toRet.nextBySt = res.dict_countsSt;
	}

/*
	getCountsForOneSide(isolates, topStVal, yearCurr, year_3Ago, colNum_currSt, colNum_year,)

	let dict_prevSts = {}; // dict_{year} => {st} => cnt
	let dict_nextSts = {}; // dict_{year} => {st} => cnt

	let colNum_prevSt = getColNum(, colNames);
	let colNum_nextSt = getColNum(colNames);

	for (let i=0; i<isolates.length; i++){
		let currYear = parseInt(isolates[i][colNum_year]);
		let thisSt = String(isolates[i][colNum_currSt]);

		if (currYear && thisSt && thisSt == topStVal && currYear > parseInt(year_10Ago)){

		}
	}
	*/

	return (toRet);
}

function getCountsForOneSide(isolates, topStVal, yearCurr, year_3Ago, colNum_currSt, colNum_year, colNumSt){

	let dict_countsByYear = {}; // dict_{year} => {st} => cnt
	let dict_countsSt = {}; // dict_{st} => cnt (this gives the overall count);

	for (let i=0; i<isolates.length; i++){
		let currSt = String(isolates[i][colNum_currSt]);

		if (currSt && currSt == topStVal){

			let currYear = parseInt(isolates[i][colNum_year]);
			let thisSt = String(isolates[i][colNumSt]);

			if (currYear >= year_3Ago && thisSt){

				// Add to dict
				if (!dict_countsByYear.hasOwnProperty(currYear)){
					dict_countsByYear[currYear] = {};
				}
				if (!dict_countsByYear[currYear].hasOwnProperty(thisSt)){
					dict_countsByYear[currYear][thisSt] = 0;
				}
				dict_countsByYear[currYear][thisSt] = dict_countsByYear[currYear][thisSt] + 1;

				if (!dict_countsSt.hasOwnProperty(thisSt)){
					dict_countsSt[thisSt] = 0;
				}
				dict_countsSt[thisSt] = dict_countsSt[thisSt] + 1;

			}
		}

	}

	return ({dict_countsByYear: dict_countsByYear, dict_countsSt: dict_countsSt});
}

function extractData_mgtLvl_4(isolates, top5Sts, colNum_year, colNum_month, colNum_st, yearCurr, year_10Ago){
	let dict_countsPerYearMth = {}; // dict_{year} => {month} => {st} => count;

	for (let i=0; i<isolates.length; i++){
		let currYear = parseInt(isolates[i][colNum_year]);
		let currMonth = parseInt(isolates[i][colNum_month]);

		if (currYear && currMonth && currYear >= parseInt(year_10Ago) && top5Sts.includes(String(isolates[i][colNum_st]))){
			// console.log("Year: " + currYear + " " + currMonth);

			if (!dict_countsPerYearMth.hasOwnProperty(currYear)){
				dict_countsPerYearMth[currYear] = {};
			}

			if (!dict_countsPerYearMth[currYear].hasOwnProperty(currMonth)){
				dict_countsPerYearMth[currYear][currMonth] = {};
			}

			if (!dict_countsPerYearMth[currYear][currMonth].hasOwnProperty(String(isolates[i][colNum_st]))){
				dict_countsPerYearMth[currYear][currMonth][String(isolates[i][colNum_st])] = 0;
			}

			dict_countsPerYearMth[currYear][currMonth][String(isolates[i][colNum_st])] = dict_countsPerYearMth[currYear][currMonth][String(isolates[i][colNum_st])] + 1;



			// if (!dict_countsPerYearMth[currYear][])
		}

	}

	// console.log("The counts per year and month are ");
	// console.log(dict_countsPerYearMth);

	return (dict_countsPerYearMth);
}

function extractData_mgtLvl_2(isolates, top10Sts, colNum_year, colNum_st, yearCurr, year_10Ago){
	let dict_countsPerYear = {}; // dict_{year} => {st} => count;


	for (let i = year_10Ago; i <= yearCurr; i++){
		dict_countsPerYear[i] = {};

		for (let j = 0; j < top10Sts.length; j++){
			dict_countsPerYear[i][top10Sts[j]] = 0;
		}
	}


	for (let i=0; i<isolates.length; i++){

		let currYear = parseInt(isolates[i][colNum_year])
		if (currYear >= parseInt(year_10Ago)){
			if (top10Sts.includes(String(isolates[i][colNum_st]))){
				// Add to dict
				dict_countsPerYear[currYear][String(isolates[i][colNum_st])] = dict_countsPerYear[currYear][String(isolates[i][colNum_st])] + 1;
			}
		}
	}

	return (dict_countsPerYear);

}


function buildChart_mgtLvl_1(isolates, colNum_ap, tableName_st, colNums_cc, tableNames_cc, chartId_stNum, country, numYears, chartNum, project){
	let theCounts = extractData_mgtLvl1(isolates, colNum_ap, colNums_cc);

	let keysSorted = trimAndGetTop10(theCounts.stCounts); // keys sorted descending order;


	plotChart_mgtLvl1(keysSorted, theCounts, tableName_st, tableNames_cc, chartId_stNum, country, project);

	writeCaption_mgtLvl_1(country, chartId_stNum, numYears, tableName_st, 10, chartNum, project);

	return ({theCounts: theCounts, keysSorted: keysSorted});
}



function extractData_mgtLvl1(isolates, colNum_st, colNums_cc){

	let dict_stCounts = {}; // dict_{st} => count;
	// let dict_ccCounts = {}; // dict_{ccColNum} => ccVal => count;
	let dict_ccForSt = {} // dict_{st} => {ccPos} => [cc1, cc2, cc3...];



	for (let i=0; i<isolates.length; i++){
		let stVal = isolates[i][colNum_st];
		if (!dict_stCounts.hasOwnProperty(stVal)){
			dict_stCounts[stVal] = 0;
		}

		dict_stCounts[stVal] = dict_stCounts[stVal] + 1;

		if (!dict_ccForSt.hasOwnProperty(stVal)){
			dict_ccForSt[stVal] = {};
			for (let c=0; c<colNums_cc.length; c++){
				dict_ccForSt[stVal][c] = [];
			}
		}

		// For each cc;
		for (let c=0; c<colNums_cc.length; c++){
			let ccVal = isolates[i][colNums_cc[c]];

			if (!dict_ccForSt[stVal][c].includes(ccVal)){
				dict_ccForSt[stVal][c].push(ccVal);
			}
		}
	}

	return ({stCounts: dict_stCounts, ccForSt: dict_ccForSt});
}


function trimAndGetTop10(dict_stCounts){
	if (dict_stCounts.hasOwnProperty('null')){
		delete dict_stCounts.null;
	}

	// var list = {"you": 100, "me": 75, "foo": 116, "bar": 15};
	let keysSorted = Object.keys(dict_stCounts).sort(function(a,b){return dict_stCounts[b]-dict_stCounts[a]})
	// console.log(keysSorted);

	return keysSorted;
}

////////////////////////////// Captions
function getProjCountryStr(country, project){

	let innerHTML = "";

	if (String(country) != 'null'){
		innerHTML = innerHTML + country;
	}

	if (String(country) != 'null' && String(project) != 'null'){
		innerHTML = innerHTML + " and ";
	}

	if (String(project) != 'null'){
		innerHTML = innerHTML + project;
	}

	return innerHTML
}

function writeCaption_1(currYear, startYear, country, project, display_name){
	// Caption
	// console.log("The project value is |" + project + "|");
	let innerHTML = "<b>Figure 1</b>: Annual case rates in "

	innerHTML = innerHTML + getProjCountryStr(country, project);

	innerHTML = innerHTML + " in the past " + (currYear - startYear + 1) + " years (" + startYear + "-" + currYear + "). Overlaid on the isolate counts, are the number of unique " + display_name + "s within this set. (Same number of " + display_name + "s indicate high clonality).";



	document.getElementById('chart1_p').innerHTML = innerHTML;
}

function writeCaption_2(currYear, yearStart, country, project){
	// Caption

	let innerHTML = "<b>Figure 2</b>: Annual number of isolates for each "

	if (String(country) != 'null'){
		innerHTML = innerHTML + 'state';
	}
	else{
		innerHTML = innerHTML + 'country';
	}

	innerHTML = innerHTML + " in ";
	innerHTML = innerHTML + getProjCountryStr(country, project);

	innerHTML = innerHTML + " in the past " + (currYear - yearStart + 1) + " years (" + yearStart + "-" + currYear + ").";

	document.getElementById('chart2_p').innerHTML = innerHTML;
}

function writeCaption_3(yearStart, yearCurr, country, project){
	let innerHTML = "<b>Table 1</b>: The number of isolates and MGT STs in the MGT database for data from ";

	innerHTML = innerHTML + getProjCountryStr(country, project);

	innerHTML = innerHTML + " over the past " + (yearCurr - yearStart + 1) + " years. The brackets indicate the number of STs which have newly emerged in that year.";

	document.getElementById('chart3_p').innerHTML = innerHTML;
}

function writeCaption_4(country, project){
	let innerHTML = "<b>Figure 3</b>: Number of isolates from ";

	innerHTML = innerHTML + getProjCountryStr(country, project);

	document.getElementById('chart4_p').innerHTML =  innerHTML + " assigned to each ST at every MGT level. White indicates STs assigned to a single ST.";
}

function writeCaption_mgtLvl_1(country, chartId_stNum, numYears, tableName_st, numTopSts, chartNum, project){

	let innerHTML = "<b>Table " + chartNum + "</b>: Distribution of top " + numTopSts + " ";

	innerHTML = innerHTML + getProjCountryStr(country, project);

	document.getElementById('chart_mgtLvl' + chartId_stNum + '_0_p').innerHTML = innerHTML + " " + tableName_st + "s (past " + numYears + " years).";
}

function writeCaption_mgtLvl_2(country, chartId_stNum, yearCurr, yearStart, tableName_st, figureNum, project){

	let innerHTML =  "<b>Figure " + figureNum + "</b>: Major " + tableName_st + "s in ";

	innerHTML = innerHTML + getProjCountryStr(country, project);

	document.getElementById('chart_mgtLvl' + chartId_stNum + '_1_p').innerHTML = innerHTML + " in the past " + (yearCurr - yearStart + 1) + " years (" + yearStart + "-" + yearCurr + ")";
}

function writeCaption_mgtLvl_2_v2(country, chartId_stNum, yearCurr, yearStart, tableName_st, figureNum, project){

	let innerHTML =  "<b>Figure " + figureNum + "</b>: Major " + tableName_st + "s in ";

	innerHTML = innerHTML + getProjCountryStr(country, project);

	document.getElementById('chart_mgtLvl' + chartId_stNum + '_1_v2_p').innerHTML = innerHTML + " in the past " + (yearCurr - yearStart + 1) + " years (" + yearStart + "-" + yearCurr + ") as a bar chart.";
}

function writeCaption_mgtLvl_3(country, chartId_stNum, yearCurr, yearStart, tableName_st, figureNum, project){
	let innerHTML = "<b>Figure " + figureNum + "</b>: Major " + tableName_st + "s in ";

	innerHTML = innerHTML + getProjCountryStr(country, project);

	document.getElementById('chart_mgtLvl' + chartId_stNum + '_2_p').innerHTML = innerHTML + " over the past " + (yearCurr - yearStart + 1) + " years (" + yearStart + " - " + yearCurr + "), where the isolate count for each ST has been scaled by the maximum in that year. This enables visualising newly emerging STs. ";
}

function writeCaption_mgtLvl_3_v2(country, chartId_stNum, yearCurr, yearStart, tableName_st, figureNum, project){
	let innerHTML = "<b>Figure " + figureNum + "</b>: Major " + tableName_st + "s in ";

	innerHTML = innerHTML + getProjCountryStr(country, project);

	document.getElementById('chart_mgtLvl' + chartId_stNum + '_2_v2_p').innerHTML = innerHTML + " over the past " + (yearCurr - yearStart + 1) + " years (" + yearStart + " - " + yearCurr + "), where the isolate count for each ST has been scaled as a percentage of the total isolates in that particular year. This enables visualising newly emerging STs.  ";
}


function writeCaption_mgtLvl_4(country, chartId_stNum, yearCurr, yearStart, figureNum, project){
	let url = window.location.href;
	let orgName = window.location.pathname.split('/')[1];

	let re = new RegExp(orgName + ".*$");
	url = url.replace(re, '');

	url = url + orgName + "/" + 'isolate-list?year__gte=' + yearStart + '&year__lte=' + yearCurr
	if (String(country) != 'null'){
		url = url + '&country=' + country;
	}
	if (String(project) != 'null'){
		url = url + '&project=' + project;
	}


	// console.log(url);

	// let innerHTML =

	document.getElementById('chart_mgtLvl' + chartId_stNum + '_3_p').innerHTML = "<b>Figure " + figureNum + "</b>: Case distributions over each month for the past " + (yearCurr - yearStart + 1) + " years (when month data is available). Explore the <a href='" + url + "' target='_blank'> complete set </a> interactively on the MGT website. (Once on the webpage, click 'Graphical view' followed by load data). ";
}

function writeCaption_mgtLvl_5(country, topStVal, yearCurr, year_3Ago, chartId_stNum, prevTableName, nextTableName, currTabObj, figureNum, project){

	let innerHTML = 'Top 10 ';
	let isAnd = false;

	if (prevTableName != ""){
		innerHTML = innerHTML + prevTableName + "s"
		isAnd = true
	}

	if (nextTableName != ""){
		if (isAnd == true) {
			innerHTML = innerHTML + " and "
		}

		innerHTML = innerHTML + nextTableName + "s"
	}

	innerHTML = innerHTML + " over the past " + (yearCurr - year_3Ago + 1) + ' years, for ' + currTabObj['display_name'] + topStVal + " (the most prevalent " +  currTabObj['display_name'] + " in "


	innerHTML = innerHTML + getProjCountryStr(country, project);

	innerHTML = innerHTML + " over the past 10 years). Other STs are shown in white.";


	let url = window.location.href;
	let orgName = window.location.pathname.split('/')[1];

	let re = new RegExp(orgName + ".*$");
	url = url.replace(re, '');

	url = url + orgName + "/" + 'isolate-list?year__gte=' + year_3Ago + '&year__lte=' + yearCurr + "&" + currTabObj['table_name']+ "_st=" + topStVal ;

	// console.log(url);

	if (String(country) != "null"){
		url = url  + '&country=' + country;
	}
	if (String(project) != 'null'){
		url = url + '&project=' + project;
	}

	innerHTML = innerHTML + " These data, as well as distributions of other MGT levels can also be explored interactively on the <a href='" + url + "' target='_blank'>MGT website</a>. (Once on the webpage, click 'Graphical view' followed by load data). "

	document.getElementById('chart_mgtLvl' + chartId_stNum + '_4_p').innerHTML = '<b>Figure ' + figureNum + '</b>: ' + innerHTML;
}


function writeCaption_mgtLvl_6(country, yearCurr, year_4Ago, chartId_stNum, numTopNSts, figureNum, project){

	let innerHTML = '<b>Figure ' + figureNum + "</b>: Distribution of isolates in the top " + numTopNSts + ' STs found in ';

	innerHTML = innerHTML + getProjCountryStr(country, project);

	document.getElementById('chart_mgtLvl' + chartId_stNum + "_5_p").innerHTML =  innerHTML + ' in the past ' + (yearCurr - year_4Ago + 1) + " years."

	 // where top ' + numTopNSts + ' STs were calculated within the past ' + (yearCurr - year_4Ago + 1) + " years.";
}

/////////////////////////////// Download report
function downloadTheReport_4(){

	var htmlContent = [document.getElementById('div_report').innerHTML];
	console.log(htmlContent);
	var bl = new Blob(htmlContent, {type: "text/html"});
	var a = document.createElement("a");

	a.href = URL.createObjectURL(bl);
	a.download = "MGT_report.html";
	a.hidden = true;
	document.body.appendChild(a);
	a.innerHTML = "something random - nobody will see this, it doesn't matter what you put here";
	a.click();
}


function downloadTheReport_3(){
	var element = document.getElementById('div_report');
	html2pdf(element);
}

function downloadTheReport_3_(){
	// $("#btnSave2").click(function() {
		let doc = new jspdf.jsPDF;
		let yPos = 0;
		let pageHeight= doc.internal.pageSize.height;




		let thePromises = [];
		thePromises.push(addCanvasToDoc(doc, "chart1"));
		thePromises.push(addCanvasToDoc(doc, "chart2"));
		thePromises.push(addCanvasToDoc(doc, "chart3"));
		thePromises.push(addCanvasToDoc(doc, "chart4"));

		let divCharts_mgtLvl = document.querySelectorAll('div [id^="div_chart_mgtLvl"]');


		divCharts_mgtLvl.forEach(function(aMgtLvl, aMgtLvl_i) {
			// console.log(aMgtLvl.id);
			thePromises.push(addCanvasToDoc(doc, aMgtLvl.id));
		});



		Promise.all(thePromises).then(function(data){
			yPos = 0;
			document.querySelectorAll("canvas").forEach(function(aCanvas, aCanvas_I){

				var imgData = aCanvas.toDataURL('image/png').replace(/.*,/, '');
				// var doc = new jspdf.jsPDF;

				var imgHeight = aCanvas.height*208/aCanvas.width;

				if ((yPos + imgHeight) > pageHeight){
					yPos = 0;
					doc.addPage();
				}

				doc.addImage(imgData, 0, yPos, 208, imgHeight);

				yPos = yPos + imgHeight + 20;
				// console.log(data);
				// doc.save("result.pdf");

				if (aCanvas_I == document.querySelectorAll("canvas").length - 1 ){
					doc.save('result.pdf');
				}
			});
			// doc.save();
		});
		/*

		html2canvas(document.body.getElementsByTagName('div').chart2, {logging: true, scrollX: -window.scrollX, scrollY: -window.scrollY}).then(function(canvas){
		   console.log("The canvas is ");
		   console.log(canvas);
		   document.body.appendChild(canvas);

		   var imgData = canvas.toDataURL('image/png').replace(/.*,/, '');
		   // var doc = new jspdf.jsPDF;
		   var imgHeight = canvas.height*208/canvas.width;
		   doc.addImage(imgData, 0, yPos, 208, imgHeight);

		   doc.save("result.pdf");

		   // saveAs(canvas.toDataURL('image/png'), 'MGT_report.png');

		 // }
		});
		// });


	 /*
	 function saveAs(uri, filename) {
	   var link = document.createElement('a');
	   if (typeof link.download === 'string') {
		 link.href = uri;
		 link.download = filename;

		 //Firefox requires the link to be in the body
		 document.body.appendChild(link);

		 //simulate click
		 link.click();

		 //remove the link when done
		 document.body.removeChild(link);
	   } else {
		 window.open(uri);
	   }
	 }
	 */
}

function addCanvasToDoc(doc, chartId){
	return new Promise(function (resolve, reject){
		html2canvas(document.body.getElementsByTagName('div')[chartId], {logging: true, scrollX: -window.scrollX, scrollY: -window.scrollY}).then(function(canvas){
		   // console.log("The chartId is " + chartId);
		   document.body.appendChild(canvas);

		   /* var imgData = canvas.toDataURL('image/png').replace(/.*,/, '');
		   // var doc = new jspdf.jsPDF;
		   var imgHeight = canvas.height*208/canvas.width;
		   doc.addImage(imgData, 0, yPos, 208, imgHeight);

		   yPos = yPos + imgHeight;
		   */



		   // doc.save("result.pdf");
		   // saveAs(canvas.toDataURL('image/png'), 'MGT_report.png');

		   resolve()
		 // }
		});
	});
}

function downloadTheReport_2(){
	$(document).ready(function() {
	/* create an svg drawing */

		//create a canvas
		let canvas = document.createElement('canvas');
		canvas.id = 'canvas'
		document.body.appendChild(canvas);
		canvas.width = 500;
		canvas.height = 500;
		let context = canvas.getContext('2d');

			// take the svg and convert it to a canvas
		let temp_img = new Image();
		temp_img.src = "data:image/svg+xml;base64,"+btoa($("#chart1_svg").html());

		// console.log(temp_img);
		//temp_img2 = new Image();
		//temp_img2.src = "data:image/svg+xml;base64,"+btoa($("#svg2").html());

		//add the images
		let base_image = new Image();
		context = canvas.getContext('2d');
		context.drawImage(temp_img,0,0);

		// console.log(context);

		//var doc = new jsPDF('p', 'mm');
		var doc = new jspdf.jsPDF('p','pt','a4');
		html2canvas($("#canvas"), {
		  onrendered: function(canvas) {
		    var imgData = canvas.toDataURL('image/png');
		    // $("#canvas").hide();
		    doc.addImage(imgData, 'PNG', 10, 10, 200, 200);
			// console.log(imgData);
			/*
		    doc.addHTML(document.getElementById('div1'), 0, 0, function() {
		    	console.log('callback');
		      doc.save('sampler-file.pdf');
		    });
			*/
		    doc.save('sample-file.pdf');
		  }
		});
		});
}


function downloadTheReport_1(){
	var html = d3.select("#chart1_svg")
		.attr("version", 1.1)
		.attr("xmlns", "http://www.w3.org/2000/svg")
		.node().parentNode.innerHTML;

	//console.log(html);

	var image = new Image();
	image.src = 'data:image/svg+xml;base64,'+ btoa(html);
	console.log(image.src);
	// var image = '<img src="'+imgsrc+'">';
	/*
	d3.select("#svgdataurl").html(img);
	*/

	//image.onload = function() {
	  var canvas = document.createElement('canvas');
	  canvas.width = 200;
	  canvas.height = 200;
	  var context = canvas.getContext('2d');
	  context.drawImage(image, 0, 0);

	  var a = document.createElement('a');
	  a.download = "image.png";
	  a.href = canvas.toDataURL('image/svg+xml');
	  document.body.appendChild(a);

	  console.log("Coronary artery dissection repair");
	  console.log(a);
	  a.click();
	//}
}

function downloadTheReport(){
	var doc = new jspdf.jsPDF();


	let svg_chart1 = document.getElementById("chart1_svg");

	let svgData = new XMLSerializer().serializeToString(chart1_svg);

	// if (svg)
	/*
	let svgData = new XMLSerializer().serializeToString(chart1_svg);

	let svg_str = svgData.replace(/\r?\n|\r/g, '').trim();

// var context = canvas.getContext('2d');

	console.log(svg_str);

	// context.clearRect(0, 0, canvas.width, canvas.height);
	var canvas = document.createElement('canvas');
	// const ctx = canvas.getContext('2d');

	// canvg.Canvg.fromString(ctx, svg_str);

	canvg(canvas, svgData);

	var imgData = canvas.toDataURL('image/png');




	document.getElementById('div_report').appendChild(canvas);
	// console.log("The canvas");
	// console.log(canvas);

	// console.log("Image data");
	// console.log(imgData);

	// Generate PDF
	// var doc = new jsPDF('p', 'pt', 'a4');

	var html = d3.select("#chart1_svg")
		.attr("version", 1.1)
		.attr("xmlns", "http://www.w3.org/2000/svg")
		.node().parentNode.innerHTML;

	//console.log(html);
	var imgsrc = 'data:image/svg+xml;base64,'+ btoa(html);
	var img = '<img src="'+imgsrc+'">';

	d3.select("#svgdataurl").html(img);
	*/
	doc.addSvgAsImage(svgData, 40, 40, 100, 300);
	doc.save('test.pdf');



}


////////////////////////// AUX
function setupDivs(tabAps){
	// Div style == chart_mgtLvl{stNum}_{chartNum};
	let div_mgtLvl_charts = document.getElementById('chart_mgtLvls');
	//div_mgtLvl_charts.innerHTML = "";




	// Number of charts per level;
	let totalNumChartPerLvl = 5;
	for (let i=0; i<tabAps.length; i++){
		let newH2 = document.getElementById('mgtLvl_h2_' + i);
		newH2.innerHTML = ""; 
		newH2.innerHTML = tabAps[i]['display_name'] + newH2.innerHTML;
		newH2.innerHTML = newH2.innerHTML.replace("ST", '');


		let navIdx = document.getElementById('mgtLvl_idx_' + i);
		navIdx.innerHTML = tabAps[i]['display_name'];
		navIdx.innerHTML = navIdx.innerHTML.replace('ST', '');

		// div_mgtLvl_charts.append(newH2);
		/*
		for (let chartNum = 0; chartNum < totalNumChartPerLvl; chartNum++){
			let newDiv = document.createElement('div');
			newDiv.id = 'chart_mgtLvl' + i + '_1' + chartNum;
			newDiv.setAttribute('height', '600');
			newDiv.setAttribute('width', '400');
			newDiv.style.display = 'block';
			if (chartNum == 0){
				// Append a table and text;
				let newTable = document.createElement('table');
				newTable.id = newDiv.id + "_table";
				newTable.className = "table table-sm table-bordered";

				let newP = document.createElement('p');
				newP.id = newDiv.id + "_p";
				newDiv.append(newTable);
				newDiv.append(newP);

				div_mgtLvl_charts.append(newDiv);
			}

			else if (chartNum == 1){
				let newSvg = document.createElement('svg');
				newSvg.id = newDiv.id + "_svg";
				newSvg.className = "chart_mgtLvl";
				newSvg.style = "border: 1px solid;";
				newSvg.style.height = "400px";
				let newP = document.createElement('p');
				newP.id = newDiv.id + "_p";
				newDiv.append(newSvg);
				newDiv.append(newP);

				document.getElementById('div_report').append(newDiv)
			}


		}
		*/

	}


}


function getTotalStCount(stCounts){
	let total = 0;

	Object.keys(stCounts).forEach(function(stVal, stVal_i){
		total = total + stCounts[stVal];
	});

	return total;
}

function xAxisLabel(displayText, xPos, yPos, nodeToAppendTo){
	nodeToAppendTo.append("text")
	   .attr('x', xPos)
	   .attr('y', yPos)
	   .style("text-anchor", "middle")
	   .text(displayText)
	   .attr("class", "xAxisText");
}

function yAxisLabel(displayText, xPos, yPos, nodeToAppendTo, theId){
	nodeToAppendTo.append('text').style('text-anchor', 'middle')
		.attr('dy', '.75em')
		.attr('x', yPos * -1)
		.attr('transform', 'rotate(-90)')
		.text(displayText)
		.attr('id', theId);


	// .attr('transform', (d,i)=>{
    //    return 'translate( '+xScale(i)+' , '+220+'),'+ 'rotate(45)';})

	//console.log("Hello world");
	//console.log(a);
		// .attr('x', xPos)
		//.attr('y', yPos)
		//.selectAll('text')
		//.attr("transform", function (d) {
	   //return "rotate(-30)";});
		// .attr('transform', 'rotate(-90)');
		// .attr("transform", "translate(-" + xPos + ", -" + yPos +")" );
}


function squareLegendAndText(nodeToAppendTo, rect_xPos, rect_yPos, fillColor, text_xPos, text_yPos, textLabel){

	nodeToAppendTo.append('rect')
		.attr("width", 10)
		.attr("height", 10)
		.attr("x", rect_xPos)
		.attr('y', rect_yPos)
		.style('fill', fillColor)
		.style('stroke', 'black');

	nodeToAppendTo.append("text")
	   .attr('x', text_xPos)
	   .attr('y', text_yPos)
	   .style("text-anchor", "left")
	   .text(textLabel);
}


function scale_2(dataObj, maxPlotHeight){

	let maxCount = 0;

	// Finding the max
	for (let key in dataObj){
		dataObj[key].forEach(function(item, i){
			if (item > maxCount){
				maxCount = item;
			}
		});
	}

	// console.log("The max count is " + maxCount);

	// Scaling
	for (let key in dataObj){
		for (let i=0; i<dataObj[key].length; i++){
			dataObj[key][i] = (dataObj[key][i]/maxCount) * maxPlotHeight;
		}
	}


	return maxCount;
}


function transformTheData_2(dataArr, currYear, yearStart){

	// dataArr - year, count, country
	let dataObj = {};

	let locs = [];
	// let years = [];


	// Getting all possible locs
	for (let i =0; i< dataArr.length; i++){
		// console.log(dataArr[i][0] + " " + dataArr[i][2]);
		if (!dataArr[i][2] || dataArr[i][2] === null || dataArr[i][2].match("null") || dataArr[i][2].match("None") || dataArr[i][2].match(/^[\s]*$/)){
			// console.log("And this one: " + dataArr[i][2]);
			dataArr[i][2] = 'Unknown';
			// console.log("And this one: now: " + dataArr[i][2]);
		}
		if (!locs.includes(dataArr[i][2])){
			locs.push(dataArr[i][2]);
		}
	}

	// Creating the dataObj structure
	for (let i=0; i<locs.length; i++){
		let countsArr = Array.apply(null, Array(currYear - yearStart + 1)).map(function (x, i) { return 0; });
		dataObj[locs[i]] = countsArr;
	}

	//  Filling in the counts in the dataObj
	for (let i=0; i< dataArr.length; i++){
		let idx = parseInt(dataArr[i][0]) - parseInt(yearStart);
		dataObj[dataArr[i][2]][idx] = dataObj[dataArr[i][2]][idx] + dataArr[i][1];
		// console.log("idx: " + idx  + " count:" + dataArr[i][1] + " " + dataArr[i][1] + " " + yearStart);
	}

	// console.log(locs);
	// console.log(dataObj);
	// console.log(years);
	return (dataObj);
}

function scaleAndInterpolate_1(data_bar, yearStart, currYear, plotHeight, data_line){

	// Sorting
	let sortedBar = data_bar.sort(function(a, b) {
		return b[0] - a[0];
	});

	let sortedLine = data_line.sort(function(a, b) {
		return b[0] - a[0];
	});

	// Interpolation (and finding the max)
	let maxCount = 0;
	let year = currYear;
	let yearDiff = currYear - yearStart + 1;
	for (let i=0; i < yearDiff; i++){
		if (sortedBar.length <= i || sortedBar[i][0] !== year){
			// console.log('toAddyear in this position ' + sortedArray[i][0] + " " + year);
			sortedBar.splice(i, 0, [year, 0]);
		}
		if (sortedBar[i][1] > maxCount){
			maxCount = sortedBar[i][1];
		}
		year = year - 1;
	}

	year = currYear;
	for (let i=0; i < yearDiff; i++){
		if (sortedLine.length <= i || sortedLine[i][0] !== year){
			// console.log('toAddyear in this position ' + sortedArray[i][0] + " " + year);
			sortedLine.splice(i, 0, [year, 0]);
		}
		if (sortedLine[i][1] > maxCount){
			maxCount = sortedLine[i][1];
		}
		year = year - 1;
	}


	data_bar = sortedBar.reverse();
	data_line = sortedLine.reverse();


	// Scaling
	// console.log("The maxcount is " + maxCount + " " + plotHeight);

	let keys_xAxis = [];

	for (let i=0; i < sortedBar.length; i++){
		sortedBar[i][1] = (sortedBar[i][1]/maxCount) * plotHeight;
		sortedBar[i][1] = sortedBar[i][1].toFixed(2);

		keys_xAxis.push(sortedBar[i][0]);
	}

	for (let i=0; i < sortedLine.length; i++){
		sortedLine[i][1] = (sortedLine[i][1]/maxCount) * plotHeight;
		sortedLine[i][1] = sortedLine[i][1].toFixed(2);

		// keys_xAxis.push(sortedLine[i][0]);
	}


	return ({keys_xAxis: keys_xAxis, maxCount: maxCount});
}
