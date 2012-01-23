import os

#Production
logging = False

#Database
dbHost = "localhost"
dbPort = 27017

#Users
iconSize = (75,75)

#Uploads
uploadsDir      = "uploads"
iconsDir        = os.path.join(uploadsDir, "icons")
artDir          = os.path.join(uploadsDir, "art")
thumbDir        = os.path.join(uploadsDir, "thumbs")
imageExtensions = set(['png', 'jpg', 'jpeg', 'gif', 'tif', 'svg'])
iconExtensions  = imageExtensions

#Captcha API
try:
  import captchaKey
  captchaPublicKey = captchaKey.public
  captchaSecretKey = captchaKey.secret
except ImportError: 
  captchaSecretKey = captchaKey.secret
  captchaPublicKey = None
  captchaSecretKey = None
