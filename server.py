from flask import *
import werkzeug
import pymongo

from PIL import Image

import os, math, shutil, mimetypes, sys, random, logging, datetime, base64

import system.captcha as captcha
import system.config as config
import system.cryptography as cryptography
import system.ignored_keywords as ignored_keywords
import system.models as models
import system.setup as setup
import system.usercode as usercode
import system.util as util

if config.using_S3:
  from system.S3 import S3
else:
  from system.local_storage import Local_Storage

# Create Application
app = Flask(__name__)

# Jinja Settings
app.jinja_env.trim_blocks = True

# Secret Key
if config.random_secret_key: app.secret_key = os.urandom(24)
else                       : app.secret_key = "0"

# Add Config
app.config['MAX_CONTENT_LENGTH'] = config.max_file_size

# File Storage
if config.using_S3: storage = S3()
else:               storage = Local_Storage()

# Logging
if config.logging: logging.basicConfig(filename='logs/DR.log',level=logging.DEBUG)

# Database
users_model     = models.Users()
art_model       = models.Art()
journals_model  = models.Journals()
comments_model  = models.Comments()
keys_model      = models.Keys()
beta_pass_model = models.Beta_Pass()

def main():
  # First Start Setup
  setup.main(models.db)

  # Run Server
  app.run(host=config.host,port=config.port,debug=config.debug)

@app.before_request
def before_request():
  if "username" and "password" in session:
    user = users_model.get_one({'lowername' : session["username"].lower(), 'password' : session["password"] }) 
    g.logged_in_user = user
  else: g.logged_in_user = None

@app.before_request
def remove_trailing_slash():
  """Redirects the URL to remove trailing slashes"""
  if request.path != '/' and request.path.endswith('/'):
    return redirect(request.path[:-1])

@app.context_processor
def inject_user():
  """Feeds essential variables into every template"""
  if g.logged_in_user: show_ads = g.logged_in_user["show_ads"]
  else:                show_ads = True
  return dict (logged_in_user = g.logged_in_user, show_ads = show_ads, util = util, config=config, any = any, str = str)

@app.route('/')
def index():
  """The Drawrawr Front Page"""
  # Get Arts
  recent_art = art_model.get().limit(30).sort("_id",-1)
  popular_art = art_model.get( {"fav_amount" : {"$gt" : 0 } } ).sort("favorites",-1).limit(12)
  featured_art = []

  # Get New Users
  new_users_result = users_model.get().sort("_id",1).limit(20)
  new_users = []
  for user in new_users_result:
    new_users.append(user["username"])

  return render_template("index.html",recent_art=recent_art,popular_art=popular_art,featured_art=featured_art,new_users=new_users)

@app.route('/<username>')
def userpage(username):
  """Renders the user's homepage"""
  user = users_model.get_one({"lowername": username.lower() })
  if user:
    # Increment Page Views
    users_model.increment_views({"_id": user['_id']})
    # Gallery Module
    gallery = None
    if user["layout"]["gallery"][0] != "h":
      gallery = art_model.get({"author_ID": user["_id"]}).limit(15).sort("_id",-1)
      if gallery.count() == 0: gallery = None
    else: gallery = None
    # Nearby Users Module
    # It's rather naive in that the processing is done by the server and not the database. It may be a problem in the future. 
    close_users = None
    if user["layout"]["nearby"][0] != "h" and user["latitude"] and user["longitude"]:
      all_users = users_model.get({"_id": {"$ne" : user["_id"]} , "latitude" : {"$ne" : None}, "longitude" : {"$ne" : None} })
      close_users = []
      for aUser in all_users:
        if math.sqrt( (user["latitude"] - aUser["latitude"])**2 + (user["longitude"] - aUser["longitude"])**2 ) < config.max_nearby_user_distance: close_users.append(aUser["username"])
    # Journal Module
    journal_result = journals_model.get({"author_ID" : user["_id"] }).sort("_id",-1).limit(1)
    if journal_result.count() == 0: journal = None
    else: journal = journal_result[0]
    # Comment Module
    comments = None
    if user["layout"]["comments"][0] != "h":
      comments = comments_model.get({"home": user["_id"], "home_type" : "u"}).sort("_id",1).limit(config.max_comments_on_userpages)
      if comments.count() == 0: comments = None

    return render_template("user.html", user=user, userGallery=gallery, nearby_users=close_users, journal_result=journal, comment_result=comments, show_ads=False)
  else: abort(404)

