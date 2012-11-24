watch_text   = " + watch "
unwatch_text = " - unwatch "

$(document).ready ->
	### Sets the watch button's text ###
	if $("#watch_user_button").attr("data-state") == "True"
		$("#watch_user_button").text(unwatch_text)
	else
		$("#watch_user_button").text(watch_text)

	### Watch button functionality ###
	$("#watch_user_button").click ->
		$.ajax
			url:  "/users/watch",
			type: "POST",
			data: "watched_user=" + $("#username").attr("data-name"),
			beforeSend: -> 
				$("#watch_user_button").text(" - Loading - ")
			complete: (msg) ->
				if $("#watch_user_button").attr("data-state") == "True"
					$("#watch_user_button").attr("data-state","False")
					$("#watch_user_button").text(watch_text)
					### Hide user from watch list ###
					$('#watchers img[title="' + $("#logged_in_username").attr("data-name") + '"]').fadeOut "slow", () ->
						$(this).remove()
				else
					$("#watch_user_button").attr("data-state","True")
					$("#watch_user_button").text(unwatch_text)
					### Show user in watch list ###
					$("#watchers p").remove()
					logged_in_username  = $("#logged_in_username").attr("data-name")
					logged_in_lowername = logged_in_username.toLowerCase()
					$("#watchers").prepend '<a href="/' + logged_in_lowername + '"><img src="/icons/' + logged_in_lowername + '" alt="' + logged_in_username + '\'s icon" class="tiny_icon" style="float: left;margin: 2px; display: none;" title="' + logged_in_username + '"></a>'
					$('#watchers img[title="' + $("#logged_in_username").attr("data-name") + '"]').fadeIn("slow")
