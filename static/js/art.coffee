$(document).ready ->
	art = $("#art")
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

