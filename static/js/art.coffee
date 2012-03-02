$(document).ready ->
	art = $("#art")
	# Image Full View
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

	# Favorites
	favButton = $("#favButton")
	favButton.click ->
		if favButton.attr("data-state") == "fav"
			favButton.html "- Unfavorite"
			favButton.attr "data-state", "unfav"
			$.ajax
				url: "/art/" + $("#artID").attr("data-state") + "/favorite",
				type: "POST"
		else
			favButton.html "+ Favorite"
			favButton.attr "data-state", "fav"
			$.ajax
				url: "/art/" + $("#artID").attr("data-state") + "/favorite",
				type: "POST"
