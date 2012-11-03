(function() {

  $(document).ready(function() {
    /* Comment Button
    */    $(".leaveCommentButton").click(function() {
      var _this = this;
      $("#leaveCommentForm").html($("#replyFormTemplate").clone().html());
      return $(this).fadeOut("fast", function() {
        $("#leaveCommentForm").fadeIn("fast");
        return $("#leaveCommentForm").find("textarea").focus();
      });
    });
    /* Reply Button
    */
    return $(".comment .replyButton").click(function() {
      var form, reply,
        _this = this;
      reply = $(this).parent().find(".reply");
      reply.html($("#replyFormTemplate").clone().html());
      form = reply.find("form");
      form.find(".parentInput").val($(this).parent().find(".parentData").attr("data-value"));
      form.find(".commentMapInput").val($(this).parent().find(".commentMapData").attr("data-value"));
      return $(this).hide(0, function() {
        reply.fadeIn("fast");
        return reply.find("textarea").focus();
      });
    });
  });

}).call(this);
