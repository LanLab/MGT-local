export {getInitDataG3, g3_switchStCcOdc};

import {ajaxCall} from './packageAndSend.js';
import {drawButtons_init, switchClassesForMultipleBtns, checkAndSendToPlotLvl3} from './graph_timeOrLocStCount.js';
import {getRandomColor} from './generateColors.js';

const G3_lvl1_btnsDivSt = "g3_btnDiv_ap";
const G3_lvl1_btnsDivCc = "g3_btnDiv_cc";
const G3_lvl1_btnsDivOdc = "g3_btnDiv_odc";
const G3_lvl1_btn_st = "g3_btn_st";
const G3_lvl1_btn_cc = "g3_btn_cc";
const G3_lvl1_btn_odc = "g3_btn_odc";

const Table_st = "table_st";
const Table_cc = "table_cc";
const Table_odc = "table_odc";


const G3_tbl_svgPtn = "g3_svg_";
const G3_tbl_isoCntPtn = "g3_isoCnt_";
const G3_tbl_stCntPtn = "g3_stCnt_";
const G3_tbl_hovCnt = "g3_hovCnt_";
const G3_tbl_selCnt = "g3_selCnt_";
const G3_lvl3_btnPtn = "g3_lvl3_btn_";

const Singleton = 'Singletons'; 
// const G3_tbl_clearSel = "g3_clearSel_";

var dict_filterList = {}; // dict_{tn} => [stval1, val2, ... valN]

function getInitDataG3(tabAps, tabCcsOdcs, org){
  // console.log(tabAps);
//   console.log(tabCcsOdcs);

  $("#loading_g3").show();

  // drawButtons_init(tabAps, tabCcsOdcs, G3_lvl1_btnsDivSt, G3_lvl1_btnsDivCc, G3_lvl1_btnsDivOdc, G3_lvl3_btnPtn);
  setupFilterList(tabAps, Table_st);
  setupFilterList(tabCcsOdcs, Table_cc, 1);
  setupFilterList(tabCcsOdcs, Table_odc, 2);

  setupTable(Table_st, tabAps);
  setupTable(Table_cc, tabCcsOdcs, 1);
  setupTable(Table_odc, tabCcsOdcs, 2);


	ajaxCall('/' + org + '/timeStCount', {}, handleData_mgtBreakdown);

	document.getElementById('btn_g3_getInitData').remove();

}

function clearFilterList(btnId, respData, tableId){

  let key = btnId.replace(G3_lvl3_btnPtn, '');
  dict_filterList[key] = [];

  let lvl1Choice = G3_lvl1_btn_st;
  if (tableId == Table_cc){
    lvl1Choice = G3_lvl1_btn_cc;
  }
  else if (tableId == Table_odc){
    lvl1Choice = G3_lvl1_btn_odc;
  }

  // Send for replot.
  g3_transformAndSendForPlot(respData, lvl1Choice, key, tableId);
  updateOtherChartsInTbl(tableId, key, respData, lvl1Choice);

  // Update selected count
  document.getElementById(G3_tbl_selCnt + key).innerHTML = 0;
}

function setupFilterList(tabAps, tableId, tableNum){
  let str_stCcOdc = "_st";
  if (tableId == Table_cc){
    str_stCcOdc = '_cc';
  }
  else if (tableId == Table_odc){
    str_stCcOdc = '_odc';
  }

  tabAps.forEach(function(tblObj, tblObj_i){
    if (!tableNum || tableNum == tblObj.display_table){
      dict_filterList[tblObj.table_name + str_stCcOdc] = [];
    }
  });

}