@app.route('/users/login', methods=['POST'])
def login():
  """Handles logging in to Drawrawr"""
  if request.method == 'POST':
    required_parameters = ["username","password"]
    if not util.all_in_list(required_parameters, request.form):
      return "0" #ERROR, A required form element wasn't found
    user_result = users_model.get_one({'lowername' : request.form['username'].lower() })
    if not user_result:
      return "2" # No username match
    if cryptography.encrypt_password(request.form['password'], True) != user_result['password']: 
      return "3" # No password match
    session['username'] = user_result['username']
    session['password'] = user_result['password']
    session.permanent = True
    # Add the user's IP to the front of the list of his IPs
    ip = user_result["ip"]
    try: ip.remove(request.remote_addr)
    except ValueError: pass
    ip.insert(0,request.remote_addr)
    users_model.update({"lowername": user_result['lowername']}, {"ip": ip})
    return "1"

@app.route('/users/logout', methods=['POST'])
def logout():
  """Logs the user out"""
  session.pop('username', None)
  session.pop('password', None)
  return "1"

@app.route('/users/signup', methods=['POST'])
def signup(): 
  """Handles member signup requests"""
  # Error Handling
  required_parameters = ['username','password1','password2']
  if config.captcha: required_parameters += ['recaptcha_challenge_field','recaptcha_response_field']
  if config.beta_key: required_parameters += ['beta_code']
  if not util.all_in_list(required_parameters, request.form):
    return "0" #ERROR, A required form element wasn't found
  username_len = len(request.form['username'])
  if users_model.username_taken(request.form['username']) or username_len == 0 or username_len > 30:
    return "2" #ERROR, User doesn't exist or username is too small
  if request.form['password1'] != request.form['password2'] or not request.form['password1']:
    return "3" #ERROR, Passwords don't match
  if not 'tos_agree' in request.form:
    return "4" #ERROR, Terms of Service wasn't checked
  if config.captcha and not captcha.check(request.form['recaptcha_challenge_field'], request.form['recaptcha_response_field'],config.captcha_secret_key,request.remote_addr):
    return "5" #ERROR, Captcha Fail
  if config.beta_key:
    beta_key = beta_pass_model.check(request.form["beta_code"])
    if not beta_key:
      return "6" #ERROR, Beta Code Fail
  if g.logged_in_user:
    return "7" #ERROR, User is already logged in
  else: beta_key = None
  # Add the user to the database
  hashed = cryptography.encrypt_password(request.form['password1'], True)
  icon_filepath = os.path.join(config.icons_dir, request.form['username'].lower())
  storage.push("static/images/newby_icon.png", icon_filepath, mimetype="image/png")
  if not config.using_S3: shutil.copyfile("static/images/newby_icon.png", icon_filepath)
  users_model.insert({
    "username"    : request.form['username']
  , "lowername"   : request.form['username'].lower()
  , "password"    : hashed
  , "email"       : None #request.form['email']
  , "ip"          : [request.remote_addr]
  , "dob"         : None
  , "beta_key"    : beta_key
  , "beta_keys"   : config.starting_beta_keys
  , "date_joined" : datetime.datetime.today()
  , "show_ads"    : True
  , "layout"      : {
      # [CARDINAL LOCATION, ORDERING]
      # t == top; l == left; r == right; b == bottom; h == hidden
      "profile"   : ["t",0]
    , "gallery"   : ["l",0]
    , "watches"   : ["r",0]
    , "comments"  : ["b",0]
    , "nearby"    : ["r",1]
    , "journal"   : ["l",1]
    , "shout"     : ["h",0]
    , "friends"   : ["h",0]
    , "awards"    : ["h",0]
    , "shop"      : ["h",0]
    , "favorites" : ["h",0]
    , "tips"      : ["h",0]
    , "chars"     : ["h",0]
    , "playlist"  : ["h",0]
    }
  , "permissions" : {
      "delete_comments"    : True
    , "edit_art"           : True
    , "delete_art"         : True
    , "delete_journal"     : True
    , "ban_users"          : True
    , "make_props"         : True
    , "vote"               : True
    , "generate_beta_pass" : True
    , "crop_art"           : True
    }
  , "latitude"     : None
  , "longitude"    : None
  , "theme"        : "default"
  , "profile"      : ""
  , "code_profile" : ""
  , "page_views"   : 0
  , "watchers"     : []
  , "bground"      : None
  , "icon"         : "png"
  , "glued"        : 1
    # m == Male; f == Female; h == Hide Gender
  , "gender"       : "h"
  }) 
  session['username'] = request.form['username']
  session['password'] = hashed
  session.permanent = True
  return "1" #SUCCESS

@app.route('/users/glue', methods=['GET','POST'])
def glue():
  """
  Glues and Unglues the header from the top of the screen. 
  If the user is logged in, this function will record the header's new state.
  """
  if request.method == 'GET':
    if 'username' in session:
      if g.logged_in_user:
        return str(g.logged_in_user["glued"])
      else: return "1"
    else: return "0"
  elif request.method == 'POST':
    if g.logged_in_user:
      users_model.update({"lowername": g.logged_in_user['lowername']}, {"glued": request.form['glued']})
      return "1"
    else: return "0"

