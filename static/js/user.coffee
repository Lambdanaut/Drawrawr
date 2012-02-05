watchText   = " + watch "
unwatchText = " - unwatch "

$(document).ready ->
	/* Sets the watch button's text */
	if $("#watchUserButton").attr("data-state") == "True"
		$("#watchUserButton").text(unwatchText)
	else
		$("#watchUserButton").text(watchText)

	/* Watch button functionality */
	$("#watchUserButton").click ->
		$.ajax
			url:  "/users/watch",
			type: "POST",
			data: "watchedUser=" + $("#username").attr("data-name"),
			beforeSend: -> 
				$("#watchUserButton").text(" - Loading - ")
			complete: (msg) ->
				if $("#watchUserButton").attr("data-state") == "True"
					$("#watchUserButton").attr("data-state","False")
					$("#watchUserButton").text(watchText)
				else
					$("#watchUserButton").attr("data-state","True")
					$("#watchUserButton").text(unwatchText)