function setupTable(tableId, tabAps, tableNum){
  let str_stCcOdc = "_st";
  if (tableId == Table_cc){
    str_stCcOdc = '_cc';
  }
  else if (tableId == Table_odc){
    str_stCcOdc = '_odc';
  }



  let tbl = document.getElementById(tableId);

  // Row: MGT heading
  let rowNum = 0;
  let row = tbl.insertRow(rowNum++);

  let cell = row.insertCell(0);

  let colCounter = 1;
  for (let i=0; i<tabAps.length; i++){
    if (!tableNum || tableNum == tabAps[i].display_table){
      cell = row.insertCell(colCounter++);
      cell.innerHTML = "<b class='speHeading'>" + tabAps[i].display_name + "</b>";
    }
  }


  // Row: Isolate count
  row = tbl.insertRow(rowNum++);
  cell = row.insertCell(0);
  cell.innerHTML = '<i>Isolate count</i>';
  colCounter = 1;
  for (let i=0; i<tabAps.length; i++){
    if (!tableNum || tableNum == tabAps[i].display_table){
      cell = row.insertCell(colCounter++);
      cell.id = G3_tbl_isoCntPtn + tabAps[i].table_name + str_stCcOdc;
      // cell.innerHTML = tabAps[i].display_name;
    }
  }


  // Row: ST count
  row = tbl.insertRow(rowNum++);
  cell = row.insertCell(0);
  cell.innerHTML = '<i>ST count</i>';
  colCounter = 1;
  for (let i=0; i<tabAps.length; i++){
    if (!tableNum || tableNum == tabAps[i].display_table){
      cell = row.insertCell(colCounter++);
      cell.id = G3_tbl_stCntPtn + tabAps[i].table_name + str_stCcOdc;
      // cell.innerHTML = tabAps[i].display_name;
    }
  }


  // Row: SVGs
  row = tbl.insertRow(rowNum++);
  cell = row.insertCell(0);
  // cell.innerHTML = 'ST count';
  colCounter = 1;
  for (let i=0; i<tabAps.length; i++){
    if (!tableNum || tableNum == tabAps[i].display_table){
      cell = row.insertCell(colCounter++);

      var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("height", "450");
      svg.setAttribute('id', G3_tbl_svgPtn + tabAps[i].table_name + str_stCcOdc);
      cell.append(svg);
      // Append svg in here.
    }
  }

  // Row: Hovered count
  row = tbl.insertRow(rowNum++);
  cell = row.insertCell(0);
  cell.innerHTML = '<i>Hovered identifier (isolate count)</i>';
  colCounter = 1;
  for (let i=0; i<tabAps.length; i++){
    if (!tableNum || tableNum == tabAps[i].display_table){
      cell = row.insertCell(colCounter++);
      cell.innerHTML = '';
      cell.id = G3_tbl_hovCnt + tabAps[i].table_name + str_stCcOdc;
      // Append svg in here.
    }
  }

  // Row: Selected count
  row = tbl.insertRow(rowNum++);
  cell = row.insertCell(0);
  cell.innerHTML = '<i>Selected isolate count</i>';
  colCounter = 1;
  for (let i=0; i<tabAps.length; i++){
    if (!tableNum || tableNum == tabAps[i].display_table){
      cell = row.insertCell(colCounter++);
      cell.innerHTML = 0;
      cell.id = G3_tbl_selCnt + tabAps[i].table_name + str_stCcOdc;
      // Append svg in here.
    }
  }

  // Row: clear selection
  row = tbl.insertRow(rowNum++);
  cell = row.insertCell(0);
  // cell.innerHTML = 'Selected count';
  colCounter = 1;
  for (let i=0; i<tabAps.length; i++){
    if (!tableNum || tableNum == tabAps[i].display_table){
      cell = row.insertCell(colCounter++);
      cell.innerHTML = "<button id=\"" + G3_lvl3_btnPtn + tabAps[i].table_name + str_stCcOdc + "\" class=\"btn btn-sm btn-default-outline-spe\">Clear selection</button>";
      cell.id = G3_tbl_selCnt + tabAps[i].table_name + str_stCcOdc;
      // Append svg in here.
    }
  }
}

function addSingletonProp(dict_counts){
  // console.log("The dict_counts, in addSingletonProp are");
  // console.log(dict_counts);

  let dict_countsSingletons = {}; // dict_{st|singleton} => count 
  let arr_singletons = []; 

  for (let key in dict_counts){
    if (dict_counts[key] == 1){ // Add to singleton
      if (!dict_countsSingletons.hasOwnProperty(Singleton)){
        dict_countsSingletons[Singleton] = 0; 
      }
      dict_countsSingletons[Singleton] = dict_countsSingletons[Singleton] + dict_counts[key];  
      arr_singletons.push(key); 
    }
    else { // Add as normal ST val
      dict_countsSingletons[key] = dict_counts[key]; 
    }
  }
  // console.log(dict_countsSingletons); 
  return ({dict_countSingletons: dict_countsSingletons, arr_singletons: arr_singletons}); 
}

