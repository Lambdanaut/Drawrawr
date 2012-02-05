(function() {
  var showPreview;
  showPreview = function(coords) {
    var rx, ry;
    rx = 100 / coords.w;
    ry = 100 / coords.h;
    return $('#preview').css({
      width: Math.round(rx * 500) + 'px',
      height: Math.round(ry * 370) + 'px',
      marginLeft: '-' + Math.round(rx * coords.x) + 'px',
      marginTop: '-' + Math.round(ry * coords.y) + 'px'
    });
  };
  $(document).ready(function() {
    return $('#art').Jcrop({
      onChange: showPreview,
      onSelect: showPreview,
      aspectRatio: 1.2272727
    });
  });
}).call(this);