@app.route('/users/watch', methods=['GET','POST'])
def watch():
  """Handles user watching and de-watching"""
  if request.method == 'GET':
    # This needs to return a list of watchers or something
    return "0"
  elif request.method == 'POST':
    if g.logged_in_user:
      watched_user = request.form["watched_user"]
      if g.logged_in_user["lowername"] != watched_user.lower():
        user_result = users_model.get_one({"lowername" : watched_user.lower()})
        if g.logged_in_user["username"] in user_result["watchers"]:
          users_model.update({"lowername" : watched_user.lower()}, {"watchers" : g.logged_in_user["username"] }, "$pull")
        else:
          watchers = user_result["watchers"]
          watchers.insert(0, g.logged_in_user["username"])
          users_model.update({"lowername" : watched_user.lower()},{"watchers" : watchers} )
        return "1"
      else:
        if config.logging: logging.warning("User \"" + watched_user + "\" tried to watch themself. The procedure failed, but it's a bit weird that they should even be able to do this. Keep a watch out for them. ")
        return "0"
    else: abort(401)

# TODO:
# Optimize Settings by building up one single dictionary to push to the database, rather than running multiple queries. 
@app.route('/users/settings', methods=['GET','POST'])
def settings():
  """The user's settings page. Used for changing their profile, account settings, and homepage."""
  if g.logged_in_user:
    if request.method == 'GET':
      if config.beta_key: beta_keys = beta_pass_model.get({"owner" : g.logged_in_user["username"] })
      else: beta_keys = None
      return render_template("settings.html", beta_keys = beta_keys)
    elif request.method == 'POST':
      # User Messages
      messages = []
      # User Icon
      icon = request.files['icon_upload']
      if icon:
        print icon.content_length
        if not icon.content_length <= config.max_icon_size:
          flash(config.file_size_error + "Your icon must be at most " + config.max_icon_size_text + ". ")
        else:
          if not util.allowed_file(icon.filename,config.icon_extensions):
            flash(config.file_type_error + "The allowed extensions are " + util.print_list(config.icon_extensions) + ". ")
          else: 
            try: os.remove(os.path.join(config.icons_dir, g.logged_in_user['lowername'] + "." + g.logged_in_user["icon"]))
            except: 
              if config.logging: logging.warning("Couldn't remove user \"" + g.logged_in_user['username']+ "\"'s old icon while attempting to upload a new icon. ")
            fileName = g.logged_in_user['lowername']
            fileType = util.fileType(icon.filename)
            if fileType.lower() == "jpg": fileType = "jpeg" # Change filetype for PIL
            (mimetype,i) = mimetypes.guess_type(icon.filename)
            file_location = os.path.join(config.icons_dir, fileName)
            users_model.update({"lowername": g.logged_in_user['lowername']}, {"icon": fileType} )
            icon.save(file_location)
            image = Image.open(file_location)
            resized = image.resize(config.icon_size, Image.ANTIALIAS)
            resized.save(file_location, fileType, quality=100)
            storage.push(file_location, file_location, mimetype = mimetype )
            messages.append("User Icon")
      # Password
      if request.form["change_pass_current"] and request.form["change_pass_new_1"] and request.form["change_pass_new_2"]:
        if cryptography.encrypt_password(request.form["change_pass_current"], True) != g.logged_in_user['password']:
          flash("The new password you gave didn't match the one in the database! ):")
        elif request.form["change_pass_new_1"] != request.form["change_pass_new_2"]:
          flash("The new passwords you gave don't match! Try retyping them carefully. ")
        else:
          hashed = cryptography.encrypt_password(request.form['change_pass_new_1'], True)
          users_model.update({"_id": g.logged_in_user['_id']}, {"password": hashed} )
          session['password']=hashed
          messages.append("Password")
      # Gender
      if request.form["change_gender"] != g.logged_in_user["gender"]:
        users_model.update({"_id": g.logged_in_user['_id']}, {"gender": request.form["change_gender"] })
        messages.append("Gender")
      # Location
      if request.form["change_latitude"] != str(g.logged_in_user["latitude"]) or request.form["change_longitude"] != str(g.logged_in_user["longitude"]):
        try:
          latFloat = float(request.form["change_latitude"])
          lonFloat = float(request.form["change_longitude"])
          users_model.update({"_id": g.logged_in_user['_id']}, {"latitude": latFloat, "longitude": lonFloat } )
          messages.append("Location")
        except ValueError:
          flash("The locations you gave were invalid latitude and longitude coordinates! ): ")
      # Profile
      if request.form["change_profile"] != g.logged_in_user["profile"]:
        users_model.update({"_id": g.logged_in_user['_id']}, {"profile": request.form["change_profile"], "code_profile": usercode.parse(request.form["change_profile"]) })
        messages.append("Profile")
      # Color Theme
      if request.form["change_color_theme"] != g.logged_in_user["theme"]:
        users_model.update({"_id": g.logged_in_user['_id']}, {"theme": request.form["change_color_theme"]} )
        messages.append("Color Theme")
      # Layout
      l1 = util.url_decode(request.form["change_layout"])
      l2 = util.url_decode(request.form["change_layout_order"])
      for key in l2: l2[key] = int(l2[key]) # Converts orderings to integers
      layout = util.conc_dict_values(l1,l2)
      if not util.compare_dicts(layout, g.logged_in_user["layout"]):
        if util.compare_dict_keys(layout, g.logged_in_user["layout"]):
          layout_to_push = {}
          for key in layout:
            layout_to_push["layout." + key] = layout[key]
          users_model.update({"_id": g.logged_in_user['_id']}, layout_to_push)
          messages.append("Layout")
      return render_template("settings_success.html",messages=messages,len=len)
  else: abort(401)

