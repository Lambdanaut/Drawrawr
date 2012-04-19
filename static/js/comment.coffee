$(document).ready ->
	$(".comment .replyButton").click () ->
		$(this).parent().find("form").slideDown("slow")
