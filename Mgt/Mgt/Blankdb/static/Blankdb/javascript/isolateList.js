
import { doApLayout, doCcLayout } from './modules/layoutApCcTable.js'
window.Blankdb_doApLayout = doApLayout;
window.Blankdb_doCcLayout = doCcLayout;


import {handleGraphicalViewClick, get_timeStCount, plotLvl2_stCcOdc, plotLvl1_timeLoc} from './modules/graph_timeOrLocStCount.js'
window.Blankdb_handleGraphicalViewClick = handleGraphicalViewClick;
window.Blankdb_getTimeStCount = get_timeStCount;
window.Blankdb_plotLvl2StCcOdc = plotLvl2_stCcOdc;
window.Blankdb_plotLvl1TimeLoc = plotLvl1_timeLoc;


import {bindEnterToSearch} from './modules/commonSearch.js';
window.Blankdb_bindEnterToSearch = bindEnterToSearch;


import {addRowToFilterTbl} from './modules/filterIsolatesDisplay.js';
window.Blankdb_addRowToFilterTbl = addRowToFilterTbl;


import {handleBackPage} from './modules/urlHistory_display.js';
window.Blankdb_handleBackPage = handleBackPage;


import {switchDisplayDst, switchDisplayColor} from './modules/additionalTabLayout.js';
window.Blankdb_switchDisplayDst = switchDisplayDst;
window.Blankdb_switchDisplayColor = switchDisplayColor;


import {sortElemsAndSend, getInitialData, doTheOrderBy, getOtherPage, checkAndGetPageNum} from './modules/packageAndSend.js';
window.Blankdb_sortElemsAndSend = sortElemsAndSend;
window.Blankdb_getInitialData = getInitialData;
window.Blankdb_doTheOrderBy = doTheOrderBy;
window.Blankdb_getOtherPage = getOtherPage;
window.Blankdb_checkAndGetPageNum = checkAndGetPageNum;

import {printCcMergeInfo} from './modules/mergedCcOdcDisplay.js';
window.Blankdb_printCcMergeInfo = printCcMergeInfo;

import {doTheDownload, downloadMgt9Aps} from './modules/downloads.js';
window.Blankdb_doTheDownload = doTheDownload;
window.Blankdb_downloadMgt9Aps = downloadMgt9Aps;

import {get_timeLocStCnt, g2_plotLvl1_stCcOdc} from './modules/graph_timeAndLocStCount.js';
window.Blankdb_getTimeLocStCont = get_timeLocStCnt;
window.Blankdb_g2_plotLvl1_stCcOdc = g2_plotLvl1_stCcOdc;


import {sendToMicroreact} from './modules/microreact.js';
window.Blankdb_sendToMicroreact = sendToMicroreact;


import {getInitDataG3, g3_switchStCcOdc} from './modules/graph_breakdown.js';
window.Blankdb_getInitDataG3 = getInitDataG3;
window.Blankdb_g3SwitchStCcOdc = g3_switchStCcOdc;
