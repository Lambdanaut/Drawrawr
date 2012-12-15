(function() {
  var availableMoods;

  availableMoods = ["Accepted", "Accomplished", "Acrimonious", "Aggravated", "Alone", "American", "Amused", "Angry", "Annoyed", "Anxious", "Apathetic", "Ashamed", "Autistic", "Awake", "Bewildered", "Bitchy", "Bittersweet", "Blah", "Blank", "Blissful", "Bored", "Bouncy", "Busy", "Calm", "Cheerful", "Chipper", "Cold", "Complacent", "Confused", "Content", "Contemptful", "Cranky", "Crappy", "Creative", "Crazy", "Crushed", "Curious", "Cynical", "Dark", "Depressed", "Determined", "Devious", "Dirty", "Disappointed", "Discontent", "Ditzy", "Dorky", "Drained", "Drunk", "Durr", "Ecstatic", "Edgy", "Energetic", "Enraged", "Enthralled", "Envious", "Exanimate", "Excited", "Exhausted", "Flabergasted", "Flirty", "Frustrated", "Full", "Foolish", "Geeky", "General", "Giddy", "Giggly", "Gloomy", "Good", "Grateful", "Groggy", "Grumpy", "Guilty", "Happy", "High", "Hopeful", "Homosexual", "Horny", "Hot", "Hungry", "Hurt", "Hyper", "Impressed", "Indescribable", "Indifferent", "Indignant", "Infuriated", "Irate", "Itchy", "Irritated", "Jealous", "Joyful", "Jubilant", "Lazy", "Lethargic", "Like a Sock", "Listless", "LOL", "Lonely", "Loved", "Lucky", "Mad", "Melancholy", "Mellow", "Meow", "Mischievous", "Moody", "Morose", "Naughty", "Nauseous", "Nerdy", "Not Specified", "Numb", "Old", "Okay", "Overworked", "Optimistic", "Paralyzed", "Peaceful", "Perfect", "Petrified", "Pessimistic", "Petulant", "Pissed", "Pleased", "Predatory", "Quixotic", "Recumbent", "Refreshed", "Rejected", "Rejuvenated", "Relaxed", "Relieved", "Restless", "Revolutionary", "Rushed", "Sad", "Satisfied", "Shocked", "Sick", "Silly", "Sleepy", "Skeptical", "Smart", "Sorry", "Stressed", "Stupid", "Surprised", "Sympathetic", "Thankful", "Tired", "Touched", "Trippy", "Uncomfortable", "Useless", "Weird", "Weh", "Whoops", "Zombified", "???"];

  $(document).ready(function() {
    $("#moods").autocomplete({
      source: availableMoods
    });
    return $("#manage_journals .close").click(function() {
      var confirm_deletion, journal_id, journal_link,
        _this = this;
      journal_link = $(this).parent().find("a");
      journal_id = journal_link.attr("data-id");
      confirm_deletion = confirm("Are you sure you want to delete \"" + journal_link.text() + "\"?");
      if (confirm_deletion) {
        return $.post("/journal/delete/" + journal_id, function() {
          return journal_link.parent().fadeOut("slow");
        });
      }
    });
  });

}).call(this);