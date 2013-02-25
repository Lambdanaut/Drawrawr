import os
using_secrets=True
try: import secrets
except ImportError: using_secrets=False

# Server
host = '0.0.0.0'
port = int(os.environ.get("PORT", 80))

# Production
logging           = False
debug             = True
beta_key          = False
random_secret_key = False
captcha           = False
advertisements    = False

# Database
if using_secrets:
  dbHost     = "ds029817.mongolab.com"
  dbPort     = 29817
  dbUsername = secrets.dbUsername
  dbPassword = secrets.dbPassword
else:
  dbHost = "localhost"
  dbPort = 27017
dbDatabase = "drawrawr"

# Users
icon_size = 75,75
max_nearby_user_distance = 5
starting_beta_keys = 3
reserved_usernames = ["users","art","journal","meta","clubs","search"]

# Passwords
short_salt_1 = "SDDG$##@Hfa"
short_salt_2 = "3r#$^&2andgjngds"
long_salt_1  = "#%!DD"
long_salt_2  = "$#&#N%JN323##)(#@#fmmhsppf{s}{[|11^^^43n4jfw@-"

# Comments
minimum_comment_length_in_characters = 1
max_comments_on_userpages = 5

# Art
page_views_require_alternate_IP = False
features_before_consideration = 10

# Gallery
displayed_works_per_page = 50
page_indexes = 15

# Uploads
using_S3 = False
S3_bucket_name = "drawrawr"

uploads_dir      = "uploads"
icons_dir        = os.path.join(uploads_dir, "icons")
art_dir          = os.path.join(uploads_dir, "art")
thumb_dir        = os.path.join(uploads_dir, "thumbs")

image_extensions = ['png', 'jpg', 'jpeg', 'gif', 'tif', 'svg']
animation_extensions = ['swf']
icon_extensions  = image_extensions

thumbnail_dimensions = 135,110
thumbnail_format     = "PNG"
thumbnail_extension  = ".thumbnail.png"

max_file_size       = 20 * 1024**2
max_file_size_text  = "Twenty Megabytes"

max_icon_size           = 2 * 1024**2
max_icon_size_text      = "Two Megabytes"
max_image_size          = 8 * 1024**2
max_image_size_text     = "Eight Megabytes"
max_animation_size      = 15 * 1024**2
max_animation_size_text = "Fifteen Megabytes"

# Error Messages
file_type_error = "The file you uploaded had an incorrect filetype. "
file_size_error = "The file you uploaded was too large. "

# Error Pages
page_not_found_images = [
  "scary404.png"
, "vonderdevil404.png"
, "cute404.png"
, "bomb404.png"
, "bile404.png"
, "sexy404.png"
, "browniexxx404.png"
]

# Captcha API
if using_secrets and captcha:
  captcha_public_key = secrets.captcha_public
  captcha_secret_key = secrets.captcha_secret
else:
  captcha_public_key = None
  captcha_secret_key = None