watchText   = " + watch "
unwatchText = " - unwatch "

$(document).ready ->
	### Sets the watch button's text ###
	if $("#watchUserButton").attr("data-state") == "True"
		$("#watchUserButton").text(unwatchText)
	else
		$("#watchUserButton").text(watchText)

	### Watch button functionality ###
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
					### Hide user from watch list ###
					$('#watchers img[title="' + $("#loggedInUsername").attr("data-name") + '"]').fadeOut "slow", () ->
						$(this).remove()
				else
					$("#watchUserButton").attr("data-state","True")
					$("#watchUserButton").text(unwatchText)
					### Show user in watch list ###
					$("#watchers p").remove()
					loggedInUsername  = $("#loggedInUsername").attr("data-name")
					loggedInLowername = loggedInUsername.toLowerCase()
					$("#watchers").prepend '<a href="/{{ user }}"><img src="/icons/' + loggedInLowername + '" alt="' + loggedInUsername + '\'s icon" class="tinyIcon" style="float: left;margin: 2px; display: none;" title="' + loggedInUsername + '"></a>'
					$('#watchers img[title="' + $("#loggedInUsername").attr("data-name") + '"]').fadeIn("slow")
