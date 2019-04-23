(function (){
	"use strict";

	function toggleElements(className) {
		var eles = document.getElementsByClassName(className);
		if (eles.length) {
			var visStr = eles[0].style.visibility === "hidden" ? "visible": "hidden";
			for(var i = 0; i < eles.length; i++)
				eles[i].style.visibility = visStr;
		}
	}

	var eles = document.getElementsByClassName("overlay");
	for(var i = 0; i < eles.length; i++)
		eles[i].parentElement.onclick = toggleElements.bind(null, "overlay");
})();
