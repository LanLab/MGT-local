 // $(document).ready(function() {

function theHelpFns(button){
	console.log("button is ");
	console.log(button.dataset.whatever);
  $('#exampleModal').on('show.bs.modal', function (event) {
   // var button = $(event.relatedTarget) // Button that triggered the modal
    var recipient = button.dataset.whatever; // $(button).data('whatever') // Extract info from data-* attributes
    // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
    // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
    let vals = {title: 'New message to ' + recipient, body: "Hi " + recipient};
    if (recipient == '@top5Dist'){
      	vals = helpTop5Dist();
    }
    else if (recipient == '@top5DistChart'){
      	vals = helpTop5DistChart();
    }
    else if (recipient == '@puDownloadableData'){
      	vals = helpPuDownloadableData();
    }
    else if (recipient == '@filterIsolates'){
      	vals = helpFilterIsolates();
    }
    else if (recipient == '@tablesOrGraph'){
      	vals = helpTablesOrGraph();
    }
    else if (recipient == '@dstAndCol'){
      	vals = helpDstAndCol();
    }
    else if (recipient == '@pageNumGo'){
      	vals = helpPageNumGo();
    }
    else if (recipient == '@downloadAsCsv'){
    	vals = helpDownloadAsCsv();
    }
    else if (recipient == '@downloadAsAps'){
    	vals = helpDownloadAsAps();
    }
    else if (recipient == '@viewInMicroReact'){
    	vals = helpViewInMicroReact();
    }
	else if (recipient == '@graphTimeAndLoc'){
		vals = helpGraphTimeAndLoc();
	}
	else if (recipient == '@graphTimeOrLoc'){
		vals = helpGraphTimeOrLoc();
	}
	else if (recipient == '@graphMgtBreakdown'){
		vals = helpGraphMgtBreakdown();
	}
	else if (recipient == '@isolateDetail'){
		vals = helpIsolateDetail(); 
	}
	else if (recipient == '@isoDetailOnlyComplSt'){
		vals = helpIsoDetailOnlyComplSt(); 
	}
	else if (recipient == '@mergedCcOdc'){
		vals = helpMergedCcOdc(); 
	}
	else if (recipient == '@projDwnldAps'){
		vals = helpProjDownloadApFile(); 
	}
	else if (recipient == '@downloadRepHtml'){
		vals = helpDownloadRepHtml(); 
	}
	else if (recipient == '@downloadReport'){
		vals = helpDownloadReport(); 
	}
    var modal = $(this)
    modal.find('.modal-title').text(vals.title);
    modal.find('.modal-body').html(vals.body);
   })
}

function helpDownloadReport(){
	let body = "For a chosen country or project (if logged in), or both, a report containing static summary charts for epidemeological investigation of isolates at each MGT level is generated. This report can be easily downloaded as an html file. Button to download this report can be found at the bottom of this page. Please note that for a country with a large number of isolates, report generation may take a few seconds (depending on the power of your browser).";
	return {title: 'Generate a summary report', body: body}; 
}

function helpDownloadRepHtml(){
	let body = "The generated summary report can be downloaded as a single html page, which can be opened on your local computer using any browser."; 
	return {title: 'Download report as HTML', body: body}; 
}

function helpMergedCcOdc(){
	let body = "Merged CC and ODC identifiers when present, are listed in the table below for each MGT-CC or MGT-ODC level. As the clusters here are based on allele differences (CCs are single locus differences; ODCs range from single to 10 loci difference), a new cluster may arise with the addition of any new isolate which bridges two clusters and resulting in the merge. Our algorithm retains the primary cluster identifier associated with the isolate, and additionally notes the most recent merged value.";
	return {title: 'Merged CCs and ODCs', body: body};  
}

