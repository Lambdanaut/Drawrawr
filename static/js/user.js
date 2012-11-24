(function() {
  var unwatch_text, watch_text;

  watch_text = " + watch ";

  unwatch_text = " - unwatch ";

  $(document).ready(function() {
    /* Sets the watch button's text
    */    if ($("#watch_user_button").attr("data-state") === "True") {
      $("#watch_user_button").text(unwatch_text);
    } else {
      $("#watch_user_button").text(watch_text);
    }
    /* Watch button functionality
    */
    return $("#watch_user_button").click(function() {
      return $.ajax({
        url: "/users/watch",
        type: "POST",
        data: "watchedUser=" + $("#username").attr("data-name"),
        beforeSend: function() {
          return $("#watch_user_button").text(" - Loading - ");
        },
        complete: function(msg) {
          var logged_in_lowername, logged_in_username;
          if ($("#watch_user_button").attr("data-state") === "True") {
            $("#watch_user_button").attr("data-state", "False");
            $("#watch_user_button").text(watch_text);
            /* Hide user from watch list
            */
            return $('#watchers img[title="' + $("#logged_in_username").attr("data-name") + '"]').fadeOut("slow", function() {
              return $(this).remove();
            });
          } else {
            $("#watch_user_button").attr("data-state", "True");
            $("#watch_user_button").text(unwatch_text);
            /* Show user in watch list
            */
            $("#watchers p").remove();
            logged_in_username = $("#logged_in_username").attr("data-name");
            logged_in_lowername = logged_in_username.toLowerCase();
            $("#watchers").prepend('<a href="/' + logged_in_lowername + '"><img src="/icons/' + logged_in_lowername + '" alt="' + logged_in_username + '\'s icon" class="tiny_icon" style="float: left;margin: 2px; display: none;" title="' + logged_in_username + '"></a>');
            return $('#watchers img[title="' + $("#logged_in_username").attr("data-name") + '"]').fadeIn("slow");
          }
        }
      });
    });
  });

}).call(this);
