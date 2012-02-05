thumbWidth  = 135 
thumbHeight = 110

showPreview = (coords) ->
	rx = thumbWidth  / coords.w
	ry = thumbHeight / coords.h
	$('#preview').css
		width: Math.round(rx * imageWidth ) + 'px',
		height: Math.round(ry * imageHeight ) + 'px',
		marginLeft: '-' + Math.round(rx * coords.x) + 'px',
		marginTop: '-' + Math.round(ry * coords.y) + 'px'

$(document).ready ->
	$('#art').load ->
		window.imageWidth  = $("#art").width()
		window.imageHeight = $("#art").height()
		$('#art').Jcrop
			aspectRatio: thumbWidth/thumbHeight,
			onChange: showPreview,
			onSelect: showPreview
		showPreview(w:imageWidth,h:imageHeight)


