(function() {

  $(document).ready(function() {
    $("#art_options").change(function() {
      $("#ignore").remove();
      $("#submit_title").text($(this).val());
      $(".art_area").css("display", "none");
      return $("#" + $(this).val().toLowerCase() + "_area").css("display", "inline");
    });
    return $("form").submit(function() {
      var m;
      $(".upload_button").attr("disabled", "disabled");
      m = new Modal("#submit_loading_modal");
      return 1;
    });
  });

}).call(this);