function handleData_mgtBreakdown(respData){
  let parsedRespData = JSON.parse(respData);

	let response = [];
	if (!parsedRespData.hasOwnProperty('data')){

		console.log(response);
    return ("No data to show. ");
	}
  response = parsedRespData.data;

  g3_attachEventsToBtns_init(response, Table_st);
  g3_attachEventsToBtns_init(response, Table_cc);
  g3_attachEventsToBtns_init(response, Table_odc);

  // g3_plotLvl1_stCcOdc(G3_lvl1_btn_st);

  // g3_switchStCcOdc(G3_lvl1_btn_st);

  $("#loading_g3").hide();
  $("#btnsAndPlot_g3").show();
  $("#mgtLvlBtns_g3").show();
  $("#" + G3_lvl1_btn_st).click();
}

function g3_attachEventsToBtns_init(respData, tableId){

    let btns = document.getElementById(tableId).querySelectorAll('[id^="' + G3_lvl3_btnPtn + '"]');

  	btns.forEach(function(aBtn, aBtn_i){
  		aBtn.onclick = function(){
  			// g3_handleBtnsLvl3(aBtn.id, respData, tableId);
        clearFilterList(aBtn.id, respData, tableId);
      };
      // aBtn.click();
      g3_handleBtnsLvl3(aBtn.id, respData, tableId);
    });

}

function g3_switchStCcOdc(inputClickedBtn){

  let clickedBtn = inputClickedBtn;
  let otherBtns = [];

  let divToShow = '';
  let divsToHide = [];

  if (typeof inputClickedBtn == "undefined" || inputClickedBtn == undefined || inputClickedBtn == null || inputClickedBtn == ''){
    return;
  }

  // console.log("how about over here...?");
  let btnOthers = [G3_lvl1_btn_st, G3_lvl1_btn_cc, G3_lvl1_btn_odc];
  let tablesToHide = [Table_st, Table_cc, Table_odc];

  if (inputClickedBtn == G3_lvl1_btn_st){
    $("#" + Table_st).show();
    $("#" + Table_cc).hide(); $("#" + Table_odc).hide();

    removeClassFromBtn(G3_lvl1_btn_st, "btn-default-outline-spe");
    addClassToBtn(G3_lvl1_btn_st, "btn-default-spe");

    removeClassFromBtn(G3_lvl1_btn_cc, "btn-default-spe");
    addClassToBtn(G3_lvl1_btn_cc, "btn-default-outline-spe");

    removeClassFromBtn(G3_lvl1_btn_odc, "btn-default-spe");
    addClassToBtn(G3_lvl1_btn_odc, "btn-default-outline-spe");
  }
  else if (inputClickedBtn == G3_lvl1_btn_cc){
    $("#" + Table_cc).show();
    $("#" + Table_st).hide(); $("#" + Table_odc).hide();

    removeClassFromBtn(G3_lvl1_btn_cc, "btn-default-outline-spe");
    addClassToBtn(G3_lvl1_btn_cc, "btn-default-spe");

    removeClassFromBtn(G3_lvl1_btn_st, "btn-default-spe");
    addClassToBtn(G3_lvl1_btn_st, "btn-default-outline-spe");

    removeClassFromBtn(G3_lvl1_btn_odc, "btn-default-spe");
    addClassToBtn(G3_lvl1_btn_odc, "btn-default-outline-spe");
  }
  else if (inputClickedBtn == G3_lvl1_btn_odc){
    $("#" + Table_odc).show();
    $("#" + Table_st).hide(); $("#" + Table_cc).hide();

    removeClassFromBtn(G3_lvl1_btn_odc, "btn-default-outline-spe");
    addClassToBtn(G3_lvl1_btn_odc, "btn-default-spe");

    removeClassFromBtn(G3_lvl1_btn_st, "btn-default-spe");
    addClassToBtn(G3_lvl1_btn_st, "btn-default-outline-spe");

    removeClassFromBtn(G3_lvl1_btn_cc, "btn-default-spe");
    addClassToBtn(G3_lvl1_btn_cc, "btn-default-outline-spe");
  }



}

