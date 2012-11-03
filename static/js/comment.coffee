$(document).ready ->
	### Comment Button ###
	$(".leaveCommentButton").click () ->
		$("#leaveCommentForm").html $("#replyFormTemplate").clone().html()
		$(this).fadeOut "fast", =>
			$("#leaveCommentForm").fadeIn("fast")
			$("#leaveCommentForm").find("textarea").focus()	

	### Reply Button ###
	$(".comment .replyButton").click () ->
		reply = $(this).parent().find(".reply")
		reply.html $("#replyFormTemplate").clone().html()
		form = reply.find("form")
		form.find(".parentInput").val $(this).parent().find(".parentData").attr("data-value")
		form.find(".commentMapInput").val $(this).parent().find(".commentMapData").attr("data-value")

		$(this).hide 0, () =>
			reply.fadeIn("fast")
			reply.find("textarea").focus()
