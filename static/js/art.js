(function() {

  $(document).ready(function() {
    var art, favButton, watchButton;
    art = $("#art");
    /* Image Full View
    */
    if (art.attr("data-type") === "image") {
      art.css({
        "max-width": "80%",
        "cursor": "pointer",
        "max-height": "1000px"
      });
      $("#previewText").text("Click Image to Full View");
      art.click(function() {
        if (art.attr("data-size") === "small") {
          $("#previewText").slideUp(200);
          return art.fadeOut(100, function() {
            art.css({
              "max-width": "None",
              "max-height": "None"
            });
            return art.fadeIn(100, function() {
              return art.attr("data-size", "full");
            });
          });
        } else {
          $("#previewText").slideDown(200);
          return art.fadeOut(100, function() {
            art.css({
              "max-width": "80%",
              "max-height": "1000px"
            });
            return art.fadeIn(100, function() {
              return art.attr("data-size", "small");
            });
          });
        }
      });
    }
    /* Favorites
    */
    favButton = $("#favButton");
    favButton.click(function() {
      return $.ajax({
        url: "/art/" + $("#artID").attr("data-state") + "/favorite",
        type: "POST",
        complete: function(msg) {
          if (favButton.attr("data-state") === "fav") {
            favButton.attr("src", "/static/images/unfavoritebutton.png");
            return favButton.attr("data-state", "unfav");
          } else {
            favButton.attr("src", "/static/images/favoritebutton.png");
            return favButton.attr("data-state", "fav");
          }
        }
      });
    });
    /* Watch Button
    */
    watchButton = $("#watchButton");
    watchButton.click(function() {
      return $.ajax({
        url: "/users/watch",
        type: "POST",
        data: "watchedUser=" + $("#author").attr("data-name"),
        complete: function(msg) {
          if (watchButton.attr("data-state") === "watch") {
            watchButton.attr("src", "/static/images/unwatchbutton.png");
            return watchButton.attr("data-state", "unwatch");
          } else {
            watchButton.attr("src", "/static/images/watchbutton.png");
            return watchButton.attr("data-state", "watch");
          }
        }
      });
    });
    /* Delete Button
    */
    return $("#deleteButton").click(function() {
      var conf;
      conf = confirm("Are you sure you want to delete this artwork? ");
      if (conf) {
        return $.ajax({
          type: "DELETE",
          complete: function(status, msg) {
            if (msg === "success") {
              return window.location = "/" + $("#author").attr("data-name");
            }
          }
        });
      }
    });
  });

}).call(this);