function g3_handleBtnsLvl3(inputClickedBtnId, respData, tableId){


  addClassToBtn(inputClickedBtnId, 'btn-default-spe');
  removeClassFromBtn(inputClickedBtnId, 'btn-default-outline-spe');

	// 1. transform the data.
	// 2. plot the transformed data.


	let lvlChoices = g3_readThe2LvlChoices(inputClickedBtnId);

  g3_transformAndSendForPlot(respData, lvlChoices.lvl1, lvlChoices.lvl2, tableId);
}

function g3_readThe2LvlChoices(inputClickedBtnId){

	let lvlChoices = {lvl1: G3_lvl1_btn_st, lvl2: ''};
	let lvl2BtnDiv = G3_lvl1_btnsDivSt;


	if (document.getElementById(G3_lvl1_btn_cc).classList.contains('btn-default-spe')){
		lvlChoices.lvl1 = G3_lvl1_btn_cc;
    lvl2BtnDiv = G3_lvl1_btnsDivCc;
	}
	else if (document.getElementById(G3_lvl1_btn_odc).classList.contains('btn-default-spe')) {
		lvlChoices.lvl1 = G3_lvl1_btn_odc;
    lvl2BtnDiv = G3_lvl1_btnsDivOdc;
	}

  /*
	let lvl2Btns = document.getElementById(lvl2BtnDiv).querySelectorAll("button");

	lvl2Btns.forEach(function(aBtn, aBtn_i){
		if (aBtn.classList.contains('btn-default-spe')){
			lvlChoices.lvl2 = aBtn.id;
		}
	});
  */
	// console.log(lvlChoices);

  lvlChoices.lvl2 = inputClickedBtnId.replace(G3_lvl3_btnPtn, '');

	return (lvlChoices);
}


function g3_transformAndSendForPlot(respData, lvl1_choice, lvl2_choice, tableId){

	// console.log("Lvl choices: " + lvl1_choice + " " + lvl2_choice + " " );


  let colNumsAndTn = getColNameAndNum(lvl1_choice, lvl2_choice, respData[0], tableId);


	let dict_counts = g3_doTheTransformation(respData, colNumsAndTn.countCol, colNumsAndTn.colNums, lvl1_choice, colNumsAndTn.otherColNums, tableId);

  let asSingletons = addSingletonProp(dict_counts);
  // console.log(lvl1_choice + " " + tableId);
  // console.log(dict_counts);
  /*
	g2_convertToMergedStFormat(dict_.data_forPlot);

	g2_doThePlot_timeAndLocStCnt(dict_.data_forPlot, colBy_choice);
  */


  let strToAppend = 'ST';
  if (tableId == Table_cc){
    strToAppend = 'CC';
  }
  else if (tableId == Table_odc){
    strToAppend = 'ODC';
  }
  
  // console.log(asSingletons); 
  g3_doThePlot(asSingletons.dict_countSingletons, asSingletons.arr_singletons, colNumsAndTn.tn, strToAppend, tableId, respData, lvl1_choice);
}

function updateOtherChartsInTbl(tableId, currTn, respData, lvl1Choice){
  let btns = document.getElementById(tableId).querySelectorAll('[id^="' + G3_lvl3_btnPtn + '"]');

  btns.forEach(function(aBtn, aBtn_i){
    let btnTn = aBtn.id.replace(G3_lvl3_btnPtn, '');

    if (btnTn != currTn){
      // console.log(btnTn);
      g3_transformAndSendForPlot(respData, lvl1Choice, btnTn, tableId);
    }
  });

}

