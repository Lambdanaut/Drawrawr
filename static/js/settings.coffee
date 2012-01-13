/* What items belong to what sets */
/* setA :: T L B */
/* 	profile */
/* setB :: T L B H */
/* 	gallery */
/*	comments */
/* setC :: R H */
/* 	watches */
/* 	friends */
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
	comment      : 'd',
	clubs        : 'e',
	chars        : 'f',
	playlist     : 'g',
	interactions : 'g'


allowedIn = () ->
	

$(document).ready ->
	/* Gender */
	$("#changeGender").val($("#defaultGender").val())	

	/* Userpage Layout */	
	$("#profileTop, #profileLeftCol, #profileRightCol, #profileBottom, #profileHidden").sortable(
		connectWith: ".dragBox"
	).disableSelection()
