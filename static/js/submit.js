(function() {

  $(document).ready(function() {
    $("#artOptions").change(function() {
      $("#ignore").remove();
      $("#submitTitle").text($(this).val());
      $(".artArea").css("display", "none");
      return $("#" + $(this).val().toLowerCase() + "Area").css("display", "inline");
    });
    return $("form").submit(function() {
      var m;
      $(".uploadButton").attr("disabled", "disabled");
      m = new Modal("#modal");
      return 1;
    });
  });

}).call(this);