function g3_doThePlot(dict_counts, arr_singletonKeys, tn, strToAppend, tableId, respData, lvl1Choice){

  let toolTip = d3.select("#btnsAndPlot_g3")
    .append("div")
    .attr('id', 'g1_tooltip')
      .attr("class", "tooltip")
    .style('background', 'beige')
    .style('border-radius', '8px')
    .style('padding', '2px')
    .style('border-color', '#cabfd9')
    .style('border-style', 'solid')
    .style('text-align', 'center');


  // Check if dict is empty.

  let sortedKeys = sortByIsoCount(dict_counts);
  let summedCount = getMaxCount(dict_counts);

  document.getElementById(G3_tbl_isoCntPtn + tn).innerHTML = summedCount;
  document.getElementById(G3_tbl_stCntPtn + tn).innerHTML = Object.keys(dict_counts).length;


  // document.getElementById("g3_svg_ap2_0").innerHTML = "";
  let theChart_svg = d3.select("#" + G3_tbl_svgPtn + tn);
  theChart_svg.selectAll("*").remove();

  let g = theChart_svg.append("g");

  let maxPlotHeight = 400; let barX_width = 30;
  let yPos = 0;

  sortedKeys.forEach(function(key, key_i){
    let scaledHeight = (dict_counts[key]/summedCount) * maxPlotHeight;
    let bar = g.append('rect')
      .attr('width', barX_width)
      .attr('height', scaledHeight)
      .attr('x', 0)
      .attr('y', yPos)
      // .attr('class', 'g3NotActive')
      .style('fill', function(){
        if (key == Singleton){
          return 'white'
        }
        return getRandomColor(key, 0, 0.5).replace("rgba", "rgb").replace("\,0.5\)", "\)");
      })
      .style('fill-opacity', function(){
        if(isInFilterList(tn, key) == true){
          return 1;
        }
        else {
          return 0.5;
        }
      })
      .style('stroke', function(){
        // if (key == Singleton && ) 
        if (key == Singleton && isInFilterList(tn, key)){
          return 'red';
        }
        else if (key == Singleton){
          return 'white'; 
        }
        else if (isInFilterList(tn, key)){
          return 'black';
        }

        return getRandomColor(key, 0, 0.5); //.replace("rgba", "rgb").replace("\,0.5\)", "\)");
      })
      .style('stroke-width', 1)
      .style('stroke-opacity', 0.5);

      if (isInFilterList(tn, key) == true){
        bar.attr('class', 'g3Active');
      }

      yPos = yPos + scaledHeight;


      bar.data([key])
        .on("mouseenter", function(d){
          d3.select(this)
            // .classed('active', true);
            // .style('opacity', 1)
            .style('stroke-width', 5);


          toolTip.transition()
            ///.duration(200)
            .style("opacity", 1);
            toolTip.html(function(){
              if (key == Singleton){
                return "<b>" + key + "</b> <br> Count: "+ dict_counts[key]  
              }
              else {
                return "<b>" + strToAppend  + key + "</b> <br> Count: "+ dict_counts[key]   
              }
            })
            .style("left", event.pageX + "px")
            .style("top", event.pageY + "px");

            if (key != Singleton){
              document.getElementById(G3_tbl_hovCnt+tn).innerHTML = strToAppend  + key +  ' (' + dict_counts[key] + ')';
            }
            else {
              document.getElementById(G3_tbl_hovCnt+tn).innerHTML = key +  ' (' + dict_counts[key] + ')';
            }
            
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
          document.getElementById(G3_tbl_hovCnt+tn).innerHTML = "";
        })
        .on("click", function(d){
          let rect = d3.select(this);
          if (!this.classList.contains('g3Active')){
            d3.select(this)
              .style('fill-opacity', 1);

            if (key == Singleton){
              d3.select(this)
              .style('stroke', 'red');
            }
            else {
              d3.select(this)
              .style('stroke', 'black');
            }
            this.classList.add('g3Active');
            document.getElementById(G3_tbl_selCnt+tn).innerHTML = parseInt(document.getElementById(G3_tbl_selCnt+tn).innerHTML) + dict_counts[key];
            
            addRmFromFilterList('add', tn, key, arr_singletonKeys);
            
            updateOtherChartsInTbl(tableId, tn, respData, lvl1Choice);
          }
          else {
            d3.select(this)
              .style('fill-opacity', 0.5);
            
            if (key == Singleton){
              d3.select(this)
              .style('stroke', 'white');
            }
            else{
              d3.select(this)
              .style('stroke', getRandomColor(key, 0, 0.5));
            }

            this.classList.remove('g3Active');
            document.getElementById(G3_tbl_selCnt+tn).innerHTML = parseInt(document.getElementById(G3_tbl_selCnt+tn).innerHTML) - dict_counts[key];

            addRmFromFilterList('rm', tn, key, arr_singletonKeys);
            updateOtherChartsInTbl(tableId, tn, respData, lvl1Choice);
          }
        });
  });

  // console.log("The filter list is ");
  // console.log(dict_filterList);
}