@app.route('/<username>/comment/<int:commentID>', methods=['GET'])
@app.route('/art/<int:art>/comment/<int:commentID>', methods=['GET'])
@app.route('/journal/view/<int:journal>/comment/<int:commentID>', methods=['GET'])
@app.route('/<username>/comment', methods=['POST'])
@app.route('/art/<int:art>/comment', methods=['POST'])
@app.route('/journal/view/<int:journal>/comment', methods=['POST'])
def comment(username=None,art=None,journal=None,commentID=None):
  """Handles posting and getting comments and comment threads."""
  if request.method == 'GET':
    comment_result = comments_model.get_one({"_id" : commentID})
    if not comment_result: abort(404)
    return render_template("comment.html", comment=comment_result)
  else:
    if g.logged_in_user:
      # Filter out broken or incomplete comments
      if "parent" not in request.form or "comment_map" not in request.form or "content" not in request.form: abort(500)
      if len(request.form["content"]) < config.minimum_comment_length_in_characters: return "0"
      parent = request.form["parent"]
      comment_map = request.form["comment_map"]
      # Comment Reply
      if parent != "" and comment_map != "": 
        try: 
          parent     = int(request.form["parent"])
          comment_map = util.parse_comment_map(request.form["comment_map"])
        except ValueError: abort(500)
        comments_model.update( { "_id" : parent }, { comment_map : {
            "author_ID"    : g.logged_in_user["_id"]
          , "author"       : g.logged_in_user["username"]
          , "content"      : request.form["content"]
          , "code_content" : usercode.parse(request.form["content"])
          , "r"            : []
          , "date"         : datetime.datetime.today()
          } }
        , "$push")
        return "1"
      # Top Level Comment
      else:
        if username:
          location = "u"
          user_lookup = users_model.get_one({"lowername" : username.lower()})
          if user_lookup: home = user_lookup["_id"]
          else: abort(500)
        elif art:
          location = "a"
          home = art
        elif journal:
          location = "j"
          home = journal
        else: abort(500)
        comments_model.insert({
          "author_ID"    : g.logged_in_user["_id"]
        , "author"       : g.logged_in_user["username"]
        , "content"      : request.form["content"]
        , "code_content" : usercode.parse(request.form["content"])
        , "r"            : []
        , "home"         : home
        , "home_type"    : location
        , "date"         : datetime.datetime.today()
        })
        return "1"

    else: abort(401)

@app.route('/users/welcome', methods=['GET'])
def welcome():
  """A welcome page displayed to new members that have just signed up"""
  return render_template("welcome.html")

@app.route('/art/<int:art>', methods=['GET','DELETE'])
def view_art(art):
  """Displays the artwork of whichever ID is passed in, along with comments, and information about the artwork."""
  try: 
    art_lookup = art_model.get_one({'_id' : art})
  except ValueError: abort(404)
  if not art_lookup: abort(404)
  if request.method == 'GET':
    author_lookup = users_model.get_one({'_id' : art_lookup["author_ID"]})
    # Increment Art Views
    inc_views = True
    if g.logged_in_user: inc_views = not g.logged_in_user["_id"] == author_lookup["_id"]
    if config.page_views_require_alternate_IP: not request.remote_addr in author_lookup["ip"]
    if inc_views: art_model.increment_views({"_id": art})
    return render_template("art.html", art=art_lookup, author=author_lookup )
  elif request.method == 'DELETE':
    if g.logged_in_user:
      if art_lookup["author_ID"] == g.logged_in_user["_id"] or g.logged_in_user["permissions"]["delete_art"]:
        # Delete File
        storage.delete(os.path.join(config.art_dir , str(art_lookup['_id']) + "." + art_lookup['filetype'] ) )
        # Delete From Database
        art_model.delete({'_id' : art_lookup['_id']})
        flash("Your artwork <b>" + art_lookup["title"] + "</b> was deleted successfully! ")
        return "1"
      else: abort(401)

