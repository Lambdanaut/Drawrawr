$(document).ready ->
	art = $("#art")
	### Image Full View ###
	if art.attr("data-type") == "image"
		art.css
			"max-width": "80%"
			"cursor": "pointer"
			"max-height": "1000px"
		$("#preview_text").text "Click Image to Full View"

		art.click ->
			if art.attr("data-size") == "small"
				$("#preview_text").slideUp(200)
				art.fadeOut 100, ->
					art.css
						"max-width": "None"
						"max-height": "None"
					art.fadeIn 100, ->
						art.attr "data-size","full"
			else
				$("#preview_text").slideDown(200)
				art.fadeOut 100, ->
					art.css
						"max-width": "80%"
						"max-height": "1000px"
					art.fadeIn 100, ->
						art.attr "data-size","small"

	### Favorites ###
	fav_button = $("#fav_button")
	fav_button.click ->
		$.ajax
			url: "/art/" + $("#art_ID").attr("data-state") + "/favorite",
			type: "POST"
			complete: (msg) ->
				if fav_button.attr("data-state") == "fav"
					fav_button.attr "src","/static/images/unfavorite_button.png"
					fav_button.attr "data-state", "unfav"
				else
					fav_button.attr "src", "/static/images/favorite_button.png"
					fav_button.attr "data-state", "fav"

	### Watch Button ###
	watchButton = $("#watchButton")
	watchButton.click ->
		$.ajax
			url:  "/users/watch",
			type: "POST",
			data: "watched_user=" + $("#author").attr("data-name"),
			complete: (msg) ->
				if watchButton.attr("data-state") == "watch"
					watchButton.attr "src","/static/images/unwatch_button.png"
					watchButton.attr "data-state","unwatch"
				else
					watchButton.attr "src","/static/images/watch_button.png"
					watchButton.attr "data-state","watch"

	### Feature Button ###
	$("#featureButton").click ->
		featureModal = new Modal "#feature_art_modal"

	### Delete Button ###
	$("#delete_button").click ->
		conf = confirm "Are you sure you want to delete this artwork? "
		if conf
			$.ajax
				type: "DELETE",
				complete: (status,msg) ->
					if msg is "success"
						window.location = "/" + $("#author").attr "data-name"

	### Flash Animation ###
	flash_animation = $("#flash_animation")
	if flash_animation.length
		flash_src = flash_animation.data "src" 
		swfobject.embedSWF(flash_src, "flash_animation", "10%", "10%", "9.0.0","expressInstall.swf", {}, {}, {});