function helpIsoDetailOnlyComplSt(){
	let body = "Default search ignores the dST value, and searches for any isolates assigned the same ST. Selecting this option excludes alleles with missing information (i.e. alleles assigned a dST value) from search - even if the current isolate is assigned a dST - and only searches for isolates assigned a complete ST (equivalent to an empty dST, or dST with value of '.0').";
	return {title: 'Searching isolates assigned a complete ST', body: body};  
}

function helpIsolateDetail(){
	let body = 'Click on highlightable values (light purple) in the tables below, to select them. Once selected, a search can then be performed by clicking on the "Search" button below. For any selected values, an exact search is performed. For any MGT ST search, the dST value is ignored.'; 
	return {title: 'Navigation', body: body}; 
}

function helpGraphTimeOrLoc(){
	let body = (function (){ /*
		This interactive graph summarizes all the initially loaded isolates, or filtered isolates, as a stacked bar graph. Only isolates with associated metadata from the search are plotted - the counts of the total and plotted isolates are listed below the plot (line beginning "Total isolates matching search are ..."). Within the plot, the X-axis shows the count and Y-axis shows the metadata (e.g. year or country). The graph is stacked by the number of isolates assigned particular STs, CCs or ODCs that occur within the shown metadata. Isolates which match to a unique ST, CC or ODC within a particular stacked column (i.e. in particular year, or particular country) are added to a 'Singleton' class (when number of isolates to be plotted are > 1000). <br><br> 

		<h6 class='speHeading'> Data fetching and processing </h6> 
		The data is initially fetched once on clicking 'Load data'. The processing of the data, and switching of the data happens on the user's browser. Any bar chart in this visualization is currently scaled to 650 pixels height in the browser window. <br>
		<b> Note: </b> The graph rendering may take a few minutes when a large and diverse set of isolates are plotted (such as the  initially loaded isolates' sequence types visualized at the MGT 9 level). <i> We strongly recommend visualising a small set of data (upto 5000 isolates) in this graph. </i> <br><br> 

		<h6 class='speHeading'> Updating the plot data (Zoom by) </h6> 
		The various buttons at the top of the plot can be used to control the data that is visualised. <br> <br> 

		<b> Time or location </b>  <br> 
		The top level buttons, enable switching between visualising time or location. By default, isolates are shown <i> per year </i> in time, and <i> per country </i> in location. The time can be changed to counts <i> per month </i>  or  <i> per date </i>. Location can be zoomed out to, by <i> per continent </i>  or zoomed in, to <i> per state </i>  or <i> per postcode </i>. <br><br> 

		<b> Sequence types, clonal complexes and outbreak detection clusters </b> <br> 
		By default, the charts are plotted depicting isolate distributions over MGT sequence types (ST). This can be switched to show the isolate distributions over conal complexes (CC) or outbreak detection clusters (ODC). <br> <br> 
		
		<b> MGT ST/CC/ODC  </b> <br> 
		By default isolate distributions are visualized at the smallest level of MGT-ST, CC or ODC. These can be switch to any larger level. <br> <br> 


		<h6 class='speHeading'> Additional viewing features</h6> 
		<b> Stack by </b> <br> 
		The default stack order is by the isolate distribution of STs, CCs or ODCs, where the STs with the most number of isolates are shown at the bottom, and the least (and singletons - STs represented by a single isolate) at the top. This can be switched to order the stacked-bars by the ST, CC or ODC identifier. <br> <br> 


		<b> Highlighting only top X </b> <br> 
		By default, all STs, CCs, or ODCs are shown, with the exception of singletons (which are grouped together into one class). This is equivalent to having a 'Only highlight top' value of 0. 
		<br> 
		As an example case, in order to highlight the ST, CC or ODC with the largest number of isolates assigned to it, the user can specify the 'Only highlight top' value of 1. This results in only the bars with the largest ST, CC or ODC isolate count (computed globally, i.e. total taken over all isolates and not per column), being shown coloured, and the remaining bars are shown in white.  
		<br>
		In this manner, the user can spcify any (positive integer) value to this input to highlight STs, CCs, or ODCs containing the top X isolate distributions. 
		<br><br> 
		<b> Show background isolates </b> <br> 
		When a user is logged in and viewing isolate distributions for isolates in any of their projects, the 'Background strains' button can be switched-on to overlay isolate ST, CC or ODC distributions of publicly available isolates. The background isolates are indicated by the reduced opacity segment of a ST, CC or ODC bar. The exact values of the isolate counts, in the user's project and in the MGT public database, for any ST, CC, or ODC are revealed by hovering over a bar.   
		<br><br> 
		
		<h6 class='speHeading'> Download as SVG </h6> 
		The bar graph with the currently rendered data can be downloaded as a scalable vector graphics (SVG) file. The ST, CC or ODC identifier which is revealed on hover in the interactive graph is appended as legend in the downloaded graph. Such a downloaded SVG graph can be opened in external tools such as Adobe Illustrator and edited as needed. 
	*/}).toString().match(/[^]*\/\*([^]*)\*\/\}$/)[1];
	return {title: 'Summarize search with either isolate associated time or location metadata', body: body}; 
}