@app.route('/art/<int:art>/feature', methods=['POST'])
def feature_art(art):
  """Handles feature suggestion of an artwork by users. """
  try: 
    art_lookup = art_model.get_one({'_id' : art})
  except ValueError: abort(404)
  if not art_lookup: abort(404)
  if not "featured_text" in request.form: abort(500)
  art_model.suggest_feature ({
    "author"  : g.logged_in_user["username"]
  , "art_ID"  : art
  , "content" : request.form["featured_text"]
  , "date"    : datetime.datetime.today()
  })
  feature_count = art_model.get_feature({"art_ID" : art}).count()
  flash("Your feature suggestion was submitted successfully. If " + str(config.features_before_consideration - feature_count) + " more users request this artwork to be featured, then staff will be notified. " )
  return redirect(url_for("view_art", art=art))

@app.route('/art/<int:art>/favorite', methods=['POST','GET'])
def favorite(art):
  """Handles favoriting and de-favoriting artworks"""
  if g.logged_in_user:
    if request.method == 'POST':
      fav = art_model.get_one({"_id" : art})
      if g.logged_in_user != fav["author"]:
        if g.logged_in_user["username"] in fav["favorites"]:
          art_model.art.update({"_id" : art}, {"$pull" : {"favorites" : g.logged_in_user["username"] } , "$inc" : {"fav_amount": -1 } } )
        else:
          art_model.art.update({"_id" : art}, {"$addToSet" : {"favorites" : g.logged_in_user["username"] } , "$inc" : {"fav_amount": 1 } } )
        return "1"
      else: return "0"
    else:
      # The GET method returns 1 if the user has fav'd this art, and a 0 if they're not. 
      fav = art_model.get_one({"_id" : art})
      if g.logged_in_user["username"] in fav["favorites"]: return "1"
      else:                                              return "0"
  else: abort(401)

@app.route('/<username>/gallery', defaults={'folder': "all", 'page': 0}, methods=['GET'])
@app.route('/<username>/gallery/<folder>', defaults={'page': 0}, methods=['GET'])
@app.route('/<username>/gallery/<folder>/<int:page>', methods=['GET'])
def view_gallery(username,folder,page):
  """Displays a user's gallery or favorites, filtered and ordered based on given GET parameters."""
  author_lookup = users_model.get_one({'lowername' : username.lower()})
  if not author_lookup: abort(404)
  else:
    sort  = "d"
    order = "d"
    if "sort" in request.args: sort = request.args["sort"]
    if "order" in request.args: order = request.args["order"]
    if order == "d": user_order = -1
    else:            user_order = 1
    if   sort == "t": user_sort = "title"
    elif sort == "p": user_sort = "fav_amount"
    else:             user_sort = "_id"
    if folder=="all":
      art_lookup = art_model.get({'author' : author_lookup["username"]}).skip(config.displayed_works_per_page * page).limit( config.displayed_works_per_page ).sort(user_sort,user_order)
    elif folder=="mature":
      art_lookup = art_model.get({'author' : author_lookup["username"], 'mature' : True}).skip(config.displayed_works_per_page * page).limit( config.displayed_works_per_page ).sort(user_sort,user_order)
    elif folder=="favorites":
      art_lookup = art_model.get({'favorites' : {"$in" : [author_lookup["username"] ] } } ).skip(config.displayed_works_per_page * page).limit( config.displayed_works_per_page ).sort(user_sort,user_order)
    else:
      art_lookup = art_model.get({'author' : author_lookup["username"], 'folder' : folder}).skip(config.displayed_works_per_page * page).limit( config.displayed_works_per_page ).sort(user_sort,user_order)
    # Create page index
    art_count = art_lookup.count()
    if not art_count: art_lookup = None
    if art_count % config.displayed_works_per_page: extra_page = 1
    else:                                           extra_page = 0
    pages = range(0,(art_count / config.displayed_works_per_page) + extra_page)
    page_count = len(pages)
    pages_left = len(pages[page:])
    if pages_left > config.page_indexes:
      pages = pages[page: page + config.page_indexes]
      more = True
    else:
      pages = pages[page: page + pages_left]
      more = False
    return render_template("gallery.html", art=art_lookup, author=author_lookup, folder=folder, sort=sort, order=order, current_page=page, pages=pages, last=page_count - 1)

