$(document).ready ->
	$("#artOptions").change () ->
		$("#ignore").remove()
		$("#submitTitle").text($(this).val())
		$(".artArea").css "display","none"
		$("#" + $(this).val().toLowerCase() + "Area").css "display","inline"
