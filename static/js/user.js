(function() {
  var unwatchText, watchText;

  watchText = " + watch ";

  unwatchText = " - unwatch ";

  $(document).ready(function() {
    /* Sets the watch button's text
    */    if ($("#watchUserButton").attr("data-state") === "True") {
      $("#watchUserButton").text(unwatchText);
    } else {
      $("#watchUserButton").text(watchText);
    }
    /* Watch button functionality
    */
    return $("#watchUserButton").click(function() {
      return $.ajax({
        url: "/users/watch",
        type: "POST",
        data: "watchedUser=" + $("#username").attr("data-name"),
        beforeSend: function() {
          return $("#watchUserButton").text(" - Loading - ");
        },
        complete: function(msg) {
          if ($("#watchUserButton").attr("data-state") === "True") {
            $("#watchUserButton").attr("data-state", "False");
            return $("#watchUserButton").text(watchText);
          } else {
            $("#watchUserButton").attr("data-state", "True");
            return $("#watchUserButton").text(unwatchText);
          }
        }
      });
    });
  });

}).call(this);
