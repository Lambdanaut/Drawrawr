(function() {
  var showPreview, thumbHeight, thumbWidth;

  thumbWidth = 135;

  thumbHeight = 110;

  showPreview = function(coords) {
    var rx, ry;
    rx = thumbWidth / coords.w;
    ry = thumbHeight / coords.h;
    $("#x").val(coords.x);
    $("#y").val(coords.y);
    $("#w").val(coords.w);
    $("#h").val(coords.h);
    return $('#preview').css({
      width: Math.round(rx * imageWidth) + 'px',
      height: Math.round(ry * imageHeight) + 'px',
      marginLeft: '-' + Math.round(rx * coords.x) + 'px',
      marginTop: '-' + Math.round(ry * coords.y) + 'px'
    });
  };

  $(document).ready(function() {
    $('#art').load(function() {
      window.imageWidth = $("#art").width();
      window.imageHeight = $("#art").height();
      $('#art').Jcrop({
        aspectRatio: thumbWidth / thumbHeight,
        onChange: showPreview,
        onSelect: showPreview,
        setSelect: [0, 0, imageWidth, imageHeight]
      });
      return showPreview({
        w: imageWidth,
        h: imageHeight
      });
    });
    return $("form").submit(function() {
      var m;
      $(".button").attr("disabled", "disabled");
      m = new Modal("#modal");
      return 1;
    });
  });

}).call(this);
