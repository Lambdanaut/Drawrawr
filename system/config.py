import os
usingSecrets=True
try: import secrets
except ImportError: usingSecrets=False

# Server
host = '0.0.0.0'
port = int(os.environ.get("PORT", 80))

# Production
production      = True
logging         = False
debug           = True
betaKey         = True
randomSecretKey = False

# Display
headerImage = "/static/images/headers/regheader.png"

# Database
if production and usingSecrets:
  dbHost = "ds029817.mongolab.com"
  dbPort = 29817
  dbUsername = secrets.dbUsername
  dbPassword = secrets.dbPassword
else:
  dbHost = "localhost"
  dbPort = 27017

# Users
iconSize = 75,75
maxNearbyUserDistance = 5
startingBetaKeys = 3

# Comments
minimumCommentLengthInCharacters = 1
maxCommentsOnUserpages = 5

# Art
pageViewsRequireAlternateIP = False
featuresBeforeConsideration = 10

# Gallery
displayedWorksPerPage = 30
pageIndexes = 15

# Uploads
usingS3 = True

uploadsDir      = "uploads"
iconsDir        = os.path.join(uploadsDir, "icons")
artDir          = os.path.join(uploadsDir, "art")
thumbDir        = os.path.join(uploadsDir, "thumbs")

imageExtensions = set(['png', 'jpg', 'jpeg', 'gif', 'tif', 'svg'])
iconExtensions  = imageExtensions

thumbnailDimensions = 135,110
thumbnailFormat     = "PNG"
thumbnailExtension  = ".thumbnail.png"

maxFileSize      = 20 * 1024**2
maxFileSizeText  = "Twenty Megabytes"

maxIconSize      = 2 * 1024**2
maxIconSizeText  = "Two Megabytes"
maxImageSize     = 8 * 1024**2
maxImageSizeText = "Eight Megabytes"

# Error Messages
fileTypeError = "The file you uploaded had an incorrect filetype. "
fileSizeError = "The file you uploaded was too large. "

# Captcha API
if usingSecrets:
  captchaPublicKey = secrets.captchaPublic
  captchaSecretKey = secrets.captchaSecret
else:
  captchaPublicKey = None
  captchaSecretKey = None
