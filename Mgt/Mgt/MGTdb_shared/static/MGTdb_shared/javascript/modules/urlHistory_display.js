export {handleBackPage};

import {addRowToFilterTbl} from './filterIsolatesDisplay.js';
import {islnYear, islnDate, islnMonth} from './constants.js';


/* Page (search) request through url. */
function handleBackPage(dirColsInfo, dirAps, dirCcs, serverStatusChoices, assignStatusChoices, privStatusChoices, boolChoices){
	console.log('In handleBackPage: '); 
	console.log(boolChoices); 


	var isAnyRowForSearchAdded = false;

	if (window.location.search && window.location.search != ""){ // url search present
		var searchParams = new URLSearchParams(window.location.search);

		console.log("The searchParams are " + searchParams);

		var arr_aps = [];

		// var aps = {};
		// let timeSearch = {};
		let timeSearch = [];
		searchParams.forEach(function(value, key){ // check if value is recognized...
			console.log ("The key and value are " + key + " " + value);

			if (key == 'searchType'){
				document.getElementById(value+'Search').checked = true;
			}

			if(isKeyPresent(key, dirColsInfo) == true || isKeyPresent(key, dirAps) || isKeyPresent(key, dirCcs) /* && isKeyPresent(key, apHeader) == false && isKeyPresent(key, ccHeader) == false && isKeyPresent(key, epiHeader) == false && isKeyPresent(key, locHeader) == false && isKeyPresent(key, islnHeader) == false */ ) {

				if (key.match(/\_st$/) || key.match(/\_dst$/)){
					addToApsArr(arr_aps, key, value);

					//console.log(arr_aps)
				}
				else if (key.match(/\_\_gte$/) || key.match(/\_\_lte$/) || key == islnYear || key == islnDate || key == islnMonth){
					timeSearch = addToTimeArr(timeSearch, key, value);
					console.log(timeSearch);
				}
				else{
					addRowToFilterTbl("theSearchTbl", dirColsInfo, dirAps, dirCcs, serverStatusChoices, assignStatusChoices, privStatusChoices, key, value, boolChoices);
				}
				isAnyRowForSearchAdded = true;
			}
		});

		// now add the aps.
		// console.log("now the aps");
		//for(var apTn in aps) {
		arr_aps.forEach(function(aps, aps_i){
			for (let apTn in aps){

				if (aps.hasOwnProperty(apTn)) {
					// handle prop as required
					// console.log(aps[apTn]);
					addRowToFilterTbl("theSearchTbl", dirColsInfo, dirAps, dirCcs, serverStatusChoices, assignStatusChoices, privStatusChoices, apTn, aps[apTn], boolChoices);
				}
			}
		});

		timeSearch.forEach(function(timeSearch_hm, timeSearch_hm_i){
			for (let [tn, arrVal] of Object.entries(timeSearch_hm)) {
				// console.log(`${key}: ${value}`);
				addRowToFilterTbl("theSearchTbl", dirColsInfo, dirAps, dirCcs, serverStatusChoices, assignStatusChoices, privStatusChoices, tn, arrVal, boolChoices);
			}
		});



		// http://localhost:8000/salmonella/isolate-list?ap2_0_st=2&ap2_0_dst=7&ap6_0_st=2
		// http://localhost:8000/salmonella/isolate-list?year__gte=2010&year__lte=2020

		// search with params ... for isolate list.
	}

	return isAnyRowForSearchAdded;
}

function addToTimeArr(arr, key, value){
	if (key.match(/\_\_gte$/)){
		key = key.replace(/\_\_gte$/, '');
		doTheAdding(arr, key, value, 0);
	}
	else if (key.match(/\_\_lte$/)){
		key = key.replace(/\_\_lte$/, '');
		doTheAdding(arr, key, value, 1);
	}
	else if (key == islnYear || key == islnMonth || key == islnDate){
		doTheAdding(arr, key, value, 0);
		doTheAdding(arr, key, value, 1);
	}
	return arr;
}


function addToApsArr(arr, key, value){
	// console.log("the key is " + key);
	if (key.match(/\_st$/)){
		key = key.replace(/\_st$/, '');
		// console.log(key);
		doTheAdding(arr, key, value, 0);

	}
	if (key.match(/\_dst$/)){
		key = key.replace(/\_dst$/, '');

		doTheAdding(arr, key, value, 1);
	}
	// return arr;
}

function doTheAdding(arr, key, value, position){
	let isAdded = false;

	for (let i = arr.length - 1; i >= 0; i--){

		if (position == 1 && arr[i].hasOwnProperty(key)){
			var stdst = arr[i][key];

			stdst[position] = value;
			arr[i][key] = stdst;


			isAdded = true;
			break;
		}
	}

	if (isAdded == false){
		let ap = {};
		ap[key] = [null, null];
		ap[key][position] = value;
		console.log('The arr(2) is');
		console.log(arr);
		arr.push(ap);
	}
}


function isKeyPresent(key, apInfo){

	for  (var i = 0; i< apInfo.length; i++){ // dst is added to the last st value.
		if (key && (key == apInfo[i].table_name || key == apInfo[i].table_name + "_st" || key == apInfo[i].table_name + "_dst"  || key == apInfo[i].table_name + "__gte" ||key ==  apInfo[i].table_name + "__lte")){
			// console.log('true');
			return (true)
		}
	}

	return (false);

}