function helpGraphMgtBreakdown(){
	let body = (function (){ /*

		This interactive graph can be used to explore the breakdown of isolate distributions for particular MGT-STs, CCs and ODCs in the initially loaded or searched isolates. <br> 
		<br> 

		<h6 class='speHeading'> Data fetching and processing </h6> 
		The data is initially fetched once on clicking 'Load data'. The processing of the data, and switching of the data happens on the user's browser. Any bar chart in this visualization is currently scaled to 400 pixels height in the browser window. <br>
		<b> Note: </b> The graph rendering may take a few minutes when a large and diverse set of isolates are plotted (such as the  initially loaded isolates' sequence types). <i> We strongly recommend visualising a smaller set of data (upto 8000 isolates) in this graph. </i> <br><br> 

		<h6 class='speHeading'> Updating the plot data </h6> 
		<b> Sequence types, clonal complexes and outbreak detection clusters </b> <br> 
		By default, the charts are plotted depicting isolate distributions over MGT sequence types (ST). This can be switched to show the isolate distributions over conal complexes (CC) or outbreak detection clusters (ODC). <br> <br> 


		<h6 class='speHeading'> The graph layout </h6>
		For all MGT levels within a particular view (i.e. STs, CCs, or ODCs), stacked column graphs are created. A graph is stacked by the number of isolates assigned particular STs, CCs or ODCs (with STs, CCs or ODCs assigned to the most isolates, plotted at the top). Isolates that are assigned to a unique ST, CC or ODC within a particular stacked column are added to a 'Singleton' class (added at the bottom of the stacked chart). Above each chart, the total number of isolates and the total number of STs, plotted in the chart are presented. 
		<br> <br> 


		<h6 class='speHeading'> Exploring breakdown </h6>
		Hovering over a bar reveals the ST value and the number of isolates assigned that ST. For a particular ST value, The distributions of isolates at other MGT levels can be explored. This is done by clicking on a bar with a particular ST value, which selects it.  A selected bar is indicated by its opacity being 0%, where as, unselected bars have 50% opacity. The selection of an ST value, results in the stacked bar graphs for other MGT levels to be replotted (and the update of the corresponding isolate counts and ST counts). The counts of isolates in the selected ST is indicated below its stacked bar chart. 
		<br> <br>  
		Multiple STs from the same stacked bar chart or STs from different MGT levels can be selected in any combination. At any time, for any MGT level, the selection can be cleared by clicking on the 'Clear selection' button at the bottom. This results in all selections from the cleared-selection-graph to be removed, and other MGT level graphs to be updated to now remove isolate-distribution calculation restrictions to the cleared ST values.
		<br> <br> 


		<h6 class='speHeading'> Hierarchical inconsistency </h6>
		Occasionally, due to the mutually exclusive nature of the lower MGT levels, a user may encounter hierarchical inconsistencies - i.e. a scenario where mutation in a lower resolution level (e.g. MGT3) could result in two separate STs, while a higher resolution level (e.g. MGT4) has the same ST. 

		For a detailed explaination please see topic '<a href="https://mgt-docs.readthedocs.io/en/latest/overview.html#hierarchical-inconsistency" target="_blank">Hierarchical inconsistency</a>' in MGTdb's documentation. 
		
	*/}).toString().match(/[^]*\/\*([^]*)\*\/\}$/)[1];
	return {title: 'Explore MGT-STs, CCs or ODCs', body: body}; 
}