@app.route('/art/do/submit', methods=['GET','POST'])
def submit_art():
  """Displays the artwork submission page and handles the submission of artworks."""
  if g.logged_in_user:
    if request.method == 'GET':
        return render_template("submit.html")
    else:
      # Form Validation
      if not ("title" in request.form and "description" in request.form) : 
        abort(500)
      elif not request.form["title"]:
        flash("Your title must not be left blank. ")
      art = request.files['upload']
      art_type = None

      # Image
      if request.form["art_type"] == "image":
        if not util.allowed_file(art.filename, config.image_extensions):
          flash(config.file_type_error + "The allowed filetypes are " + util.print_list(config.image_extensions) + ". ")
        elif art.content_length >= config.max_image_size:
          flash(config.file_size_error + "Your image must be at most " + config.max_image_size_text + ". ")
        else: art_type = "image"
      # Audio
      # Literature
      # Animation
      if request.form["art_type"] == "animation":
        if not util.allowed_file(art.filename, config.animation_extensions):
          flash(config.file_type_error + "Your animation must be a " + util.print_list(config.animation_extensions) + " file. ")
        elif art.content_length >= config.max_animation_size:
          flash(config.file_size_error + "Your .swf file must be at most " + config.max_image_size_text + ". ")
        else: art_type = "animation"
      # Craft
      # Cullinary
      # Performance

      if art_type:
        fileType = util.fileType(art.filename)
        key = keys_model.next("art")
        file_location = os.path.join(config.art_dir, str(key) + "." + fileType)
        art.save(file_location)
        storage.push(file_location, file_location)
        art_model.insert({
          "_id"         : key
        , "title"       : request.form["title"]
        , "description" : request.form["description"]
        , "code_desc"   : usercode.parse(request.form["description"])
        , "author"      : g.logged_in_user["username"]
        , "author_ID"   : g.logged_in_user["_id"]
        , "keywords"    : filter (lambda keyword: not keyword in ignored_keywords.commonWords, map(lambda keyword: keyword.lower() , request.form["title"].split() ) )
        , "mature"      : False
        , "folder"      : "complete"
        , "favorites"   : []
        , "fav_amount"  : 0
        , "views"       : 0
        , "date"        : datetime.datetime.today()
        , "filetype"    : fileType
        , "type"        : art_type
        })
        if type == "image":
          autocrop(key)
          return redirect(url_for('crop',art=key))
        else:
          return redirect(url_for('view_art',art=key))
      return redirect(url_for('submit_art'))
    return redirect(url_for('submit_art'))
  else: abort(401)

@app.route('/art/do/autocrop/<int:art>',methods=['POST'])
def autocrop(art):
  """Automatically creates a crappily cropped temporary thumbnail for an artwork. Used as the default thumbnail until the user crops a better one. """
  if g.logged_in_user:
    art_lookup = art_model.get_one({'_id' : art})
    if not art_lookup: abort(404)
    if not g.logged_in_user["_id"] == art_lookup["author_ID"] and not g.logged_in_user["permissions"]["crop_art"]: abort(401)
    image_location = os.path.join(config.art_dir, str(art_lookup["_id"]) + "." + art_lookup["filetype"] )
    storage.download(image_location)
    image = Image.open(image_location)
    cropped = image.resize(config.thumbnail_dimensions,Image.ANTIALIAS)
    cropped_location = os.path.join(config.thumb_dir, str(art_lookup["_id"]) + config.thumbnail_extension)
    cropped.save(cropped_location, config.thumbnail_format, quality=100)
    storage.push(cropped_location, cropped_location)
    return "1"
  else: abort(401)

@app.route('/art/do/crop/<int:art>', methods=['GET','POST'])
def crop(art):
  """Displays a page for the user to crop out a thumbnail from their artwork and handles cropping requests."""
  if g.logged_in_user:
    art_lookup = art_model.get_one({'_id' : art})
    if not art_lookup: abort(404)
    if not g.logged_in_user["_id"] == art_lookup["author_ID"] and not g.logged_in_user["permissions"]["crop_art"]: abort(401)
    if request.method == 'GET':
      if not art_lookup: abort(404)
      return render_template("crop.html",art=art_lookup)
    else: 
      image_location = os.path.join(config.art_dir, str(art_lookup["_id"]) + "." + art_lookup["filetype"] )
      storage.download(image_location)
      image = Image.open(image_location)
      crop_area = int(request.form["x"]),int(request.form["y"]),int(request.form["x"]) + int(request.form["w"]), int(request.form["y"]) + int(request.form["h"])
      cropped = image.crop(crop_area).resize(config.thumbnail_dimensions,Image.ANTIALIAS)
      cropped_location = os.path.join(config.thumb_dir, str(art_lookup["_id"]) + config.thumbnail_extension)
      cropped.save(cropped_location, config.thumbnail_format, quality=100)
      storage.push(cropped_location, cropped_location)
      return redirect(url_for('view_art',art=art))
  else: abort(401)

