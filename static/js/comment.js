(function() {

  $(document).ready(function() {
    /* Comment Button
    */    $(".leave_comment_button").click(function() {
      var _this = this;
      $("#leave_comment_form").html($("#reply_form_template").clone().html());
      return $(this).fadeOut("fast", function() {
        $("#leave_comment_form").fadeIn("fast");
        return $("#leave_comment_form").find("textarea").focus();
      });
    });
    /* Reply Button
    */
    return $(".comment .reply_button").click(function() {
      var form, reply,
        _this = this;
      reply = $(this).parent().find(".reply");
      reply.html($("#reply_form_template").clone().html());
      form = reply.find("form");
      form.find(".parent_input").val($(this).parent().find(".parentData").attr("data-value"));
      form.find(".comment_map_input").val($(this).parent().find(".comment_map_data").attr("data-value"));
      return $(this).hide(0, function() {
        reply.fadeIn("fast");
        return reply.find("textarea").focus();
      });
    });
  });

}).call(this);