function isInFilterList(tn, stVal){

  if (dict_filterList[tn].includes(stVal)){
    return true;
  }
  return false;
}

function addRmFromFilterList(fn, key, val, arr_singletonKeys){

  if (fn == 'add'){
    if (val == Singleton){
      // Add singleton keys 
      arr_singletonKeys.forEach(function(singletonKey){
        if (!dict_filterList[key].includes(singletonKey)){
          dict_filterList[key].push(singletonKey);
        }        
      })
    }
    // else {
      if (!dict_filterList[key].includes(val)){ // Add normal keys
        dict_filterList[key].push(val);
      }
    // }
  }

  if (fn == 'rm'){
    if (val == Singleton){
      // Add singleton keys 
      arr_singletonKeys.forEach(function(singletonKey){
        let idx = dict_filterList[key].indexOf(singletonKey);
        if (idx != -1){
          dict_filterList[key].splice(idx, 1);   
        }    
      })
    }
   //  else {
      if (dict_filterList[key].includes(val)){
        let idx = dict_filterList[key].indexOf(val);
        if (idx != -1){
          dict_filterList[key].splice(idx, 1);
        }
      }
    // }
  }
}


function getMaxCount(dict_counts){
  let maxValue = 0;

  Object.values(dict_counts).forEach(function(value, value_i){
    maxValue = maxValue + value;
    /* if (value > maxValue){
      maxValue = value;
    } */
  });


  return (maxValue);
}

function sortByIsoCount(dict_counts){
  let keys = Object.keys(dict_counts);

  let sortedKeys = keys.sort(function(a,b){
    return dict_counts[b] - dict_counts[a];
  });

  if (sortedKeys.includes(Singleton)){
    let idx = sortedKeys.indexOf(Singleton);
    sortedKeys.splice(idx, 1); 
    sortedKeys.push(Singleton); 
  }
  // console.log(keys)
  // console.log(sortedKeys)

  return (sortedKeys);
}

function g3_doTheTransformation(respData, countColNum, colNums, lvl1_choice, otherColNums, tableId){

  let dict_counts = {}; // dict_{st} => cnt (number of isolates);

  respData.forEach(function(arrVals, arrVals_i){
    if (arrVals_i != 0){
      if (tableId == Table_st){
        if (arrVals[colNums[0]] != null){

          // Check other values
          if (checkOtherTns(otherColNums, arrVals) == true){
            if (!dict_counts.hasOwnProperty(arrVals[colNums[0]])){
              dict_counts[arrVals[colNums[0]]] = 0
            }
            dict_counts[arrVals[colNums[0]]] = dict_counts[arrVals[colNums[0]]] + parseInt(arrVals[countColNum]);
          }
        }
      }
      else if (tableId == Table_cc || tableId == Table_odc){
        // console.log(otherColNums);
        if (arrVals[colNums[0]] != null){

          // Check other values
          if (checkOtherTns_ccOdc(otherColNums, arrVals) == true){
            if (!dict_counts.hasOwnProperty(arrVals[colNums[0]])){
              dict_counts[arrVals[colNums[0]]] = 0
            }
            dict_counts[arrVals[colNums[0]]] = dict_counts[arrVals[colNums[0]]] + parseInt(arrVals[countColNum]);
          }
        }
      }
    }
  });

  return (dict_counts);
}

function checkOtherTns(otherColNums, isoVals){
  // console.log("Check other table names ");
  // console.log(dict_filterList);
  let isAnyFound = false; let isInAllSubset = true;

  for (let tn in otherColNums){
    //console.log('Length is ' + dict_filterList[tn]);

    if (dict_filterList[tn].length > 0){
      isAnyFound = true;
      otherColNums[tn].forEach(function(colNum, colNum_i){
        // console.log("Value is " + isoVals[colNum]);
        if (!dict_filterList[tn].includes(String(isoVals[colNum]))){
          isInAllSubset = false;
        }
      });
    }
  }

  if (isAnyFound == false){
    //console.log("cond 1");
    return true;
  }
  else if (isAnyFound == true && isInAllSubset == true){
    //console.log("cond 2");
    return true;
  }
  else {
    //console.log("cond 3");
    return false;
  }
}

