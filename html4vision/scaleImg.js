function scaleImg(scale) {
	"use strict";
	function imgLoaded() {
		this.style.width = this.naturalWidth*scale + "px";
		this.style.height = this.naturalHeight*scale + "px";
	}
	
	var imgs = document.querySelectorAll("img");
	for (var i = 0; i < imgs.length; i++) {
		var img = imgs[i];
		if (img.complete || img.naturalWidth > 0) {
			img.style.width = img.naturalWidth*scale + "px";
			img.style.height = img.naturalHeight*scale + "px";
		} else {
			img.onload = imgLoaded;
		}
	}
}