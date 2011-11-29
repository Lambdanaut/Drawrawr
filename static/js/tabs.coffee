class Tabs
	constructor: (firstTab) ->
		if firstTab == undefined
			@selectTab $("#tabs ul li:first-child").attr "id"
		else
			 @selectTab firstTab

		$("#tabs ul li").each (i, self) =>
			$("#tab-" + ($(self).attr "id")).css("display","none")
			$(self).click () =>
				@selectTab $(self).attr "id"

	selectTab: (tab) ->
		$("#tabs .tab-selected").removeAttr "class"
		$("#" + tab).attr "class","tab-selected"
		$("#tab-content").html $("#tab-"+tab).html()

$(document).ready ->
	tabs = new Tabs
