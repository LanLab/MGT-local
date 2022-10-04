import {bindEnterToSearch} from './modules/commonSearch.js';
window.Blankdb_bindEnterToSearch = bindEnterToSearch;


import {rowLayoutOfApsAndCcs, doSimHl, removeSimHl, doSmpToggle, doHighlighting, clearHighlighting, toggleHighlighting, clearHlSelection} from './modules/isolateDetailPageFns.js'
window.Blankdb_rowLayoutApCc = rowLayoutOfApsAndCcs;
window.Blankdb_doSimHl = doSimHl;
window.Blankdb_removeSimHl = removeSimHl;
window.Blankdb_doSmpToggle = doSmpToggle;
window.Blankdb_doHighlighting = doHighlighting;
window.Blankdb_clearHighlighting = clearHighlighting;
window.Blankdb_toggleHighlighting = toggleHighlighting;
window.Blankdb_clearHlSelection = clearHlSelection; 

import {isolateDetailSearch} from './modules/isolateDetailAjax.js';
window.isolateDetailSearch = isolateDetailSearch;


import {printCcMergeInfo} from './modules/mergedCcOdcDisplay.js';
window.Blankdb_printCcMergeInfo = printCcMergeInfo;


import { doApLayout, doCcLayout } from './modules/layoutApCcTable.js'
window.Blankdb_doApLayout = doApLayout;
window.Blankdb_doCcLayout = doCcLayout;

import {sortElemsAndSend, getInitialData, doTheOrderBy, getOtherPage, checkAndGetPageNum} from './modules/packageAndSend.js';
window.Blankdb_sortElemsAndSend = sortElemsAndSend;
window.Blankdb_getInitialData = getInitialData;
window.Blankdb_doTheOrderBy = doTheOrderBy;
window.Blankdb_getOtherPage = getOtherPage;
window.Blankdb_checkAndGetPageNum = checkAndGetPageNum;


import {handleGraphicalViewClick, get_timeStCount, plotLvl2_stCcOdc, plotLvl1_timeLoc} from './modules/graph_timeOrLocStCount.js'
window.Blankdb_handleGraphicalViewClick = handleGraphicalViewClick;
window.Blankdb_getTimeStCount = get_timeStCount;
window.Blankdb_plotLvl2StCcOdc = plotLvl2_stCcOdc;
window.Blankdb_plotLvl1TimeLoc = plotLvl1_timeLoc;


import {switchDisplayDst, switchDisplayColor} from './modules/additionalTabLayout.js';
window.Blankdb_switchDisplayDst = switchDisplayDst;
window.Blankdb_switchDisplayColor = switchDisplayColor;


import {get_timeLocStCnt, g2_plotLvl1_stCcOdc} from './modules/graph_timeAndLocStCount.js';
window.Blankdb_getTimeLocStCont = get_timeLocStCnt;
window.Blankdb_g2_plotLvl1_stCcOdc = g2_plotLvl1_stCcOdc;

import {doTheDownload, downloadMgt9Aps} from './modules/downloads.js';
window.Blankdb_doTheDownload = doTheDownload;
window.Blankdb_downloadMgt9Aps = downloadMgt9Aps;

import {sendToMicroreact} from './modules/microreact.js';
window.Blankdb_sendToMicroreact = sendToMicroreact;

import {getInitDataG3, g3_switchStCcOdc} from './modules/graph_breakdown.js';
window.Blankdb_getInitDataG3 = getInitDataG3;
window.Blankdb_g3SwitchStCcOdc = g3_switchStCcOdc;
