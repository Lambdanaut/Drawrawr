(function() {
  var Tabs;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  Tabs = (function() {
    function Tabs(firstTab) {
      var anchor;
      $("#tabs ul li").each(__bind(function(i, self) {
        $("#tab-" + ($(self).attr("id"))).css("display", "none");
        return $(self).click(__bind(function() {
          return this.selectTab($(self).attr("id"));
        }, this));
      }, this));
      if (firstTab === void 0) {
        anchor = window.location.hash.replace("#-", "");
        if (anchor !== "") {
          this.currentTab = anchor;
        } else {
          this.currentTab = $("#tabs ul li:first-child").attr("id");
        }
      } else {
        this.currentTab = firstTab;
      }
      this.selectTab(this.currentTab);
    }
    Tabs.prototype.selectTab = function(tab) {
      $("#tabs .tab-selected").removeAttr("class");
      $("#" + tab).attr("class", "tab-selected");
      $("#tab-" + this.currentTab).css("display", "none");
      $("#tab-" + tab).css("display", "inline");
      return this.currentTab = tab;
    };
    return Tabs;
  })();
  $(document).ready(function() {
    var tabs;
    return tabs = new Tabs;
  });
}).call(this);
