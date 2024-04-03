export {getRandomColor};

function mulberry32(a) {

      var t = a += 0x6D2B79F5;
      t = Math.imul(t ^ t >>> 15, t | 1);
      t ^= t + Math.imul(t ^ t >>> 7, t | 61);
      return ((t ^ t >>> 14) >>> 0) / 4294967296;

}

function xoshiro128ss(a, b, c, d) {
    return function() {
        var t = b << 9, r = a * 5; r = (r << 7 | r >>> 25) * 9;
        c ^= a; d ^= b;
        b ^= c; a ^= d; c ^= t;
        d = d << 11 | d >>> 21;
        return (r >>> 0) / 4294967296;
    }
}


// Note: Not random, gets color based on key!! 
function getRandomColor(stVal, j, opacity) {
  var letters = '0123456789ABCDEF';
  var color = '#';
  for (var i = 0; i < 6; i++) {
    // color += letters[Math.floor(Math.random() * 16)];
	let val = (mulberry32(parseInt(stVal+i + j)) * 16) ;
	// console.log(numToColor(val));
	// color = numToColor(val);
	color += letters[Math.floor(val)];
	// color += letters[Math.floor(JSF(parseInt(stVal))() * (i+1))];

  }

  let rgbaCol = hexToRgbA(color, opacity);
  return rgbaCol;
}



function hexToRgbA(hex, opacity){
    var c;
    if(/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)){
        c= hex.substring(1).split('');
        if(c.length== 3){
            c= [c[0], c[0], c[1], c[1], c[2], c[2]];
        }
        c= '0x'+c.join('');
        return 'rgba('+[(c>>16)&255, (c>>8)&255, c&255].join(',')+',' + opacity + ')';
    }
    throw new Error('Bad Hex');
}
