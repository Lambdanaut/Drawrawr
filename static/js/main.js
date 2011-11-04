(function() {
  var Header, Modal, Notice;
  var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };
  Header = (function() {
    function Header(glued) {
      this.glued = glued;
      this.switchGlue();
      $("#set-header").click(__bind(function() {
        return this.switchGlue();
      }, this));
    }
    Header.prototype.switchGlue = function() {
      if (this.glued) {
        return this.unglue();
      } else {
        return this.glue();
      }
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
        "margin": "50px 15px 4px 15px"
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
    /* Keeps the copyright up to date on the current year */;    var date, header, notice;
    date = new Date();
    $("#copyright-date").html(date.getFullYear());
    /* Registration button */;
    $("#register-button").click(__bind(function() {
      var signupModal;
      return signupModal = new Modal("CREATE A NEW ACCOUNT", $("#register-form").html());
    }, this));
    /* Set up the header */;
    header = new Header(false);
    return notice = new Notice("MESSAGE THINGY", "Catherine: The message thingy?");
  });
}).call(this);
