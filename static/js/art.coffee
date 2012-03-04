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
				beforeSend: -> 
					favButton.text(" - Loading - ")
				complete: (msg) ->
					if favButton.attr("data-state") == "fav"
						favButton.text "- Unfavorite"
						favButton.attr "data-state", "unfav"
					else
						favButton.text "+ Favorite"
						favButton.attr "data-state", "fav"

	### Watch Button ###
	watchButton = $("#watchButton")
	watchButton.click ->
		$.ajax
			url:  "/users/watch",
			type: "POST",
			data: "watchedUser=" + $("#author").attr("data-name"),
			beforeSend: -> 
				watchButton.text " - Loading - "
			complete: (msg) ->
				if watchButton.attr("data-state") == "watch"
					watchButton.text "- Unwatch"
					watchButton.attr "data-state","unwatch"
				else
					watchButton.text "+ Watch"
					watchButton.attr "data-state","watch"
