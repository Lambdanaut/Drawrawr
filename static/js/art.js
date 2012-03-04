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
        beforeSend: function() {
          return favButton.text(" - Loading - ");
        },
        complete: function(msg) {
          if (favButton.attr("data-state") === "fav") {
            favButton.text("- Unfavorite");
            return favButton.attr("data-state", "unfav");
          } else {
            favButton.text("+ Favorite");
            return favButton.attr("data-state", "fav");
          }
        }
      });
    });
    /* Watch Button
    */
    watchButton = $("#watchButton");
    return watchButton.click(function() {
      return $.ajax({
        url: "/users/watch",
        type: "POST",
        data: "watchedUser=" + $("#author").attr("data-name"),
        beforeSend: function() {
          return watchButton.text(" - Loading - ");
        },
        complete: function(msg) {
          if (watchButton.attr("data-state") === "watch") {
            watchButton.text("- Unwatch");
            return watchButton.attr("data-state", "unwatch");
          } else {
            watchButton.text("+ Watch");
            return watchButton.attr("data-state", "watch");
          }
        }
      });
    });
  });

}).call(this);
