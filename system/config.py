import os

#Server
host = '0.0.0.0'
port = int(os.environ.get("PORT", 80))

#Production
logging         = False
debug           = True
betaKey         = False
randomSecretKey = False

#Database
dbHost = "localhost"
dbPort = 27017

#Users
iconSize = 75,75

#Art
pageViewsRequireAlternateIP = False

#Gallery
displayedWorksPerPage = 30
pageIndexes = 15

#Uploads
uploadsDir      = "uploads"
iconsDir        = os.path.join(uploadsDir, "icons")
artDir          = os.path.join(uploadsDir, "art")
thumbDir        = os.path.join(uploadsDir, "thumbs")

imageExtensions = set(['png', 'jpg', 'jpeg', 'gif', 'tif', 'svg'])
iconExtensions  = imageExtensions

thumbnailDimensions = 135,110
thumbnailFormat     = "JPEG"
thumbnailExtension  = ".thumbnail.jpg"

maxFileSize      = 20 * 1024**2
maxFileSizeText  = "Twenty Megabytes"

maxIconSize      = 2 * 1024**2
maxIconSizeText  = "Two Megabytes"
maxImageSize     = 8 * 1024**2
maxImageSizeText = "Eight Megabytes"

#Error Messages
fileTypeError = "The file you uploaded had an incorrect filetype. "
fileSizeError = "The file you uploaded was too large. "

#Captcha API
try:
  import captchaKey
  captchaPublicKey = captchaKey.public
  captchaSecretKey = captchaKey.secret
except ImportError: 
  captchaPublicKey = None
  captchaSecretKey = None
