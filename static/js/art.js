(function() {

  $(document).ready(function() {
    var art, favButton;
    art = $("#art");
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
    favButton = $("#favButton");
    return favButton.click(function() {
      if (favButton.attr("data-state") === "fav") {
        favButton.html("- Unfavorite");
        favButton.attr("data-state", "unfav");
        return $.ajax({
          url: "/art/" + $("#artID").attr("data-state") + "/favorite",
          type: "POST"
        });
      } else {
        favButton.html("+ Favorite");
        favButton.attr("data-state", "fav");
        return $.ajax({
          url: "/art/" + $("#artID").attr("data-state") + "/favorite",
          type: "POST"
        });
      }
    });
  });

}).call(this);