@app.route('/<username>/journals', methods=['GET'])
def view_user_journals(username):
  """Redirects to the most recent journal for a given user."""
  owner_result = users_model.get_one({"lowername" : username.lower() })
  if not owner_result: abort(404)
  journal_result = journals_model.get({"author_ID" : owner_result["_id"] }).limit(1).sort("_id",-1)
  if journal_result.count() == 0: 
    flash(username + " hasn't posted any journals yet. ")
    abort(404)
  return redirect(url_for('view_journal', journal = journal_result[0]["_id"]) )

@app.route('/journal/view/<int:journal>', methods=['GET'])
def view_journal(journal):
  """Views a specific journal given its ID."""
  journal_result = journals_model.get_one({"_id" : journal })
  if not journal_result: abort(404)
  journals_model.increment_views({"_id": journal})
  all_journals = journals_model.get({"author_ID" : journal_result['author_ID'] }).sort("_id",-1)
  return render_template("view_journal.html", journal=journal_result, all_journals=all_journals)

@app.route('/journal/edit/<int:journal>', methods=['GET', 'POST'])
def edit_journal(journal):
  """Edits a specific journal given its ID"""
  if g.logged_in_user:
    journal_result = journals_model.get_one({"_id" : journal })
    if not journal_result: abort(404)
    if g.logged_in_user["_id"] != journal_result['author_ID']: abort(401)
    if request.method == 'GET':
      all_journals = journals_model.get({"author_ID" : g.logged_in_user['_id'] }).sort("_id",-1)
      return render_template("edit_journal.html", journal=journal_result, all_journals=all_journals)
    elif request.method == 'POST':
        if "journal_title" in request.form and "journal_content" in request.form and "journal_mood" in request.form:
          if request.form["journal_title"].strip() != "":
            journals_model.update({"_id": journal}, {"title": request.form["journal_title"], "content": request.form["journal_content"], "code_content": usercode.parse(request.form["journal_content"]), "mood": request.form["journal_mood"] })
            flash("Journal edited successfully! ")
            return redirect(url_for('view_journal', journal = journal) )
  else: abort(401)

@app.route('/journal/delete/<int:journal>', methods=['POST'])
def delete_journal(journal):
  """Deletes a journal given its ID"""
  if g.logged_in_user:
    journal_result = journals_model.get_one({"_id" : journal })
    if not journal_result: abort(404)
    if g.logged_in_user["_id"] != journal_result['author_ID'] and not g.logged_in_user["permissions"]["delete_journal"]: abort(401)
    journals_model.delete({"_id" : journal})
    return "1"


@app.route('/journal/manage', methods=['GET','POST'])
def manage_journal():
  """
  Renders a page for posting a new journal, with links to edit past journals. 
  Handles the posting of new journals. 
  """
  if g.logged_in_user:
    if request.method == 'GET':
      all_journals = journals_model.get({"author_ID" : g.logged_in_user['_id'] }).sort("_id",-1)
      return render_template("manage_journals.html", all_journals = all_journals)
    else:
      if not "journal_title" in request.form or not "journal_content" in request.form or not "journal_mood" in request.form: abort(500)
      if request.form["journal_title"].strip() == "": return "0" # ERROR: 
      key = keys_model.next("journals")
      journals_model.insert({
        "_id"          : key
      , "title"        : request.form["journal_title"]
      , "content"      : request.form["journal_content"]
      , "code_content" : usercode.parse(request.form["journal_content"])
      , "mood"         : request.form["journal_mood"]
      , "author"       : g.logged_in_user["username"]
      , "author_ID"    : g.logged_in_user["_id"]
      , "views"        : 0
      , "date"         : datetime.datetime.today()
      })
      return redirect(url_for('view_journal',journal=key))
      
  else: abort(401)    

@app.route('/clubs')
def clubs():
  """Dummy Clubs Page"""
  return render_template("clubs.html")

@app.route('/clubs/edit',  methods=['GET','POST'])
def clubs_edit():
  """Dummy Clubs Page"""
  return render_template("club_edit.html")

@app.route('/clubs/view/<clubName>')
def clubpage(clubName):
  """Dummy Clubs Page"""
  return render_template("clubpage.html")

