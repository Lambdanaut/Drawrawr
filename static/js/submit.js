(function() {
  $(document).ready(function() {
    return $("#artOptions").change(function() {
      $("#ignore").remove();
      $("#submitTitle").text($(this).val());
      $(".artArea").css("display", "none");
      return $("#" + $(this).val().toLowerCase() + "Area").css("display", "inline");
    });
  });
}).call(this);
