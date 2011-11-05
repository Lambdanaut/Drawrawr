class Header
	constructor: (@glued) ->
		@switchGlue()

		$("#set-header").click () => @switchGlue()

	switchGlue: () ->
		if @glued
			@unglue()
		else @glue()

	/* Glue the header to the top of the page */
	glue: () -> 
		@glued=true

		headerCSS = 
			"position":"relative",
			"top":"auto","left":"auto","right":"auto",
			"margin":"5px 15px 4px 15px"
		navCSS =
			"margin":"0px 15px 4px 15px"

		$("#header").css headerCSS
		$("#navigation").css navCSS

		$("#header").addClass("roundBox")

		$("#set-header").html "↓"

	/* Unglue the header from the top of the page */
	unglue: () -> 
		@glued=false
		headerCSS = 
			"position":"fixed",
			"top":"5px","left":"0px","right":"0px",
			"margin":"auto"
		navCSS =
			"margin":"50px 15px 4px 15px"

		$("#header").css headerCSS
		$("#navigation").css navCSS

		$("#header").removeClass("roundBox")

		$("#set-header").html "↑"

class Notice
	constructor: (@title,@content) ->
		$("#notice").slideDown "slow"
		
		$("#notice").html "<span class='close'></span><h4>" + @title + "</h4><p>" + @content + "</p>"

		$("#notice .close").click @die

	die: () ->
		$("#notice").slideUp "fast", () =>
			$("#notice").hide()

class Modal
	constructor: (@title,@content) ->
		$("#modal div").html "<span class='close'></span><h4>" + @title + "</h4><p>" + @content + "</p>"

		$("#modal .close").click @die

		@show()
	show: () ->
		@visible=true
		$("#modal").css("visibility","visible")
	die: () ->
		@visible=false
		$("#modal").css("visibility","hidden")

$(document).ready ->
	/* Keeps the copyright up to date on the current year */
	date = new Date()
	$("#copyright-date").html date.getFullYear()
	
	/* Registration */
	$("#register-button").click () =>
		signupModal = new Modal "CREATE A NEW ACCOUNT", $("#register-form").html()
		
		$("#modal button").click () =>
			$.ajax 
				url:  "/users/signup",
				type: "POST",
				data: $("#modal form").serialize(),
				success: (data) =>
					alert data

	/* Login */
	$("#login-button").click () =>
		loginModal = new Modal "LOGIN", $("#login-form").html()

		$("#modal button").click () =>
			$.ajax
				url:  "/users/login",
				type: "POST",
				data: $("#modal form").serialize(),
				success: (data) =>
					alert data

	/* Set up the header */
	header = new Header false
