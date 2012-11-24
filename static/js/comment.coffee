$(document).ready ->
	### Comment Button ###
	$(".leave_comment_button").click () ->
		$("#leave_comment_form").html $("#reply_form_template").clone().html()
		$(this).fadeOut "fast", =>
			$("#leave_comment_form").fadeIn("fast")
			$("#leave_comment_form").find("textarea").focus()	

	### Reply Button ###
	$(".comment .reply_button").click () ->
		reply = $(this).parent().find(".reply")
		reply.html $("#reply_form_template").clone().html()
		form = reply.find("form")
		form.find(".parent_input").val $(this).parent().find(".parentData").attr("data-value")
		form.find(".comment_map_input").val $(this).parent().find(".comment_map_data").attr("data-value")

		$(this).hide 0, () =>
			reply.fadeIn("fast")
			reply.find("textarea").focus()
