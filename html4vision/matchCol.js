function matchCol(matchColId, scale) {
	"use strict";
    function setRowImgSize(row, wStr, hStr) {
        for (var c = 0; c < row.cells.length; c++) {
            var ele = row.cells[c].firstElementChild;
			if (!ele) continue;
			if (ele.tagName === "DIV")
				ele.style.width = wStr;
                ele.style.height = hStr;
				for (var i = 0; i < ele.children.length; i++)
					if (ele.children[i] && ele.children[i].tagName === "IMG") {
						ele.children[i].style.width = wStr;
						ele.children[i].style.height = hStr;
					}
            if (ele.tagName === "IMG") {
                ele.style.width = wStr;
                ele.style.height = hStr;
            }
        }
    }
	
	function imgLoaded(row) {
		var wStr = this.naturalWidth*scale + "px";
		var hStr = this.naturalHeight*scale + "px";
		setRowImgSize(row, wStr, hStr);
	}
	
	var tables = document.querySelectorAll("table.html4vision");
	for (var t = 0; t < tables.length; t++) {
		var table = tables[t];
		for (var r = 1; r < table.rows.length; r++) {
			var row = table.rows[r];
			var ele = row.cells[matchColId].firstElementChild;
			if (!ele) continue;
			if (ele.tagName === "DIV")
				ele = ele.firstElementChild;
			if (!ele || ele.tagName !== "IMG") continue;
			if (ele.complete || ele.naturalWidth > 0) {
				var wStr = ele.naturalWidth*scale + "px";
				var hStr = ele.naturalHeight*scale + "px";
				setRowImgSize(row, wStr, hStr);
			} else {
                ele.onload = imgLoaded.bind(ele, row);
			}
		}
	}
}