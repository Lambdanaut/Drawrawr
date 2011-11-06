
class TrackingType:
  COUNT = 0x0
  STRING = 0x1 


achievements = {
  "epic trolling":
  {
    "id": 0x0,
    "tracking type": TrackingType::COUNT,
    
    "achievement goal": 500,
    "achievement title": "Epic trolling",
    "achievement message": "You troll.",
    "achievement icon": None,
    "stats": { "badassery": 5000, "likability": -40, "artistic": 0 }                 
  }
}

NOTIFICATION_ACHIEVEMENT = "Achievement get!"

class AchievementTracker:
  def addTo(tracker, user, value = 1):
    if achievementTracker.get('achievements', tracker):
      
      if achievementTracker["tracking type"] is TrackingType::COUNT:
        if not isinstance(value, (int, long)) or not ('user' in locals()): return False
        
        