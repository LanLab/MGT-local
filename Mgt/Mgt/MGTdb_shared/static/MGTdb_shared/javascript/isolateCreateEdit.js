// import {showHideAssembly} from './modules/isolateCreateEditFns.js'

// window.Salmonella_showHideAssembly = showHideAssembly;

window.showHideAssembly = function() {
    if (document.getElementById('id_isQuery').checked) {
        document.getElementById('row_assembly').style.visibility = 'visible';
        document.getElementById('id_privacy_status').value = 'PV'
    }
    else {
        document.getElementById('row_assembly').style.visibility = 'hidden';
    }
}
