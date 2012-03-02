thumbWidth  = 135 
thumbHeight = 110

showPreview = (coords) ->
	rx = thumbWidth  / coords.w
	ry = thumbHeight / coords.h
	$("#x").val(coords.x)
	$("#y").val(coords.y)
	$("#w").val(coords.w)
	$("#h").val(coords.h)
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
			onSelect: showPreview,
			setSelect:   [ 0,0,imageWidth,imageHeight ],
		showPreview(w:imageWidth,h:imageHeight)
