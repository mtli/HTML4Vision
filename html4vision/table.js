function addImgSize(matchColId, scale) {
	"use strict";
    function setRowImgSize(row, wStr, hStr) {
        for (var c = 0; c < row.cells.length; c++) {
            var ele = row.cells[c].firstElementChild;
            if (ele && ele.tagName === "IMG") {
                ele.style.width = wStr;
                ele.style.height = hStr;
            }
        }
    }
	
	function imgLoaded(row) {
		var wStr = String(this.naturalWidth*scale) + "px";
		var hStr = String(this.naturalHeight*scale) + "px";
		setRowImgSize(row, wStr, hStr);
	}
	
	var tables = document.querySelectorAll("table.html4vision");
	for (var t = 0; t < tables.length; t++) {
		var table = tables[t];
		for (var r = 1; r < table.rows.length; r++) {
			var row = table.rows[r];
			var tdChild = row.cells[matchColId].firstElementChild;
			if (!tdChild || tdChild.tagName !== "IMG") continue;
			if (tdChild.complete || tdChild.naturalWidth > 0) {
				var wStr = String(tdChild.naturalWidth*scale) + "px";
				var hStr = String(tdChild.naturalHeight*scale) + "px";
				setRowImgSize(row, wStr, hStr);
			} else {
                tdChild.onload = imgLoaded.bind(tdChild, row);
			}
		}
	}
}