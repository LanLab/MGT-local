import {bindEnterToSearch} from './modules/commonSearch.js';
window.bindEnterToSearch = bindEnterToSearch;


import {rowLayoutOfApsAndCcs, doSimHl, removeSimHl, doSmpToggle, doHighlighting, clearHighlighting, toggleHighlighting, clearHlSelection} from './modules/isolateDetailPageFns.js'
window.rowLayoutApCc = rowLayoutOfApsAndCcs;
window.doSimHl = doSimHl;
window.removeSimHl = removeSimHl;
window.doSmpToggle = doSmpToggle;
window.doHighlighting = doHighlighting;
window.clearHighlighting = clearHighlighting;
window.toggleHighlighting = toggleHighlighting;
window.clearHlSelection = clearHlSelection; 

import {isolateDetailSearch} from './modules/isolateDetailAjax.js';
window.isolateDetailSearch = isolateDetailSearch;


import {printCcMergeInfo} from './modules/mergedCcOdcDisplay.js';
window.printCcMergeInfo = printCcMergeInfo;


import { doApLayout, doCcLayout } from './modules/layoutApCcTable.js'
window.doApLayout = doApLayout;
window.doCcLayout = doCcLayout;

import {sortElemsAndSend, getInitialData, doTheOrderBy, getOtherPage, checkAndGetPageNum} from './modules/packageAndSend.js';
window.Salmoenlla_sortElemsAndSend = sortElemsAndSend;
window.getInitialData = getInitialData;
window.doTheOrderBy = doTheOrderBy;
window.getOtherPage = getOtherPage;
window.checkAndGetPageNum = checkAndGetPageNum;


import {handleGraphicalViewClick, get_timeStCount, plotLvl2_stCcOdc, plotLvl1_timeLoc} from './modules/graph_timeOrLocStCount.js'
window.handleGraphicalViewClick = handleGraphicalViewClick;
window.getTimeStCount = get_timeStCount;
window.plotLvl2StCcOdc = plotLvl2_stCcOdc;
window.plotLvl1TimeLoc = plotLvl1_timeLoc;


import {switchDisplayDst, switchDisplayColor} from './modules/additionalTabLayout.js';
window.switchDisplayDst = switchDisplayDst;
window.switchDisplayColor = switchDisplayColor;


import {get_timeLocStCnt, g2_plotLvl1_stCcOdc} from './modules/graph_timeAndLocStCount.js';
window.getTimeLocStCont = get_timeLocStCnt;
window.g2_plotLvl1_stCcOdc = g2_plotLvl1_stCcOdc;

import {doTheDownload, downloadMgt9Aps} from './modules/downloads.js';
window.doTheDownload = doTheDownload;
window.downloadMgt9Aps = downloadMgt9Aps;

import {sendToMicroreact} from './modules/microreact.js';
window.sendToMicroreact = sendToMicroreact;

import {getInitDataG3, g3_switchStCcOdc} from './modules/graph_breakdown.js';
window.getInitDataG3 = getInitDataG3;
window.g3SwitchStCcOdc = g3_switchStCcOdc;