### What items belong to what sets ###
### setA :: T L B ###
### 	profile ###
### setB :: T L B H ###
### 	gallery ###
###	comments ###
### setC :: R H ###
### 	watches ###
### 	friends ###
sets =
	a : ['t','l','r','b','h'],
	b : ['r','h'],
	c : ['t','l','b','h'],
	d : ['t','b','h'],
	e : ['r','b','h'],
	f : ['r','l','h'],
	g : ['t','r','b','h']

inSet =
	shop         : 'a',
	shout        : 'a',
	watches      : 'b',
	friends      : 'b',
	nearby       : 'b',
	awards       : 'b',
	tips         : 'b',
	profile      : 'c',
	gallery      : 'c',
	favorites    : 'c',
	journal      : 'c',
	comments     : 'd',
	clubs        : 'e',
	chars        : 'f',
	playlist     : 'g',
	interactions : 'g'


allowed_in = () ->
	

### Returns a serialized version of the layout ###
serialize_layout = () ->
	data = ""
	$("#profile_top, #profile_left_col, #profile_right_col, #profile_bottom, #profile_hidden").each (idx,elem) ->
		$(elem).children(".draggable").each (idx2,elem2) ->
			data += $(elem2).attr("id") + "=" + $(elem).attr("data-loc") + "&"
	data
		
serialize_layout_order = () ->
	data = ""
	$("#profile_top, #profile_left_col, #profile_right_col, #profile_bottom, #profile_hidden").each (idx,elem) ->
		$(elem).children(".draggable").each (idx2,elem2) ->
			data += $(elem2).attr("id") + "=" + idx2 + "&"
	data

update_location = (position) ->
	lat = position.coords.latitude
	lon = position.coords.longitude

	$("#latitude").val lat
	$("#longitude").val lon

get_location = () ->
	navigator.geolocation.getCurrentPosition update_location

$(document).ready ->
	### Gender ###
	$("#change_gender").val($("#default_gender").val())

	### Geolocation ###
	if Modernizr.geolocation
		$("#get_location").click get_location
	else
		$("#get_location").attr "disabled","disabled"
		$("#get_location").css "display","none"
		$("#no_location_browser").css "display","block"

	$("#why_location").click () ->
		box = new Help_Box "#whyHelp"

	### Color Theme ###
	$("#change_color_theme").change ->
		$("#colorThemeStyle").attr("href","/static/css/userpages/" + $(this).val() + ".css")
	$("#change_color_theme").val($("#default_theme").attr("data-theme"))
	$("#change_color_theme").trigger("change")

	### Userpage Layout ###	
	$("#profile_top, #profile_left_col, #profile_right_col, #profile_bottom, #profile_hidden").sortable(
		connectWith: ".drag_box"
		update: () -> 
			$("#change_layout").val(serialize_layout())
			$("#change_layout_order").val(serialize_layout_order())
	).disableSelection()

	### Beta Keys ###
	$("#generate_new_invite").click () ->
		conf = confirm "Are you sure you want to spend one of your invites? "
		if conf
			$.ajax
				url: "/admin/generate_beta_pass",
				type: "POST",
				beforeSend: () ->
					$("#beta_loader").css("display","inline")
				success: (data) ->
					$("#beta_key_list").append("<li style='display:none'>" + data + "</li>")
					$("#beta_key_list li:last-child").fadeIn "slow", ->
						$("#beta_loader").css("display","none")
