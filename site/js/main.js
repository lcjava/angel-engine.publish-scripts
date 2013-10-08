$(document).ready(function() {
	// set images up for swap if we're on a retina device
	var isRetina = false;
	var mediaQuery = "(-webkit-min-device-pixel-ratio: 1.5),\
			  (min--moz-device-pixel-ratio: 1.5),\
			  (-o-min-device-pixel-ratio: 3/2),\
			  (min-resolution: 1.5dppx)";

	if (window.devicePixelRatio > 1)
		isRetina = true;

	if (window.matchMedia && window.matchMedia(mediaQuery).matches)
		isRetina = true;

	$('noscript[data-large][data-small]').each(function() {
		var datums = $(this).data();
		var src = isRetina ? datums['large'] : datums['small'];
		delete datums['large'];
		delete datums['small'];

		var attrs = "";
		for (var key in datums) {
			attrs += ' ' + key + '="' + datums[key] + '"';
		}

		$('<img src="' + src + '"' + attrs + ' />').insertAfter($(this));
	});
	// \retina swap
});
