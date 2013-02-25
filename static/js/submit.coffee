$(document).ready ->
	$("#art_options").change () ->
		$("#ignore").remove()
		$("#submit_title").text($(this).val())
		$(".art_area").css "display","none"
		$("#" + $(this).val().toLowerCase() + "_area").css "display","inline"

	$("form").submit () ->
		$(".upload_button").attr "disabled","disabled"
		m = new Modal "#submit_loading_modal"
		return 1