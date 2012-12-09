thumb_width  = 135 
thumb_height = 110

show_preview = (coords) ->
	rx = thumb_width  / coords.w
	ry = thumb_height / coords.h
	$("#x").val(coords.x)
	$("#y").val(coords.y)
	$("#w").val(coords.w)
	$("#h").val(coords.h)
	$('#preview').css
		width: Math.round(rx * image_width ) + 'px',
		height: Math.round(ry * image_height ) + 'px',
		marginLeft: '-' + Math.round(rx * coords.x) + 'px',
		marginTop: '-' + Math.round(ry * coords.y) + 'px'

$(document).ready ->
	$('#art').load ->
		window.image_width  = $("#art").width()
		window.image_height = $("#art").height()
		$('#art').Jcrop
			aspectRatio: thumb_width/thumb_height,
			onChange: show_preview,
			onSelect: show_preview,
			setSelect: [ 0,0,image_width,image_height ],
		show_preview(w:image_width,h:image_height)

	$("form").submit () ->
		$(".button").attr "disabled","disabled"
		m = new Modal "#crop_loading_modal"
		return 1