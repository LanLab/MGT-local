export {doTheDownload, downloadCsvSuccess, downloadMgt9Aps, downloadMgt9ApsSuccess};

import {getOtherPage} from './packageAndSend.js';

function downloadMgt9ApsSuccess(response){
	// console.log(response);

	var blob=new Blob([response]);
	var link=document.createElement('a');
	link.href=window.URL.createObjectURL(blob);
	var fn_ap = document.getElementById('btnMgt9Download').innerHTML;
	fn_ap = fn_ap.trim();
	fn_ap = fn_ap.replace('Download ', '');
	fn_ap = fn_ap.replace(' allelic profiles', '');
	fn_ap = fn_ap.replace(/[\s]+/g, '_');
	// console.log('Downloaded file name is ' + fn_ap);

	link.download = fn_ap + "_allelic_profiles.tsv";
	link.click();




	// 3. Enable the button again & hide searching div.
	document.getElementById("btnMgt9Download").disabled = false;
	document.getElementById("fetchingcsv").style.display='none';

	if (document.getElementById('pageNumLoading')){
		document.getElementById('pageNumLoading').style.display = 'none';
	}

}


function downloadCsvSuccess(response){
	document.getElementById("csvDownload").disabled = false;
	document.getElementById("fetchingcsv").style.display='none';

	var blob=new Blob([response]);
	var link=document.createElement('a');
	link.href=window.URL.createObjectURL(blob);
	link.download="MGT_isolate_data.txt";
	link.click();

	if (document.getElementById('pageNumLoading')){
		document.getElementById('pageNumLoading').style.display = 'none';
	}


}


function doTheDownload(searchVar){
	document.getElementById("csvDownload").disabled=true;
	document.getElementById("fetchingcsv").style.display='';

	getOtherPage(null, searchVar, true, false, false, false);
}

function downloadMgt9Aps(searchVar){
	document.getElementById("btnMgt9Download").disabled = true;
	document.getElementById("fetchingcsv").style.display='';


	let isGrapeTreeFmt = document.getElementById('isGrapeTree').checked;
	console.log("Is grapetree format required " + isGrapeTreeFmt);


	getOtherPage(null, searchVar, false, true, false, isGrapeTreeFmt);
}
