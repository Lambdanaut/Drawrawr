
/* What items belong to what sets
*/

/* setA :: T L B
*/

/* 	profile
*/

/* setB :: T L B H
*/

/* 	gallery
*/

/*	comments
*/

/* setC :: R H
*/

/* 	watches
*/

/* 	friends
*/

(function() {
  var allowed_in, get_location, inSet, serialize_layout, serialize_layout_order, sets, update_location;

  sets = {
    a: ['t', 'l', 'r', 'b', 'h'],
    b: ['r', 'h'],
    c: ['t', 'l', 'b', 'h'],
    d: ['t', 'b', 'h'],
    e: ['r', 'b', 'h'],
    f: ['r', 'l', 'h'],
    g: ['t', 'r', 'b', 'h']
  };

  inSet = {
    shop: 'a',
    shout: 'a',
    watches: 'b',
    friends: 'b',
    nearby: 'b',
    awards: 'b',
    tips: 'b',
    profile: 'c',
    gallery: 'c',
    favorites: 'c',
    journal: 'c',
    comments: 'd',
    clubs: 'e',
    chars: 'f',
    playlist: 'g',
    interactions: 'g'
  };

  allowed_in = function() {};

  /* Returns a serialized version of the layout
  */

  serialize_layout = function() {
    var data;
    data = "";
    $("#profile_top, #profile_left_col, #profile_right_col, #profile_bottom, #profile_hidden").each(function(idx, elem) {
      return $(elem).children(".draggable").each(function(idx2, elem2) {
        return data += $(elem2).attr("id") + "=" + $(elem).attr("data-loc") + "&";
      });
    });
    return data;
  };

  serialize_layout_order = function() {
    var data;
    data = "";
    $("#profile_top, #profile_left_col, #profile_right_col, #profile_bottom, #profile_hidden").each(function(idx, elem) {
      return $(elem).children(".draggable").each(function(idx2, elem2) {
        return data += $(elem2).attr("id") + "=" + idx2 + "&";
      });
    });
    return data;
  };

  update_location = function(position) {
    var lat, lon;
    lat = position.coords.latitude;
    lon = position.coords.longitude;
    $("#latitude").val(lat);
    return $("#longitude").val(lon);
  };

  get_location = function() {
    return navigator.geolocation.getCurrentPosition(update_location);
  };

  $(document).ready(function() {
    /* Gender
    */    $("#change_gender").val($("#default_gender").val());
    /* Geolocation
    */
    if (Modernizr.geolocation) {
      $("#get_location").click(get_location);
    } else {
      $("#get_location").attr("disabled", "disabled");
      $("#get_location").css("display", "none");
      $("#no_location_browser").css("display", "block");
    }
    $("#why_location").click(function() {
      var box;
      return box = new Help_Box("#whyHelp");
    });
    /* Color Theme
    */
    $("#change_color_theme").change(function() {
      return $("#colorThemeStyle").attr("href", "/static/css/userpages/" + $(this).val() + ".css");
    });
    $("#change_color_theme").val($("#default_theme").attr("data-theme"));
    $("#change_color_theme").trigger("change");
    /* Userpage Layout
    */
    $("#profile_top, #profile_left_col, #profile_right_col, #profile_bottom, #profile_hidden").sortable({
      connectWith: ".drag_box",
      update: function() {
        $("#change_layout").val(serialize_layout());
        return $("#change_layout_order").val(serialize_layout_order());
      }
    }).disableSelection();
    /* Beta Keys
    */
    return $("#generate_new_invite").click(function() {
      var conf;
      conf = confirm("Are you sure you want to spend one of your invites? ");
      if (conf) {
        return $.ajax({
          url: "/admin/generate_beta_pass",
          type: "POST",
          beforeSend: function() {
            return $("#beta_loader").css("display", "inline");
          },
          success: function(data) {
            $("#beta_key_list").append("<li style='display:none'>" + data + "</li>");
            return $("#beta_key_list li:last-child").fadeIn("slow", function() {
              return $("#beta_loader").css("display", "none");
            });
          }
        });
      }
    });
  });

}).call(this);
