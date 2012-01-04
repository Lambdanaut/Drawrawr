class Draggable
	constructor: (@title,@content) ->

	die: () ->

$(document).ready ->
	draggable = new Draggable