function helpGraphTimeAndLoc(){
	let body = (function (){ /*
		This interactive graph summarizes all the initially loaded isolates, or filtered isolates, as a heatmap. Only isolates with associated metadata from the search are plotted - the counts of the total and plotted isolates are listed below the plot (line beginning "Total isolates matching search are ..."). Within the plot, X-axis shows the location (e.g. country) and Y-axis shows the time (e.g. year). Each cell within the heatmap summarizes the number of STs (or CCs or ODCs), the number of isolates or both (via Shannon equitability), for the temporal and locational metadata at the selected MGT ST, CC or ODC level. Hovering over a cell reveals all these data in a popup. <br> <br> 

		<h6 class='speHeading'> Data fetching and processing </h6> 
		The data is initially fetched once on clicking 'load data'. The processing of the data, and switching of the data happens on the user's browser. <br><br> 

		<h6 class='speHeading'> Updating the plot data </h6> 
		The various buttons at the top of the plot can be used to control the data that is visualised. 
		<br> <br> 

		<b> Color by </b> <br>
		The 'Color by' buttons can be used to switch the data that is shown in the heatmap. <br> <br> 

		<i> Shannon equitability: </i> This value is the <a href="https://entnemdept.ufl.edu/hodges/protectus/lp_webfolder/9_12_grade/student_handout_1a.pdf" target="_blank"> Shannon diversity index </a> computed for values in a particular cell, divided by the maximum diversity encountered for the entire data set. Thus, the equitability is the diversity, normalized between 0 and 1. This value is shown by default, it combines the number of STs (or CCs or ODCs), and the number of isolates, and reflects the diversity of the STs (or CCs or ODCs) relative to the number of isolates. <br> <br> 


		<i> ST count (or "CC count", or "ODC count"): </i> Switching this on, leads to the data in the heatmap being updated to contain the ST counts (or CC or ODC counts, respectively). <br><br> 

		<i> Isolate count: </i> Switching this on, leads to the data in the heatmap being updated to contain the isolate counts. 
		
		<br> <br> 

		<b> Zoom time by </b>  <br>
		 By default, isolates are shown <i> per year </i> in time (X-axis). The time can be changed to counts <i> per month </i>  or  <i> per date </i>.
		<br> <br> 

		<b> Zoom location by </b> <br>
		By default, isolates are shown <i> per country </i> in location (Y-axis). Location can be zoomed out to, by <i> per continent </i>  or zoomed in, to <i> per state </i>  or <i> per postcode </i>.
		<br> <br> 
		
		<b> Sequence types, clonal complexes and outbreak detection clusters </b> <br> 
		By default, the charts are plotted depicting isolate distributions over MGT sequence types (ST). This can be switched to show the isolate distributions over conal complexes (CC) or outbreak detection clusters (ODC). <br> <br> 
		
		<b> MGT ST/CC/ODC  </b> <br> 
		By default isolate distributions are visualized at the smallest level of MGT-ST, CC or ODC. These can be switch to any larger level. <br> <br> 



		<h6 class='speHeading'> Download as SVG </h6> 
		The heatmap with the currently rendered data can be downloaded as a scalable vector graphics (SVG) file. Such a downloaded SVG graph can be opened in external tools such as Adobe Illustrator and edited as needed. 
	*/}).toString().match(/[^]*\/\*([^]*)\*\/\}$/)[1];
	return {title: 'Summarize search with both isolate associated time and location metadata', body: body}; 
}

