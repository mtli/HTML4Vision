function toggleElements(className) {
	"use strict";
	var eles = document.getElementsByClassName(className);
	var visStr = eles[0].style.visibility === "hidden" ? "visible": "hidden";
	for(var i = 0; i < eles.length; i++)
		eles[i].style.visibility = visStr;
}
document.onclick = toggleElements.bind(null, "overlay");
