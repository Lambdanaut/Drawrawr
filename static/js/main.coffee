class @Header
	constructor: (@glued) ->
		@switch_glue()

		$("#set-header").click () => 
			@switch_glue()
			@update_database_glue()

	switch_glue: () ->
		if @glued
			@unglue()
		else @glue()
		
	update_database_glue: () ->
		$.ajax
			url:  "/users/glue",
			type: "POST",
			data: "glued=" + (@glued + 0)

	### Glue the header to the top of the page ###
	glue: () -> 
		@glued=true
		
		headerCSS = 
			"position":"absolute"

		$("#header").css headerCSS

		$("#set-header").html "↓"

	### Unglue the header from the top of the page ###
	unglue: () -> 
		@glued=false
		headerCSS = 
			"position":"fixed"

		$("#header").css headerCSS

		$("#set-header").html "↑"

class @Notice
	constructor: (@title,@content) ->
		$("#notice").slideDown "slow"
		
		$("#notice").html "<span class='close'></span><h4>" + @title + "</h4><p>" + @content + "</p>"

		$("#notice .close").click @die

	die: () ->
		$("#notice").slideUp "fast", () =>
			$("#notice").hide()

class @Modal
	constructor: (@modalDiv) ->
		$(".modal .close").click @die
		
		@show()

	show: () ->
		@visible=true
		$(@modalDiv).css("display","block")
		$(".modal").css("display","block")

	die: () ->
		@visible=false
		$(".modal aside").css("display","none")
		$(".modal").css("display","none")

class @Help_Box
	constructor: (@help_div) ->
		$(@help_div).click @die

		$(@help_div).addClass "help_box"
		$(@help_div).addClass "round_box"

		@show()

	show: () ->
		$(@help_div).css "display","block"

	die: () =>
		$(@help_div).css "display","none"

$(document).ready ->
	### Keeps the copyright up to date on the current year ###
	date = new Date()
	$("#copyright-date").html date.getFullYear()

	### Refreshes relative dates ###
	$("body").timeago();

	### Set up the header ###
	header = new Header false
	if $("#glued").attr("data-glued") == "0"
		header.switch_glue()

	### Flashed Messages ###
	$("#flashed li").each ->
		new Notice "MESSAGE" ,$(this).text()

	### Registration ###		
	if $("#register_captcha").length
		Recaptcha.create $("#register_captcha").attr("data-publicKey"), "register_captcha", theme : 'custom', custom_theme_widget: 'recaptcha_widget', callback: Recaptcha.focus_response_field
	$("#register-button").click () =>
		signupModal = new Modal "#register-form"
		$('form:not(.filter) :input:visible:first').focus()

	$("#register-form form").submit () =>
		form = $("#register-form form").serialize()
		$.ajax
			url:  "/users/signup",
			type: "POST",
			data: form,
			success: (data) =>
				if data == "1"
					### SUCCESS ###
					window.location = "/users/welcome"
				else if data == "0"
					new Notice "Woops!", "There was a serious error processing your signup. Try refreshing the page and trying again. "
				else if data == "2"
					new Notice "Mixup!", "That Username is already taken! Try a different one. "
				else if data == "3"
					new Notice "I H8 Passwords!", "Your passwords didn't match up! Try typing them again. "
				else if data == "4"
					new Notice "Legal Jargon!", "You must read and agree to our Terms of Service!"
				else if data == "5"
					new Notice "Woops!", "Your Captcha answer was invalid. Try again! "
				else if data == "6"
					new Notice "B8a C0d3!", "We didn't recognize your <strong>Beta Code</strong>. It seems to be inactive! "
				else if data == "7"
					new Notice "Lmao Hacker!", "You already seem to have an account with us. "
		false

	### Login ###
	$("#login-button").click () =>
		loginModal = new Modal "#login-form"
		$('form:not(.filter) :input:visible:first').focus()
		
	$("#login-form form").submit () =>
		form = $("#login-form form").serialize()
		$.ajax
			url:  "/users/login",
			type: "POST",
			data: form,
			success: (data) =>
				if data == "1"
					location.reload true
				else if data == "2"
					new Notice "WHAT Username!?", "That username <em>DOESN'T</em> exist. Believe me, I checked! Perhaps you're spelling it wrong. "
				else if data == "3"
					new Notice "Wrong Password", "That username exists, but that is <em>NOT</em> the correct password for their account. Try again, and remember, the password is <a href=\"http://en.wikipedia.org/wiki/Case_sensitivity\" target=\"_blank\">CASE SENSITIVE</a>!"
		false

	### Logout ###
	$("#logout-button").click () =>
		$.ajax
			url:  "/users/logout",
			type: "POST",
			success: (data) =>
				if data == "1"
					window.location = "/"