function helpViewInMicroReact(){
  let body = 'The set of searched (or initially loaded) isolates, along with the associated metadata, ST, CC and ODC assignments can be downloaded as a CSV in Microreact format. Importantly, the isolates are sent by MGT to Microreact via Microreact\'s API and the link returned by Micrreact is displayed instead of the button. This link opens in a new tab. Current, there a limit of 2000 isolates per request. Microreact is a powerful tool, that allows exploring the epidemeology of the searched (or loaded) isolates in a map-based context. <br><br> <a href="https://microreact.org/" target="_blank"> Link to the Microreact tool for more information </a>';
  return {title: 'View isolates in Microreact', body: body};
}

function helpDownloadAsAps(){
  let body = 'The set of searched (or initially loaded) isolates, along with the highest level MGT allelic profiles can be downloaded in CSV format. When the "In GrapeTree format" option is selected, the ST and dST columns are removed, and the negative alleles (i.e. alleles with missing information) are converted to positive alleles. This allows using the downloaded CSV file as input to the GrapeTree tool (the STs, dSTs and other information downloaded from "Download the entire set as CSV" can be used as metadata in GrapeTree). Thus, by visualising the downloaded file in GrapeTree, the epidemological investigations revealed through the minimal spanning tree built using allelic profiles of the downloaded isolates can be conducted. Currently, allelic profiles for maximum of 10000 (the first 10000) isolates are downloaded via one request. <br><br> <a href="https://github.com/achtman-lab/GrapeTree" target="_blank"> Link to GrapeTree </a> '; 

  return {title: 'Download allelic profiles for isolates', body: body};
}

function helpDownloadAsCsv(){
  let body = 'The set of searched (or initially loaded) isolates, along with the associated metadata, ST, CC and ODC assignments can be downloaded as a CSV file. Currently, a maximum of 1000000 isolates can be downloaded in one go. The larger the number of isolates requested for download, depending on your internet speed, this process may take a few minutes.';
  return {title: 'Download the table', body: body};
}

function helpPageNumGo(){
  let body = 'Enter a page number between 1 and the last page number, then click "Go".';
  return {title: 'Select a page number', body: body};
}

function helpDstAndCol(){
  let body = 'The <b> Display complete ST </b> option is available in the "Sequence types view". When switched on, it enables a user to view the complete ST, i.e. additionally the degenerate ST. Isolates with complete alleles have a dST value of 0 (these are not shown in the table when "Display complete ST" is switched on), and isolates with unresolvable/incomplete alleles have dST values (these are shown when "Display complete ST" is switched on, are displayed by a dot following the ST value.). <br> <br> The <b> Display color </b> option is available in both the "Sequence types view" as well as the "Clonal complexes view". The display color option when switched on (switched on by default) colours each cell in table by the unique ST, CC or ODC value.';
  return {title: 'Displaying DST and color', body: body};
}
function helpTablesOrGraph(){
  let body = 'The three buttons enable viewing different types of information for the loaded isolates. <br><br> The "Sequence types view" and "Clonal complexes view" are tables, which show the sequence types and the clonal complexes, respectively, assigned to the loaded isolates at each MGT level. <br><br> The "Graphical view" contains three graphs which can be initially loaded, and then interactively explored.';
  return {title: 'Switch to see different types of information for loaded isolates', body: body};
}

