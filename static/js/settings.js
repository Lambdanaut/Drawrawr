
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
  var allowedIn, getLocation, inSet, serializeLayout, serializeLayoutOrder, sets, updateLocation;

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

  allowedIn = function() {};

  /* Returns a serialized version of the layout
  */

  serializeLayout = function() {
    var data;
    data = "";
    $("#profileTop, #profileLeftCol, #profileRightCol, #profileBottom, #profileHidden").each(function(idx, elem) {
      return $(elem).children(".draggable").each(function(idx2, elem2) {
        return data += $(elem2).attr("id") + "=" + $(elem).attr("data-loc") + "&";
      });
    });
    return data;
  };

  serializeLayoutOrder = function() {
    var data;
    data = "";
    $("#profileTop, #profileLeftCol, #profileRightCol, #profileBottom, #profileHidden").each(function(idx, elem) {
      return $(elem).children(".draggable").each(function(idx2, elem2) {
        return data += $(elem2).attr("id") + "=" + idx2 + "&";
      });
    });
    return data;
  };

  updateLocation = function(position) {
    var lat, lon;
    lat = position.coords.latitude;
    lon = position.coords.longitude;
    $("#latitude").val(lat);
    return $("#longitude").val(lon);
  };

  getLocation = function() {
    return navigator.geolocation.getCurrentPosition(updateLocation);
  };

  $(document).ready(function() {
    /* Gender
    */    $("#changeGender").val($("#defaultGender").val());
    /* Geolocation
    */
    if (Modernizr.geolocation) {
      $("#getLocation").click(getLocation);
    } else {
      $("#getLocation").attr("disabled", "disabled");
      $("#getLocation").css("display", "none");
      $("#noLocationBrowser").css("display", "block");
    }
    $("#whyLocation").click(function() {
      var box;
      return box = new Helpbox("#whyHelp");
    });
    /* Color Theme
    */
    $("#changeColorTheme").change(function() {
      return $("#colorThemeStyle").attr("href", "/static/css/userpages/" + $(this).val() + ".css");
    });
    $("#changeColorTheme").val($("#defaultTheme").attr("data-theme"));
    $("#changeColorTheme").trigger("change");
    /* Userpage Layout
    */
    $("#profileTop, #profileLeftCol, #profileRightCol, #profileBottom, #profileHidden").sortable({
      connectWith: ".dragBox",
      update: function() {
        $("#changeLayout").val(serializeLayout());
        return $("#changeLayoutOrder").val(serializeLayoutOrder());
      }
    }).disableSelection();
    /* Beta Keys
    */
    return $("#generateNewInvite").click(function() {
      var conf;
      conf = confirm("Are you sure you want to spend one of your invites? ");
      if (conf) {
        return $.ajax({
          url: "/admin/generateBetaPass",
          type: "POST",
          beforeSend: function() {
            return $("#betaLoader").css("display", "inline");
          },
          success: function(data) {
            $("#betaKeyList").append("<li style='display:none'>" + data + "</li>");
            return $("#betaKeyList li:last-child").fadeIn("slow", function() {
              return $("#betaLoader").css("display", "none");
            });
          }
        });
      }
    });
  });

}).call(this);