function checkOtherTns_ccOdc(otherColNums, isoVals){
  // console.log("Check other table names ");
  // console.log(dict_filterList);
  let isAnyFound = false; let isInAllSubset = true;

  for (let tn in otherColNums){
    //console.log('Length is ' + dict_filterList[tn]);

    if (dict_filterList[tn].length > 0){
      isAnyFound = true;

      let isAnyFound_singleCcOdc = false;
      otherColNums[tn].forEach(function(colNum, colNum_i){
        // console.log("Value is " + isoVals[colNum]);
        if (isoVals[colNum] != null && dict_filterList[tn].includes(String(isoVals[colNum]))){
          // isInAllSubset = false;
          isAnyFound_singleCcOdc = true;
        }
      });
      if (isAnyFound_singleCcOdc == false){
        isInAllSubset = false;
      }
    }
  }

  if (isAnyFound == false){
    //console.log("cond 1");
    return true;
  }
  else if (isAnyFound == true && isInAllSubset == true){
    //console.log("cond 2");
    return true;
  }
  else {
    //console.log("cond 3");
    return false;
  }
}


function getColNameAndNum(lvl1_choice, lvl2_choice, headerArr, tableId){
  // console.log("Header arr is ");
  // console.log(headerArr);

  // let colNums = []; // let colNum_cnt = -1;
  let tn = lvl2_choice.replace(G3_lvl3_btnPtn, '');
  let tn_forColNum = tn;

  if (tableId == Table_cc){
    tn_forColNum = tn.replace("_cc", '');
  }
  else if (tableId == Table_odc){
    tn_forColNum = tn.replace("_odc", '');
  }



  let res = {};
  if (tableId == Table_st){
    // tn = tn + "_st";
    res = getColNums(headerArr, tn_forColNum, undefined, tableId);
  }
  else if (tableId == Table_cc || tableId == Table_odc){
    tn = tn.replace(/\_[0-9]+$/, '');
    res = getColNums(headerArr, tn_forColNum, tn_forColNum + "_merge", tableId);
  }


  // console.log("Tn is " + tn);
  // console.log(colNums);

  return ({colNums: res.colNums, tn: tn, countCol: res.colNum_cnt, otherColNums: res.otherColNums});
}

function getColNums(headerArr, tn, tn_merge, tableId){

  let colNums = []; let colNum_cnt = -1;
  let otherTnNums = {}; // Table names which are not currently clicked; dict_{tn} => colNum

  let btns = document.getElementById(tableId).querySelectorAll('[id^="' + G3_lvl3_btnPtn + '"]');


  btns.forEach(function(aBtn, aBtn_i){
    let btnTn = aBtn.id.replace(G3_lvl3_btnPtn, '');
    if (tableId == Table_cc){
        btnTn = btnTn.replace('_cc', '');
    }
    else if (tableId == Table_odc){
      btnTn = btnTn.replace('_odc', '');
    }

    if (btnTn != tn){
      otherTnNums[btnTn] = [];
    }
  });


  headerArr.forEach(function(item, i){
    if (item == tn){
      colNums.push(i);
    }

    if (tn_merge && tn_merge == item){
      colNums.push(i);
    }

    if (item == 'count'){
      colNum_cnt = i;
    }



    if (otherTnNums.hasOwnProperty(item)){
      otherTnNums[item].push(i);
    }
    if (item.match(/\_merge$/)){
      let mergeKey = item.replace("_merge", "");
      if (otherTnNums.hasOwnProperty(mergeKey)){
        otherTnNums[mergeKey].push(i);
      }
    }

  });

  let rightOtherTnNums = {};
  if (tableId == Table_cc){
    for (let key in otherTnNums){
      rightOtherTnNums[key + "_cc"] = [];
      otherTnNums[key].forEach(function(colNum, colNum_i){
        rightOtherTnNums[key + "_cc"].push(colNum);
      });

    }
  }
  else if (tableId == Table_odc){
    for (let key in otherTnNums){
      rightOtherTnNums[key + "_odc"] = [];
      otherTnNums[key].forEach(function(colNum, colNum_i){
        rightOtherTnNums[key + "_odc"].push(colNum);
      });

    }
  }
  else if (tableId == Table_st){
    rightOtherTnNums = otherTnNums;
  }


  return ({colNums: colNums, colNum_cnt: colNum_cnt, otherColNums: rightOtherTnNums});
}