function helpFilterIsolates(){
  let body = '';
  body = (function (){ /*
	<h6 class="speHeading"> Filter options </h6>
	Selection options 4 types, examples of each type. 
	There are six cateogies of information to search from: 
	<ol> 
		<li> <b> Isolate </b>
			<ol>
				<li> <i> Isolate </i> The isolate name, e.g. "SRR" or "SRR5642043". A substring match is performed. If you are logged in, any private isolates  in your projects matching the pattern are appended to search results. </li> 
				<li> <i> Serovar </i> When present, the typhimurium serovar. A few isolates belonging to different serovars may be found in the <i> Blankdb </i> databases. </li> 
				<li> <i> Server status </i> The status in the processing pipeline of the MGT server. To restrict search to isolates which have finished processing, search for 'Complete'. </li> 
				<li> <i> Assignment status </i> MGT assignment status. To restrict search to isolates which were assigned an MGT, search for 'Assigned MGT'. </li>
				<li> <i> MGT1 </i> MGT1 is also known as the 7 gene MLST. </li>
				<li> <i> Seventh pandemic </i> When 
				available, this value can be used to restrict searched isolates to those which are either part of the seventh pandemic or not (by searching for either 'true' or 'false', respectively). </li> 
				<li> <i> Environmental sampling gene VC2210 </i> When available, this value is the VC2210 gene's allele assignment of the isolate. </li> 
				<li> <i> Privacy status </i> Available when logged in, search can be restricted to either all public, or private isolates in your projects. </li> 
				<li> <i> Project </i> Available when logged in, search can be restricted to the searched project(s). The search matches to the pattern specified. </li> 
								
			</ol> 
		</li> 
		<li> <b> Location </b> <br>
			Continent, country, state or sub-country, or postcode can be search for. A substring search is performed. 
		</li> 
		<li> <b> Isolation </b>
			<ol> 
				<li> <i> Source </i> Sample source (or product) can be organic or non-organic. Some examples are: 'eggs', 'beef', 'misc food', 'live animal', 'human'. <br> To clarify, if for example, the "isolation host" is "chicken", the sample source may be "eggs". Another example, if the "isolation host" is "human", the sample source may also be "human". A substring search is performed. 
				</li> 
				<li> <i> Type </i> The setting in which the isolate was isolated. Some examples are: 'clinical', 'other'. <br> The main goal of this field is to distinguish between human clinical samples and other samples (such as vetenary samples). A substring search is performed.
				</li> 
				<li> <i> Host </i>
					Species of host animal e.g. 'chicken', 'human'. A substring search is perfromed. 
				</li> 
				<li> <i> Host disease </i> 
					The disease that was observed in the isolated host. Some examples are: 'gastroenteritis', 'sepsis'. A substring search is performed.
				</li> 
				<li> <i> Collection date </i> The searched isolates can be restricted to within the date range specified. To search for isolates isolated on a particular date, specify the same start and end date. </li> 
				<li> <i> Collection month </i> The month is specified as a number ranging from 1 to 12. Isolates are restricted within the month ranges specified. To search for a particular month, specify the same start and end month.</li> 
				<li> <i> Collection year </i> Isolates are restricted within the year ranges specified. To search for a particular year, specify the same start and end year.</li> 
			</ol> 
		</li> 
		<li> <b> Sequence type (ST) </b>
			The sequence type assigned to the isolate at each MGT level can be searched for. The sequence type is a number, optionally followed by a degenerate sequence type (dST). An example for MGT2 ST is '2', and with dST is '2.1'. <br> 
			Isolates with complete alleles have a dST value of 0 (and can be searched as, for example, MGT2 ST = '2.0'), and isolates with unresolvable/incomplete alleles have dST values. <br>   
		</li> 
		<li> <b> Clonal cluster (CC) </b> 
			Isolates within a clonal complex or cluster (CC) at a particular MGT level, differ from each other by atmost one locus within that MGT schema. CCs, specified as numeric values, can be used to restrict searched isolates to those belonging to the specfied CC at the MGT level. An example for MGT2 CC is '2'.   
		</li> 
		<li> <b> Outbreak detection cluster (ODC) </b>
			Outbreak detection clusters or complexes (ODC) are CC's defined specifically for the highest MGT level, ranging from 1 locus difference (in ODC1, hence this is equivalent to the highest MGT level CC) to 10 loci difference (in ODC10). An example is ODC10='2'. 
		</li> 
	</ol>
	<h6 class="speHeading"> Search type </h6> 
	When two or more search filters are specified, either a union ('OR' search) or an intersection ('AND' search) search can be performed between all the filters specified.      
	*/}).toString().match(/[^]*\/\*([^]*)\*\/\}$/)[1];

  return {title: "Filter isolates", body: body};
}


