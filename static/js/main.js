(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  this.Header = (function() {

    function Header(glued) {
      var _this = this;
      this.glued = glued;
      this.switch_glue();
      $("#set-header").click(function() {
        _this.switch_glue();
        return _this.update_database_glue();
      });
    }

    Header.prototype.switch_glue = function() {
      if (this.glued) {
        return this.unglue();
      } else {
        return this.glue();
      }
    };

    Header.prototype.update_database_glue = function() {
      return $.ajax({
        url: "/users/glue",
        type: "POST",
        data: "glued=" + (this.glued + 0)
      });
    };

    /* Glue the header to the top of the page
    */

    Header.prototype.glue = function() {
      var headerCSS;
      this.glued = true;
      headerCSS = {
        "position": "absolute"
      };
      $("#header").css(headerCSS);
      return $("#set-header").html("↓");
    };

    /* Unglue the header from the top of the page
    */

    Header.prototype.unglue = function() {
      var headerCSS;
      this.glued = false;
      headerCSS = {
        "position": "fixed"
      };
      $("#header").css(headerCSS);
      return $("#set-header").html("↑");
    };

    return Header;

  })();

  this.Notice = (function() {

    function Notice(title, content) {
      this.title = title;
      this.content = content;
      $("#notice").slideDown("slow");
      $("#notice").html("<span class='close'></span><h4>" + this.title + "</h4><p>" + this.content + "</p>");
      $("#notice .close").click(this.die);
    }

    Notice.prototype.die = function() {
      var _this = this;
      return $("#notice").slideUp("fast", function() {
        return $("#notice").hide();
      });
    };

    return Notice;

  })();

  this.Modal = (function() {

    function Modal(modalDiv) {
      this.modalDiv = modalDiv;
      $(".modal .close").click(this.die);
      this.show();
    }

    Modal.prototype.show = function() {
      this.visible = true;
      $(this.modalDiv).css("display", "block");
      return $(".modal").css("display", "block");
    };

    Modal.prototype.die = function() {
      this.visible = false;
      $(".modal aside").css("display", "none");
      return $(".modal").css("display", "none");
    };

    return Modal;

  })();

  this.Help_Box = (function() {

    function Help_Box(help_div) {
      this.help_div = help_div;
      this.die = __bind(this.die, this);
      $(this.help_div).click(this.die);
      $(this.help_div).addClass("help_box");
      $(this.help_div).addClass("round_box");
      this.show();
    }

    Help_Box.prototype.show = function() {
      return $(this.help_div).css("display", "block");
    };

    Help_Box.prototype.die = function() {
      return $(this.help_div).css("display", "none");
    };

    return Help_Box;

  })();

  $(document).ready(function() {
    /* Keeps the copyright up to date on the current year
    */
    var date, header,
      _this = this;
    date = new Date();
    $("#copyright-date").html(date.getFullYear());
    /* Refreshes relative dates
    */
    $("body").timeago();
    /* Set up the header
    */
    header = new Header(false);
    if ($("#glued").attr("data-glued") === "0") header.switch_glue();
    /* Flashed Messages
    */
    $("#flashed li").each(function() {
      return new Notice("MESSAGE", $(this).text());
    });
    /* Registration
    */
    if ($("#register_captcha").length) {
      Recaptcha.create($("#register_captcha").attr("data-publicKey"), "register_captcha", {
        theme: 'custom',
        custom_theme_widget: 'recaptcha_widget',
        callback: Recaptcha.focus_response_field
      });
    }
    $("#register-button").click(function() {
      var signupModal;
      signupModal = new Modal("#register-form");
      return $('form:not(.filter) :input:visible:first').focus();
    });
    $("#register-form form").submit(function() {
      var form;
      form = $("#register-form form").serialize();
      $.ajax({
        url: "/users/signup",
        type: "POST",
        data: form,
        success: function(data) {
          if (data === "1") {
            /* SUCCESS
            */
            return window.location = "/users/welcome";
          } else if (data === "0") {
            return new Notice("Woops!", "There was a serious error processing your signup. Try refreshing the page and trying again. ");
          } else if (data === "2") {
            return new Notice("Mixup!", "That Username is already taken! Try a different one. ");
          } else if (data === "3") {
            return new Notice("I H8 Passwords!", "Your passwords didn't match up! Try typing them again. ");
          } else if (data === "4") {
            return new Notice("Legal Jargon!", "You must read and agree to our Terms of Service!");
          } else if (data === "5") {
            return new Notice("Woops!", "Your Captcha answer was invalid. Try again! ");
          } else if (data === "6") {
            return new Notice("B8a C0d3!", "We didn't recognize your <strong>Beta Code</strong>. It seems to be inactive! ");
          } else if (data === "7") {
            return new Notice("Lmao Hacker!", "You already seem to have an account with us. ");
          }
        }
      });
      return false;
    });
    /* Login
    */
    $("#login-button").click(function() {
      var loginModal;
      loginModal = new Modal("#login-form");
      return $('form:not(.filter) :input:visible:first').focus();
    });
    $("#login-form form").submit(function() {
      var form;
      form = $("#login-form form").serialize();
      $.ajax({
        url: "/users/login",
        type: "POST",
        data: form,
        success: function(data) {
          if (data === "1") {
            return location.reload(true);
          } else if (data === "2") {
            return new Notice("WHAT Username!?", "That username <em>DOESN'T</em> exist. Believe me, I checked! Perhaps you're spelling it wrong. ");
          } else if (data === "3") {
            return new Notice("Wrong Password", "That username exists, but that is <em>NOT</em> the correct password for their account. Try again, and remember, the password is <a href=\"http://en.wikipedia.org/wiki/Case_sensitivity\" target=\"_blank\">CASE SENSITIVE</a>!");
          }
        }
      });
      return false;
    });
    /* Logout
    */
    return $("#logout-button").click(function() {
      return $.ajax({
        url: "/users/logout",
        type: "POST",
        success: function(data) {
          if (data === "1") return window.location = "/";
        }
      });
    });
  });

}).call(this);