@app.route('/search', defaults={'page': 0} )
@app.route('/search/<int:page>', methods=['GET'])
def search(page):
  """
  Displays a page for searching Drawrawr for artworks based on given criteria.
  By default, the most recent artworks are displayed.
  """
  sort  = "d"
  order = "d"
  keywords = []
  if "sort" in request.args: sort = request.args["sort"]
  if "order" in request.args: order = request.args["order"]
  if "keywords" in request.args: keywords = request.args["keywords"].split()
  if order == "d": user_order = -1
  else:            user_order = 1
  if   sort == "t": user_sort = "title"
  elif sort == "p": user_sort = "fav_amount"
  else:             user_sort = "_id"
  if keywords:
    art_lookup = art_model.get({"keywords" : {"$in": map(lambda keyword: keyword.lower(), keywords) } } ).skip(config.displayed_works_per_page * page).limit( config.displayed_works_per_page ).sort(user_sort,user_order)
  else:
    art_lookup = art_model.get().skip(config.displayed_works_per_page * page).limit( config.displayed_works_per_page ).sort(user_sort,user_order)
  # Create page index
  art_count = art_lookup.count()
  if not art_count: art_lookup = None
  if art_count % config.displayed_works_per_page: extra_page = 1
  else:                                       extra_page = 0
  pages = range(0,(art_count / config.displayed_works_per_page) + extra_page)
  page_count = len(pages)
  pages_left = len(pages[page:])
  if pages_left > config.page_indexes:
    pages = pages[page: page + config.page_indexes]
    more = True
  else:
    pages = pages[page: page + pages_left]
    more = False
  return render_template("search.html", art=art_lookup, keywords=util.unsplit(keywords), sort=sort, order=order, current_page=page, pages=pages, last=page_count - 1)

@app.route('/art/uploads/<filename>')
def art_file(filename):
  """Grabs an artwork file from storage."""
  return storage.get(os.path.join(config.art_dir,filename ) )

@app.route('/art/uploads/thumbs/<filename>')
def thumb_file(filename):
  """Grabs an artwork's thumbnail file from storage."""
  return storage.get(os.path.join(config.thumb_dir,filename ) )

@app.route('/icons/<filename>')
def icon_files(filename):
  """Grabs a user's icon file from storage."""
  return storage.get(os.path.join(config.icons_dir,filename ) )

@app.route('/util/parse_usercode/<text>')
def parse_usercode(text):
  """Given usercode text, parses it into HTML and returns it."""
  return usercode.parse(text)

@app.route('/admin/generate_beta_pass',methods=['POST'])
def generate_beta_pass():
  """Generates and returns a new beta key for the user."""
  if g.logged_in_user:
    if g.logged_in_user["permissions"]["generate_beta_pass"]:
      return beta_pass_model.generate(ownerName=g.logged_in_user["username"])
    elif g.logged_in_user["beta_keys"] > 0:
      users_model.increment_beta_keys({"_id" : g.logged_in_user["_id"]}, -1)
      return beta_pass_model.generate(ownerName=g.logged_in_user["username"])
    else: abort(401)
  else: abort(401)

@app.route('/api/update_count',methods=['GET'])
def update_count():
  """Returns the number of updates for a member."""
  try:
    username = request.args.get('username')
    password = request.args.get('password')
  except KeyError:
    return "Error: Invalid request"
  if username and password:
    if users_model.user_pass_check(username,password):
      pass
    else: return "Error: Invalid Username/Password combo"
  else: return "Error: Invalid request"

@app.route('/meta/terms_of_service', methods=['GET'])
def terms_of_service():
  """Displays the Drawrawr Terms of Service, loaded from a text file. """
  f = open("static/legal/tos")
  tos = f.read()
  return render_template("tos.html", tos=tos)

@app.route('/meta/about', methods=['GET'])
def about():
  """Displays a page about Drawrawr"""
  return render_template("about.html")

@app.route('/meta/donate', methods=['GET'])
def donate():
  """Displays the donations page"""
  return render_template("donate.html")

@app.route('/meta/staff')
def staff():
  """Displays the staff-only page. A member must have at least one moderator-granted permission to view it. """
  if g.logged_in_user:
    if any(util.dict_to_list(g.logged_in_user["permissions"]) ): 
      users = users_model.get()
      art   = art_model.get()
      return render_template("staff.html", userCount=users.count(), art_count=art.count() )
    else: abort(401)
  else: abort(401)

@app.errorhandler(401)
def unauthorized(e):
  return render_template('401.html'), 401

@app.errorhandler(404)
def page_not_found(e):
  randimg = config.page_not_found_images[random.randint(0,len(config.page_not_found_images) - 1)]
  return render_template('404.html',randimg=randimg), 404

@app.errorhandler(500)
def internal_error(e):
  return render_template('500.html'), 500