function helpTop5Dist(){
  let body = '<p> Clicking on each MGT level button loads a bar chart which displays the proportion of publicly available isolates within top five ST\'s in each continent. </p>';
  return {title: "Top five MGT sequence types (STs) in each continent", body: body};
}

function helpTop5DistChart(isTitle){

	let body = '<ul> <li> Shown are the top five ST\'s in each continent. </li> <li> Similarly coloured bars across continents refer to the same ST. </li> <li> <i>Hovering</i> over a coloured bar reveals the ST value, and the number of isolates containing this ST. </li> <li> <i>Clicking</i> on a coloured bar launches a search of the isolates containing the ST at the particular MGT level, and subsequently displays the results in a table. </li> <li> The proportion of isolates not within the top five ST\'s are indicated via white colouring. </li> </ul>';

  return {title: 'Chart help', body: body};
}

function helpProjDownloadApFile(){
	let body = 'The <i> allelic profile assignments </i> compressed file lists the MGT9 allelic profile assignments of isolates in this project, in a tabular format. The allele sequences of the alleles in the allelic profiles can be found in the organism home page.'; 
	return {title: 'Download table of allelic profiles', body: body}; 
}

function helpPuDownloadableData(){
  let body = 'Two types of files (updated regularly - last updated date mentioned in file name) are made available for download:<br>1. The <i> allelic profile assignments </i> compressed file lists all the publicly available isolates and their MGT9 allelic profile assignments, in a tabular format. <br>2. The <i> allele sequences </i> is a compressed folder containtaining files of allele sequences of every locus that forms part of any MGT schema.';

  return {title: 'Data available for download', body: body};
}

////////////////////// PREV. POPOVERS

$(function () {
	initVisiblePopovers();
});

function initVisiblePopovers(){
	$('[data-toggle="popover"]').popover()
	$('.popover-dismiss').popover({
		trigger: 'focus'
	});

	// console.log("instantiated popover");
}


function displayTheHelp(btnId, funcName){
	console.log("unveil");
	console.log(btnId);
	var data = funcName(false);
	var title = funcName(true);

	// Set title
	$('#'+btnId).attr('data-original-title', title);

	// Set body
	$('#'+btnId).attr('data-content', data).data('bs.popover').setContent();
}


function helpCreateEditidentifier(isTitle){
	if (isTitle == true){
		return ("Isolate");
	}
	else{
		return ('An identifier for the isolate. This field is required and must be unique within any given project.');
	}
}

function helpCreateEditprivacy_status(isTitle){
	if (isTitle == true){
		return ("Isolate's privacy status");
	}
	else{
		return ('<b> Private </b> This setting only lets you view the isolate and its associated meta data. <br> <b> Public </b> This setting lets anyone view the isolate and its associated meta data.');
	}
}

function helpCreateEditfile_forward(isTitle){
	if (isTitle == true){
		return ("Illumina forward sequencing file");
	}
	else{
		return ('Illumina sequencing results in two file. Here, the forward sequencing file is expected. An example file name is IsolateX_1.fastq.gz');
	}
}

function helpCreateEditfile_reverse(isTitle){
	if (isTitle == true){
		return ("Illumina revese sequencing file");
	}
	else{
		return ('Illumina sequencing results in two file. Here, the forward sequencing file is expected. An example file name is IsolateX_2.fastq.gz');
	}
}

function helpCreateEditfile_alleles(isTitle){
	if (isTitle == true){
		return ("Alleles file");
	}
	else{
		return ('As an alternative to providing the Illumina sequencing files, just the alleles can be provided. These alleles will be used to assign the unique MGT. <br><br> The alleles can be extracted from script reads_to_alleles.py. Details are available here: http://github.com/LanLab/MGT_reads2alleles.');
	}
}

