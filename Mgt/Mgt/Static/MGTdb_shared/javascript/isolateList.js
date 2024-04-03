
import { doApLayout, doCcLayout } from './modules/layoutApCcTable.js'
window.doApLayout = doApLayout;
window.doCcLayout = doCcLayout;


import {handleGraphicalViewClick, get_timeStCount, plotLvl2_stCcOdc, plotLvl1_timeLoc} from './modules/graph_timeOrLocStCount.js'
window.handleGraphicalViewClick = handleGraphicalViewClick;
window.getTimeStCount = get_timeStCount;
window.plotLvl2StCcOdc = plotLvl2_stCcOdc;
window.plotLvl1TimeLoc = plotLvl1_timeLoc;


import {bindEnterToSearch} from './modules/commonSearch.js';
window.bindEnterToSearch = bindEnterToSearch;


import {addRowToFilterTbl} from './modules/filterIsolatesDisplay.js';
window.addRowToFilterTbl = addRowToFilterTbl;


import {handleBackPage} from './modules/urlHistory_display.js';
window.handleBackPage = handleBackPage;


import {switchDisplayDst, switchDisplayColor} from './modules/additionalTabLayout.js';
window.switchDisplayDst = switchDisplayDst;
window.switchDisplayColor = switchDisplayColor;


import {sortElemsAndSend, getInitialData, doTheOrderBy, getOtherPage, checkAndGetPageNum} from './modules/packageAndSend.js';
window.sortElemsAndSend = sortElemsAndSend;
window.getInitialData = getInitialData;
window.doTheOrderBy = doTheOrderBy;
window.getOtherPage = getOtherPage;
window.checkAndGetPageNum = checkAndGetPageNum;

import {printCcMergeInfo} from './modules/mergedCcOdcDisplay.js';
window.printCcMergeInfo = printCcMergeInfo;

import {doTheDownload, downloadMgt9Aps} from './modules/downloads.js';
window.doTheDownload = doTheDownload;
window.downloadMgt9Aps = downloadMgt9Aps;

import {get_timeLocStCnt, g2_plotLvl1_stCcOdc} from './modules/graph_timeAndLocStCount.js';
window.getTimeLocStCont = get_timeLocStCnt;
window.g2_plotLvl1_stCcOdc = g2_plotLvl1_stCcOdc;


import {sendToMicroreact} from './modules/microreact.js';
window.sendToMicroreact = sendToMicroreact;


import {getInitDataG3, g3_switchStCcOdc} from './modules/graph_breakdown.js';
window.getInitDataG3 = getInitDataG3;
window.g3SwitchStCcOdc = g3_switchStCcOdc;
