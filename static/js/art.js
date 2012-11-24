(function() {

  $(document).ready(function() {
    var art, fav_button, watchButton;
    art = $("#art");
    /* Image Full View
    */
    if (art.attr("data-type") === "image") {
      art.css({
        "max-width": "80%",
        "cursor": "pointer",
        "max-height": "1000px"
      });
      $("#preview_text").text("Click Image to Full View");
      art.click(function() {
        if (art.attr("data-size") === "small") {
          $("#preview_text").slideUp(200);
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
          $("#preview_text").slideDown(200);
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
    fav_button = $("#fav_button");
    fav_button.click(function() {
      return $.ajax({
        url: "/art/" + $("#art_ID").attr("data-state") + "/favorite",
        type: "POST",
        complete: function(msg) {
          if (fav_button.attr("data-state") === "fav") {
            fav_button.attr("src", "/static/images/unfavorite_button.png");
            return fav_button.attr("data-state", "unfav");
          } else {
            fav_button.attr("src", "/static/images/favorite_button.png");
            return fav_button.attr("data-state", "fav");
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
            watchButton.attr("src", "/static/images/unwatch_button.png");
            return watchButton.attr("data-state", "unwatch");
          } else {
            watchButton.attr("src", "/static/images/watch_button.png");
            return watchButton.attr("data-state", "watch");
          }
        }
      });
    });
    /* Feature Button
    */
    $("#featureButton").click(function() {
      var featureModal;
      return featureModal = new Modal("modal");
    });
    /* Delete Button
    */
    return $("#delete_button").click(function() {
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