function helpCreateEditproject(isTitle){
	if (isTitle == true){
		return ("Project");
	}
	else{
		return ('The project in which this isolate should be saved in. This field is required.');
	}
}

function helpCreateEditcontinent(isTitle){
	if (isTitle == true){
		return ("Isolation continent");
	}
	else{
		return ('The continent in which this isolate was isolated. This field is required.');
	}
}

function helpCreateEditcountry(isTitle){
	if (isTitle == true){
		return ("Isolation country");
	}
	else{
		return ('The country in which this isolate was isolated. This field is required.');
	}
}


function helpCreateEditstate(isTitle){
	if (isTitle == true){
		return ("Isolation location");
	}
	else{
		return ('The state (or sub-country) in which this isolate was isolated. <br> For e.g., "NSW" in Australia, or "England" in UK.');
	}
}

function helpCreateEditpostcode(isTitle){
	if (isTitle == true){
		return ("Isolation postcode");
	}
	else{
		return ('The postcode or zipcode in which this isolate was isolated.');
	}
}

function helpCreateEditsource(isTitle){
	if (isTitle == true){
		return ("Sample source");
	}
	else{
		return ('Sample source (or product) can be organic or non-organic. Some examples are: Eggs, Beef, Misc Food, live animal, Human. <br> To clarify, if for example, the "isolation host" is "chicken", the sample source may be "eggs". Another example, if the "isolation host" is "human", the sample source may also be "human".');
	}
}

function helpCreateEdittype(isTitle){
	if (isTitle == true){
		return ("Isolation type");
	}
	else{
		return ('The setting in which the isolate was isolated. Some examples are: Clinical, Other. <br> <br> The main goal of this field is to distinguish between human clinical samples and other samples (such as vetenary samples).');
	}
}

function helpCreateEdithost(isTitle){
	if (isTitle == true){
		return ("Isolation host organism");
	}
	else{
		return ('Species of host animal e.g. chicken, Human.');
	}
}

function helpCreateEditdisease(isTitle){
	if (isTitle == true){
		return ("Disease in isolated host");
	}
	else{
		return ('The disease that was observed in the isolated host. Some examples are: gastroenteritis, sepsis.');
	}
}

function helpCreateEditdate(isTitle){
	if (isTitle == true){
		return ("Isolation date");
	}
	else{
		return ('The date on which this isolate was isolated.');
	}
}

function helpCreateEdityear(isTitle){
	if (isTitle == true){
		return ("Isolation year");
	}
	else{
		return ('The year in which this isolate was isolated. This field is required.');
	}
}

function helpCreateEditmonth(isTitle){
	if (isTitle == true){
		return ("Isolation month");
	}
	else{
		return ('The month in which this isolate was isolated.');
	}
}

function helpCreateEditisQuery(isTitle){
	if (isTitle == true){
		return ("Query the isolate for available MGT-STs");
	}
	else{
		return ('Selecting this option results in isolates only being queried for the available MGT-STs (and any new alleles are not extracted and assigned new allele-identifiers and hence new STs). Here, new STs are not created if an ST cannot be found in the database.<br><br>This option additionally allows the upload of assemblies. Assemblies can only be queried.');
	}
}

function helpCreateEditfile_assembly(isTitle){
	if (isTitle == true){
		return ("Upload assembly file");
	}
	else{
		return ('Note: this option is only available to \'Run as query\. <br><br>The assembly pipeline used by you may differ from the one we utilize to extract alleles, and since the identification of alleles is hugely dependent on the pipeline used, and subsequently the ST assignments to an isolate, we prefer that you too use the same pipeline to extract-alleles (available publicly on github at: <a href="https://github.com/LanLab/MGT_reads2alleles">https://github.com/LanLab/MGT_reads2alleles</a>). This also prevents the contamination of our database where in multiple isolates with the same name are assigned different STs. We apologize, but this is a nomenclature database after all.');
	}
}
