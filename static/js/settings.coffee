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


allowedIn = () ->
	

### Returns a serialized version of the layout ###
serializeLayout = () ->
	data = ""
	$("#profileTop, #profileLeftCol, #profileRightCol, #profileBottom, #profileHidden").each (idx,elem) ->
		$(elem).children(".draggable").each (idx2,elem2) ->
			data += $(elem2).attr("id") + "=" + $(elem).attr("data-loc") + "&"
	data
		
serializeLayoutOrder = () ->
	data = ""
	$("#profileTop, #profileLeftCol, #profileRightCol, #profileBottom, #profileHidden").each (idx,elem) ->
		$(elem).children(".draggable").each (idx2,elem2) ->
			data += $(elem2).attr("id") + "=" + idx2 + "&"
	data

updateLocation = (position) ->
	lat = position.coords.latitude
	lon = position.coords.longitude

	$("#latitude").val lat
	$("#longitude").val lon

getLocation = () ->
	navigator.geolocation.getCurrentPosition updateLocation

$(document).ready ->
	### Gender ###
	$("#changeGender").val($("#defaultGender").val())

	### Geolocation ###
	if Modernizr.geolocation
		$("#getLocation").click getLocation
	else
		$("#getLocation").attr "disabled","disabled"
		$("#getLocation").css "display","none"
		$("#noLocationBrowser").css "display","block"

	$("#whyLocation").click () ->
		box = new Helpbox "#whyHelp"

	### Color Theme ###
	$("#changeColorTheme").change ->
		$("#colorThemeStyle").attr("href","/static/css/userpages/" + $(this).val() + ".css")
	$("#changeColorTheme").val($("#defaultTheme").attr("data-theme"))
	$("#changeColorTheme").trigger("change")

	### Userpage Layout ###	
	$("#profileTop, #profileLeftCol, #profileRightCol, #profileBottom, #profileHidden").sortable(
		connectWith: ".dragBox"
		update: () -> 
			$("#changeLayout").val(serializeLayout())
			$("#changeLayoutOrder").val(serializeLayoutOrder())
	).disableSelection()

	### Beta Keys ###
	$("#generateNewInvite").click () ->
		conf = confirm "Are you sure you want to spend one of your invites? "
		if conf
			$.ajax
				url: "/admin/generateBetaPass",
				type: "POST",
				beforeSend: () ->
					$("#betaLoader").css("display","inline")
				success: (data) ->
					$("#betaKeyList").append("<li style='display:none'>" + data + "</li>")
					$("#betaKeyList li:last-child").fadeIn "slow", ->
						$("#betaLoader").css("display","none")
