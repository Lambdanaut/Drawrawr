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
          var loggedInLowername, loggedInUsername;
          if ($("#watchUserButton").attr("data-state") === "True") {
            $("#watchUserButton").attr("data-state", "False");
            $("#watchUserButton").text(watchText);
            /* Hide user from watch list
            */
            return $('#watchers img[title="' + $("#loggedInUsername").attr("data-name") + '"]').fadeOut("slow", function() {
              return $(this).remove();
            });
          } else {
            $("#watchUserButton").attr("data-state", "True");
            $("#watchUserButton").text(unwatchText);
            /* Show user in watch list
            */
            $("#watchers p").remove();
            loggedInUsername = $("#loggedInUsername").attr("data-name");
            loggedInLowername = loggedInUsername.toLowerCase();
            $("#watchers").prepend('<a href="/{{ user }}"><img src="/icons/' + loggedInLowername + '" alt="' + loggedInUsername + '\'s icon" class="tinyIcon" style="float: left;margin: 2px; display: none;" title="' + loggedInUsername + '"></a>');
            return $('#watchers img[title="' + $("#loggedInUsername").attr("data-name") + '"]').fadeIn("slow");
          }
        }
      });
    });
  });

}).call(this);
