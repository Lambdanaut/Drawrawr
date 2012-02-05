(function() {
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  this.Header = (function() {
    function Header(glued) {
      this.glued = glued;
      this.switchGlue();
      $("#set-header").click(__bind(function() {
        this.switchGlue();
        return this.updateDatabaseGlue();
      }, this));
    }
    Header.prototype.switchGlue = function() {
      if (this.glued) {
        return this.unglue();
      } else {
        return this.glue();
      }
    };
    Header.prototype.updateDatabaseGlue = function() {
      return $.ajax({
        url: "/users/glue",
        type: "POST",
        data: "glued=" + (this.glued + 0)
      });
    };
    /* Glue the header to the top of the page */;
    Header.prototype.glue = function() {
      var headerCSS;
      this.glued = true;
      /* Old Header Style. This doesn't stretch across the page */;
      /* headerCSS = "position":"relative","top":"auto","left":"auto","right":"auto","margin":"5px 15px 4px 15px" */;
      /* navCSS ="margin":"0px 15px 4px 15px" */;
      /* $("#header").addClass("roundBox") */;
      /* New Header Style. This stetches all the was across the page */;
      headerCSS = {
        "position": "absolute"
      };
      $("#header").css(headerCSS);
      return $("#set-header").html("↓");
    };
    /* Unglue the header from the top of the page */;
    Header.prototype.unglue = function() {
      var headerCSS;
      this.glued = false;
      headerCSS = {
        "position": "fixed"
      };
      $("#header").css(headerCSS);
      /* Old Header Style fix. Only required for old header */;
      /* $("#header").removeClass("roundBox") */;
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
      return $("#notice").slideUp("fast", __bind(function() {
        return $("#notice").hide();
      }, this));
    };
    return Notice;
  })();
  this.Modal = (function() {
    function Modal(modalDiv) {
      this.modalDiv = modalDiv;
      $("#modal .close").click(this.die);
      this.show();
    }
    Modal.prototype.show = function() {
      this.visible = true;
      $(this.modalDiv).css("display", "block");
      return $("#modal").css("display", "block");
    };
    Modal.prototype.die = function() {
      this.visible = false;
      $("#modal aside").css("display", "none");
      return $("#modal").css("display", "none");
    };
    return Modal;
  })();
  $(document).ready(function() {
    /* Keeps the copyright up to date on the current year */;    var date, header;
    date = new Date();
    $("#copyright-date").html(date.getFullYear());
    /* Set up the header */;
    header = new Header(false);
    if ($("#glued").attr("data-glued") === "0") {
      header.switchGlue();
    }
    /* Flashed Messages */;
    $("#flashed li").each(function() {
      return new Notice("MESSAGE", $(this).text());
    });
    /* Registration */;
    Recaptcha.create($("#registerCaptcha").attr("data-publicKey"), "registerCaptcha", {
      theme: 'custom',
      custom_theme_widget: 'recaptcha_widget',
      callback: Recaptcha.focus_response_field
    });
    $("#register-button").click(__bind(function() {
      var signupModal;
      signupModal = new Modal("#register-form");
      return $('form:not(.filter) :input:visible:first').focus();
    }, this));
    $("#register-form form").submit(__bind(function() {
      var form;
      form = $("#register-form form").serialize();
      $.ajax({
        url: "/users/signup",
        type: "POST",
        data: form,
        success: __bind(function(data) {
          if (data === "1") {
            return window.location = "/users/welcome";
          }
        }, this)
      });
      return false;
    }, this));
    /* Login */;
    $("#login-button").click(__bind(function() {
      var loginModal;
      loginModal = new Modal("#login-form");
      return $('form:not(.filter) :input:visible:first').focus();
    }, this));
    $("#login-form form").submit(__bind(function() {
      var form;
      form = $("#login-form form").serialize();
      $.ajax({
        url: "/users/login",
        type: "POST",
        data: form,
        success: __bind(function(data) {
          if (data === "1") {
            location.reload(true);
          }
          if (data === "0") {
            return new Notice("Woops!", "Incorrect Username/Password combination. Remember that your password is case sensative! ");
          }
        }, this)
      });
      return false;
    }, this));
    /* Logout */;
    return $("#logout-button").click(__bind(function() {
      return $.ajax({
        url: "/users/logout",
        type: "POST",
        success: __bind(function(data) {
          if (data === "1") {
            return window.location = "/";
          }
        }, this)
      });
    }, this));
  });
}).call(this);
