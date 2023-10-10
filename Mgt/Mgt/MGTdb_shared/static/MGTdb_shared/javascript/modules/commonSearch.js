export {bindEnterToSearch}; 

// SEARCH - ENTER BUTTON
function bindEnterToSearch(btnId){
	$(document).keypress(function(e){
		if (e.which == 13){ // 13 == enter key
			document.getElementById(btnId).click();
		}
	});
}
