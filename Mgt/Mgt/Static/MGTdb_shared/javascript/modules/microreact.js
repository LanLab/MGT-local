export {sendToMicroreact, downloadMrSuccess};

import {getOtherPage, ajaxCall} from './packageAndSend.js';


function sendToMicroreact(searchVar){
  /*
  1. Send request to mgt to get data with country and year.
  2. Package data in microreact format.
  3. Send data to microreact
  4. get data from microreact

  */

  document.getElementById("viewInMicroReact").disabled = true;
  document.getElementById("fetchingcsv").style.display = '';
  document.getElementById('viewInMicroReact').innerHTML = "Converting - this might take a few seconds";

  getOtherPage(null, searchVar, false, false, true, false);
}


function downloadMrSuccess(response){
  document.getElementById("viewInMicroReact").disabled = false;
  document.getElementById("fetchingcsv").style.display='none';

  console.log(response);
  if (response.hasOwnProperty('outString')){
    downloadMgt9ApsSuccess(response.outString);
  }

  if (response.hasOwnProperty('resMr') && response.resMr.hasOwnProperty('url')){
    document.getElementById('viewInMicroReact').innerHTML = response.resMr.url;
    document.getElementById('viewInMicroReact').onclick = function(){
      window.open(response.resMr.url, '_blank').focus();
    }

    document.getElementById('viewInMicroReact').classList.remove('btn-primary');
    document.getElementById('viewInMicroReact').classList.add('btn-link');

  }
  else{
    // document.getElementById('viewInMicroReact').innerHTML = "Could not create project in Microreact";
    document.getElementById('viewInMicroReact').innerHTML = "Data download for Microreact complete. Download again.";
  }
  /*
  let data = {};

  data['name'] = 'MGT';
  data['webiste'] = "https://mgtdb.unsw.edu.au";
  data['data'] = response;


  console.log("Now packing up as POST for microreact");
  console.log(data);
  */
  // ajaxCall('https://microreact.org/api/project/', data, microreactSuccess);
}

function microreactSuccess(response){
  console.log("Success from microreact");
  console.log(response);
}

function downloadMgt9ApsSuccess(response){
	// console.log(response);

	var blob=new Blob([response]);
	var link=document.createElement('a');
	link.href=window.URL.createObjectURL(blob);
	link.download="Microreact.csv";
	link.click();




	// 3. Enable the button again & hide searching div.
  document.getElementById("viewInMicroReact").disabled = false;
  document.getElementById("fetchingcsv").style.display='none';

	if (document.getElementById('pageNumLoading')){
		document.getElementById('pageNumLoading').style.display = 'none';
	}

}
