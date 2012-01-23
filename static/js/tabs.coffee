class Tabs
	constructor: (firstTab) ->
		$("#tabs ul li").each (i, self) =>
			$("#tab-" + ($(self).attr "id")).css("display","none")
			$(self).click () =>
				@selectTab $(self).attr "id"

		if firstTab == undefined
			anchor =  window.location.hash.replace("#", "")
			if anchor != ""
				@currentTab = anchor
			else 
				@currentTab = $("#tabs ul li:first-child").attr "id"
		else
			@currentTab = firstTab

		@selectTab @currentTab
		
	selectTab: (tab) ->
		$("#tabs .tab-selected").removeAttr "class"
		$("#" + tab).attr "class","tab-selected"
		$("#tab-"+@currentTab).css("display","none")
		$("#tab-"+tab).css("display","inline")
		@currentTab = tab

$(document).ready ->
	tabs = new Tabs
