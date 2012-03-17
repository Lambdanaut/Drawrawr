$(document).ready ->
	art = $("#art")
	### Image Full View ###
	if art.attr("data-type") == "image"
		art.css
			"max-width": "80%"
			"cursor": "pointer"
			"max-height": "1000px"
		$("#previewText").text "Click Image to Full View"

		art.click ->
			if art.attr("data-size") == "small"
				$("#previewText").slideUp(200)
				art.fadeOut 100, ->
					art.css
						"max-width": "None"
						"max-height": "None"
					art.fadeIn 100, ->
						art.attr "data-size","full"
			else
				$("#previewText").slideDown(200)
				art.fadeOut 100, ->
					art.css
						"max-width": "80%"
						"max-height": "1000px"
					art.fadeIn 100, ->
						art.attr "data-size","small"

	### Favorites ###
	favButton = $("#favButton")
	favButton.click ->
		$.ajax
			url: "/art/" + $("#artID").attr("data-state") + "/favorite",
			type: "POST"
			complete: (msg) ->
				if favButton.attr("data-state") == "fav"
					favButton.attr "src","/static/images/unfavoritebutton.png"
					favButton.attr "data-state", "unfav"
				else
					favButton.attr "src", "/static/images/favoritebutton.png"
					favButton.attr "data-state", "fav"

	### Watch Button ###
	watchButton = $("#watchButton")
	watchButton.click ->
		$.ajax
			url:  "/users/watch",
			type: "POST",
			data: "watchedUser=" + $("#author").attr("data-name"),
			complete: (msg) ->
				if watchButton.attr("data-state") == "watch"
					watchButton.attr "src","/static/images/unwatchbutton.png"
					watchButton.attr "data-state","unwatch"
				else
					watchButton.attr "src","/static/images/watchbutton.png"
					watchButton.attr "data-state","watch"

	### Delete Button ###
	$("#deleteButton").click ->
		conf = confirm "Are you sure you want to delete this artwork? "
		if conf
			$.ajax
				type: "DELETE",
				complete: (msg) ->
					window.location = $("#author").attr "data-name"

