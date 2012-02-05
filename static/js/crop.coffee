showPreview = (coords) ->
	rx = 100 / coords.w
	ry = 100 / coords.h

	$('#preview').css({
		width: Math.round(rx * 500) + 'px',
		height: Math.round(ry * 370) + 'px',
		marginLeft: '-' + Math.round(rx * coords.x) + 'px',
		marginTop: '-' + Math.round(ry * coords.y) + 'px'
	});

$(document).ready ->
	$('#art').Jcrop
		onChange: showPreview,
		onSelect: showPreview,
		aspectRatio: 1.2272727
