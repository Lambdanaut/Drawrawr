(function() {

  $(document).ready(function() {
    return $(".comment .replyButton").click(function() {
      return $(this).parent().find("form").slideDown("slow");
    });
  });

}).call(this);
