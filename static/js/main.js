(function() {
  var Header, Modal, Notice;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  Header = (function() {
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
      var headerCSS, navCSS;
      this.glued = true;
      headerCSS = {
        "position": "relative",
        "top": "auto",
        "left": "auto",
        "right": "auto",
        "margin": "5px 15px 4px 15px"
      };
      navCSS = {
        "margin": "0px 15px 4px 15px"
      };
      $("#header").css(headerCSS);
      $("#navigation").css(navCSS);
      $("#header").addClass("roundBox");
      return $("#set-header").html("↓");
    };
    /* Unglue the header from the top of the page */;
    Header.prototype.unglue = function() {
      var headerCSS, navCSS;
      this.glued = false;
      headerCSS = {
        "position": "fixed",
        "top": "5px",
        "left": "0px",
        "right": "0px",
        "margin": "auto"
      };
      navCSS = {
        "margin": "83px 15px 4px 15px"
      };
      $("#header").css(headerCSS);
      $("#navigation").css(navCSS);
      $("#header").removeClass("roundBox");
      return $("#set-header").html("↑");
    };
    return Header;
  })();
  Notice = (function() {
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
  Modal = (function() {
    function Modal(title, content) {
      this.title = title;
      this.content = content;
      $("#modal div").html("<span class='close'></span><h4>" + this.title + "</h4><p>" + this.content + "</p>");
      $("#modal .close").click(this.die);
      this.show();
    }
    Modal.prototype.show = function() {
      this.visible = true;
      return $("#modal").css("visibility", "visible");
    };
    Modal.prototype.die = function() {
      this.visible = false;
      return $("#modal").css("visibility", "hidden");
    };
    return Modal;
  })();
  $(document).ready(function() {
    /* Keeps the copyright up to date on the current year */;    var date, header;
    date = new Date();
    $("#copyright-date").html(date.getFullYear());
    /* Set up the header */;
    header = new Header(false);
    $.ajax({
      url: "/users/glue",
      type: "GET",
      success: __bind(function(data) {
        if (data === "0") {
          return header.switchGlue();
        }
      }, this)
    });
    /* Registration */;
    $("#register-button").click(__bind(function() {
      var signupModal;
      signupModal = new Modal("CREATE A NEW ACCOUNT", $("#register-form").html());
      return $("#modal button").click(__bind(function() {
        return $.ajax({
          url: "/users/signup",
          type: "POST",
          data: $("#modal form").serialize(),
          success: __bind(function(data) {
            if (data === "1") {
              return location.reload();
            }
          }, this)
        });
      }, this));
    }, this));
    /* Login */;
    $("#login-button").click(__bind(function() {
      var loginModal;
      loginModal = new Modal("LOGIN", $("#login-form").html());
      return $("#modal button").click(__bind(function() {
        return $.ajax({
          url: "/users/login",
          type: "POST",
          data: $("#modal form").serialize(),
          success: __bind(function(data) {
            if (data === "1") {
              return location.reload();
            } else {
              return new Notice("Incorrect Login Combo", "The username and password didn't match any in our records. Try again! ");
            }
          }, this)
        });
      }, this));
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
