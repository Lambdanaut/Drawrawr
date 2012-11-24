from flask import *
import werkzeug

import os, math, mimetypes, sys, random, logging, datetime, base64

from PIL import Image

from system.database import Database
from system.S3 import S3

import system.captcha as captcha
import system.config as config
import system.cryptography
import system.ignored_keywords as ignored_keywords
import system.models as models
import system.setup as setup
import system.usercode as usercode
import system.util as util

# Create Application
app = Flask(__name__)
app.jinja_env.trim_blocks = True

# Secret Key
if config.random_secret_key: app.secret_key = os.urandom(24)
else                     : app.secret_key = "0"

# Add Config
app.config['MAX_CONTENT_LENGTH'] = config.max_file_size

storage = S3()

if config.logging: logging.basicConfig(filename='logs/DR.log',level=logging.DEBUG)

# Database
db_con = pymongo.Connection(config.dbHost,config.dbPort)
db     = db_con.heroku_app2925802
db.authenticate(config.dbUsername, config.dbPassword)

users_model = models.Users(db)
keys_model  = models.Keys(db)
beta_pass_model  = models.Beta_Pass(db)

def main():
  # First Start Setup
  setup.main(db)

  # Run Server
  app.run(host=config.host,port=config.port,debug=config.debug)

@app.before_request
def before_request():
  if "username" and "password" in session:
    user = db.db.users.find_one({'lowername' : session["username"].lower(), 'password' : session["password"] }) 
    g.logged_in_user = user
  else: g.logged_in_user = None

@app.context_processor
def inject_user():
  if g.logged_in_user: show_ads = g.logged_in_user["show_ads"]
  else:              show_ads = True
  return dict (logged_in_user = g.logged_in_user, show_ads = show_ads, util = util, config=config, any = any, str = str)

@app.route('/')
def index():
  # Get Arts
  recentArt = db.db.art.find().limit(30).sort("_id",-1)
  popular_art = db.db.art.find( {"fav_amount" : {"$gt" : 0 } } ).sort("favorites",-1).limit(12)
  featured_art = []

  # Get New Users
  new_users_result = db.db.users.find().sort("_id",1).limit(20)
  new_users = []
  for user in new_users_result:
    new_users.append(user["username"])

  return render_template("index.html",recentArt=recentArt,popular_art=popular_art,featured_art=featured_art,new_users=new_users)

@app.route('/<username>')
def userpage(username):
  user = users_model.get_one({"lowername": user['lowername']})
  if user:
    # Increment Page Views
    db.db.users.update({"lowername": user['lowername']}, {"$inc": {"page_views": 1} })
    # Gallery Module
    gallery = None
    if user["layout"]["gallery"][0] != "h":
      gallery = db.db.art.find({"author_ID": user["_id"]}).limit(15).sort("_id",-1)
      if gallery.count() == 0: gallery = None
    else: gallery = None
    # Nearby Users Module
    # It's rather naive in that the processing is done by the server and not the database. It may be a problem in the future. 
    close_users = None
    if user["layout"]["nearby"][0] != "h" and user["latitude"] and user["longitude"]:
      all_users = db.db.users.find({"_id": {"$ne" : user["_id"]} , "latitude" : {"$ne" : None}, "longitude" : {"$ne" : None} })
      close_users = []
      for aUser in all_users:
        if math.sqrt( (user["latitude"] - aUser["latitude"])**2 + (user["longitude"] - aUser["longitude"])**2 ) < config.max_nearby_user_distance: close_users.append(aUser["username"])
    # Journal Module
    journal = None
    if user["layout"]["journal"][0] != "h":
      journal_result = db.db.journals.find({"author_ID" : user["_id"] }).sort("_id",-1).limit(1)
      if journal_result.count() == 0: journal = None
      else: journal = journal_result[0]
    # Comment Module
    comments = None
    if user["layout"]["comments"][0] != "h":
      comments = db.db.comments.find({"home": user["_id"], "home_type" : "u"}).sort("_id",1).limit(config.max_comments_on_userpages)
      if comments.count() == 0: comments = None

    return render_template("user.html", user=user, userGallery=gallery, nearby_users=close_users, journal_result=journal, comment_result=comments, show_ads=False)
  else: abort(404)

@app.route('/users/login', methods=['POST'])
def login():
  if request.method == 'POST':
    user_result = db.db.users.find_one({'lowername' : request.form['username'].lower() })
    if user_result:
      if system.cryptography.encrypt_password(request.form['password'], True) == user_result['password']: 
        session['username'] = user_result['username']
        session['password'] = user_result['password']
        session.permanent = True
        # Add the user's IP to the front of the list of his IPs
        ip = user_result["ip"]
        try: ip.remove(request.remote_addr)
        except ValueError: pass
        ip.insert(0,request.remote_addr)
        db.db.users.update({"lowername": user_result['lowername']}, {"$set": {"ip": ip} })
        return "1"
      else: return "0"
    else: return "0"
  else: return "None"

@app.route('/users/logout', methods=['POST'])
def logout():
  session.pop('username', None)
  session.pop('password', None)
  return "1"

@app.route('/users/signup', methods=['GET', 'POST'])
def signup(): 
  if db.user_exists(request.form['username']) or len(request.form['username']) == 0 or request.form['password1'] != request.form['password2'] or request.form['tosAgree'] != 'true':
    return "0" #ERROR, User doesn't exist or username is too small
  if captcha.check(request.form['recaptcha_challenge_field'], request.form['recaptcha_response_field'],config.captcha_secret_key,request.remote_addr):
    return "2" #ERROR, Captcha Fail
  if config.beta_key:
    beta_key = db.checkBetaPass(request.form["beta_code"])
    if not beta_key:
      return "3" #ERROR, Beta Code Fail
  else: beta_key = None
  hashed = system.cryptography.encrypt_password(request.form['password1'], True)
  storage.push("static/images/newby_icon.png", os.path.join(config.icons_dir, request.form['username'].lower() ), mimetype="image/png")
  key = keys_model.next("users")
  db.db.users.insert({
    "_id"         : key
  , "username"    : request.form['username']
  , "lowername"   : request.form['username'].lower()
  , "password"    : hashed
  , "email"       : None #request.form['email']
  , "ip"          : [request.remote_addr]
  , "dob"         : None
  , "beta_key"     : beta_key
  , "beta_keys"    : config.starting_beta_keys
  , "date_joined"  : datetime.datetime.today()
  , "show_ads"     : True
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
    , "ban_users"           : True
    , "make_props"          : True
    , "vote"               : True
    , "generate_beta_pass" : True
    , "crop_art"            : True
    }
  , "latitude"    : None
  , "longitude"   : None
  , "theme"       : "default"
  , "profile"     : ""
  , "code_profile" : ""
  , "page_views"   : 0
  , "watchers"    : []
  , "bground"     : None
  , "icon"        : "png"
  , "glued"       : 1
    # m == Male; f == Female; h == Hide Gender
  , "gender"      : "h"
  }) 
  session['username'] = request.form['username']
  session['password'] = hashed
  session.permanent = True
  return "1" #SUCCESS

@app.route('/users/glue', methods=['GET','POST'])
def glue():
  if request.method == 'GET':
    if 'username' in session:
      if g.logged_in_user:
        return str(g.logged_in_user["glued"])
      else: return "1"
    else: return "1"
  elif request.method == 'POST':
    if g.logged_in_user:
      db.db.users.update({"lowername": g.logged_in_user['lowername']}, {"$set": {"glued": request.form['glued']}})
      return "1"
    else: return "0"

@app.route('/users/watch', methods=['GET','POST'])
def watch():
  if request.method == 'GET':
    # This needs to return a list of watchers or something
    return "0"
  elif request.method == 'POST':
    if g.logged_in_user:
      watchedUser = request.form["watchedUser"]
      if g.logged_in_user["lowername"] != watchedUser.lower():
        user_result = db.db.users.find_one({"lowername" : watchedUser.lower()})
        if g.logged_in_user["username"] in user_result["watchers"]:
          db.db.users.update({"lowername" : watchedUser.lower()},{"$pull" : {"watchers" : g.logged_in_user["username"] } })
        else:
          watchers = user_result["watchers"]
          watchers.insert(0, g.logged_in_user["username"])
          db.db.users.update({"lowername" : watchedUser.lower()},{"$set" : {"watchers" : watchers } } )
        return "1"
      else:
        if config.logging: logging.warning("User \"" + watchedUser + "\" tried to watch themself. The procedure failed, but it's a bit weird that they should even be able to do this. Keep a watch out for them. ")
        return "0"
    else: abort(401)

@app.route('/users/welcome', methods=['GET'])
def welcome():
  return render_template("welcome.html")

# TODO:
# Optimize Settings by building up one single dictionary to push to the database, rather than running multiple queries. 
@app.route('/users/settings', methods=['GET','POST'])
def settings():
  if g.logged_in_user:
    if request.method == 'GET':
      if config.beta_key: beta_keys = db.db.betaPass.find({"owner" : g.logged_in_user["username"] })
      else: beta_keys = None
      return render_template("settings.html", beta_keys = beta_keys)
    elif request.method == 'POST':
      # User Messages
      messages = []
      # User Icon
      icon = request.files['icon_upload']
      if icon:
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
            db.db.users.update({"lowername": g.logged_in_user['lowername']}, {"$set": {"icon": fileType } } )
            icon.save(file_location)
            image = Image.open(file_location)
            resized = image.resize(config.iconSize, Image.ANTIALIAS)
            resized.save(file_location, fileType, quality=100)
            storage.push(file_location, file_location, mimetype = mimetype )
            messages.append("User Icon")
      # Password
      if request.form["change_pass_current"] and request.form["change_pass_new_1"] and request.form["change_pass_new_2"]:
        if system.cryptography.encrypt_password(request.form["change_pass_current"], True) != g.logged_in_user['password']:
          flash("The new password you gave didn't match the one in the database! ):")
        elif request.form["change_pass_new_1"] != request.form["change_pass_new_2"]:
          flash("The new passwords you gave don't match! Try retyping them carefully. ")
        else:
          hashed = system.cryptography.encrypt_password(request.form['change_pass_new_1'], True)
          db.db.users.update({"lowername": g.logged_in_user['lowername']}, {"$set": {"password": hashed}})
          session['password']=hashed
          messages.append("Password")
      # Gender
      if request.form["change_gender"] != g.logged_in_user["gender"]:
        db.db.users.update({"lowername": g.logged_in_user['lowername']}, {"$set": {"gender": request.form["change_gender"] }})
        messages.append("Gender")
      # Location
      if request.form["change_latitude"] != str(g.logged_in_user["latitude"]) or request.form["change_longitude"] != str(g.logged_in_user["longitude"]):
        try:
          latFloat = float(request.form["change_latitude"])
          lonFloat = float(request.form["change_longitude"])
          db.db.users.update({"lowername": g.logged_in_user['lowername']}, {"$set": {"latitude": latFloat, "longitude": lonFloat } } )
          messages.append("Location")
        except ValueError:
          flash("The locations you gave were invalid latitude and longitude coordinates! ): ")
      # Profile
      if request.form["change_profile"] != g.logged_in_user["profile"]:
        db.db.users.update({"lowername": g.logged_in_user['lowername']}, {"$set": {"profile": request.form["change_profile"], "code_profile": usercode.parse(request.form["change_profile"]) } })
        messages.append("Profile")
      # Color Theme
      if request.form["change_color_theme"] != g.logged_in_user["theme"]:
        db.db.users.update({"lowername": g.logged_in_user['lowername']}, {"$set": {"theme": request.form["change_color_theme"]} })
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
          db.db.users.update({"lowername": g.logged_in_user['lowername']}, {"$set": layout_to_push })
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
  if request.method == 'GET':
    comment_result = db.db.comments.find_one({"_id" : commentID})
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
        db.db.comments.update( { "_id" : parent }, {
          "$push" : { comment_map : {
            "author_ID"    : g.logged_in_user["_id"]
          , "author"      : g.logged_in_user["username"]
          , "content"     : request.form["content"]
          , "code_content" : usercode.parse(request.form["content"])
          , "r"           : []
          , "date"        : datetime.datetime.today()
          } }
        })
        return "1"
      # Top Level Comment
      else:
        if username:
          location = "u"
          user_lookup = db.db.users.find_one({"lowername" : username.lower()})
          if user_lookup: home = user_lookup["_id"]
          else: abort(500)
        elif art:
          location = "a"
          home = art
        elif journal:
          location = "j"
          home = journal
        else         : abort(500)
        key = keys_model.next("comments")
        db.db.comments.insert({
          "_id"         : key
        , "author_ID"    : g.logged_in_user["_id"]
        , "author"      : g.logged_in_user["username"]
        , "content"     : request.form["content"]
        , "code_content" : usercode.parse(request.form["content"])
        , "r"           : []
        , "home"        : home
        , "home_type"    : location
        , "date"        : datetime.datetime.today()
        })
        return "1"

    else: abort(401)

@app.route('/meta/terms_of_service', methods=['GET'])
def policy():
  f = open("static/legal/tos")
  tos = f.read()
  return render_template("tos.html", tos=tos)

@app.route('/meta/about', methods=['GET'])
def about():
  return render_template("about.html")

@app.route('/meta/donate', methods=['GET'])
def donate():
  return render_template("donate.html")

@app.route('/art/<int:art>', methods=['GET','DELETE'])
def view_art(art):
  try: 
    art_lookup = db.db.art.find_one({'_id' : art})
  except ValueError: abort(404)
  if not art_lookup: abort(404)
  if request.method == 'GET':
    author_lookup = db.db.users.find_one({'_id' : art_lookup["author_ID"]})
    # Increment Art Views
    inc_views = True
    if g.logged_in_user: inc_views = not g.logged_in_user["_id"] == author_lookup["_id"]
    if config.page_views_require_alternate_IP: not request.remote_addr in author_lookup["ip"]
    if inc_views: db.db.art.update({"_id": art}, {"$inc": {"views": 1} })
    return render_template("art.html", art=art_lookup, author=author_lookup )
  elif request.method == 'DELETE':
    if g.logged_in_user:
      if art_lookup["author_ID"] == g.logged_in_user["_id"] or g.logged_in_user["permissions"]["delete_art"]:
        # Delete File
        storage.delete(os.path.join(config.art_dir , str(art_lookup['_id']) + "." + art_lookup['filetype'] ) )
        # Delete From Database
        db.db.art.remove({'_id' : art_lookup['_id']})
        flash("Your artwork <b>" + art_lookup["title"] + "</b> was deleted successfully! ")
        return "1"
      else: abort(401)

@app.route('/art/<int:art>/feature', methods=['POST'])
def feature_art(art):
  try: 
    art_lookup = db.db.art.find_one({'_id' : art})
  except ValueError: abort(404)
  if not art_lookup: abort(404)
  if not "featured_text" in request.form: abort(500)
  db.db.feature.insert({
    "author"  : g.logged_in_user["username"]
  , "art_ID"   : art
  , "content" : request.form["featured_text"]
  , "date"    : datetime.datetime.today()
  })
  featureCount = db.db.feature.find({"art_ID" : art}).count()
  flash("Your feature suggestion was submitted successfully. If " + str(config.features_before_consideration - featureCount) + " more users request this artwork to be featured, then staff will be notified. " )
  return redirect(url_for("view_art", art=art))

@app.route('/art/<int:art>/favorite', methods=['POST','GET'])
def favorite(art):
  if g.logged_in_user:
    if request.method == 'POST':
      fav = db.db.art.find_one({"_id" : art})
      if g.logged_in_user != fav["author"]:
        if g.logged_in_user["username"] in fav["favorites"]:
          db.db.art.update({"_id" : art}, {"$pull" : {"favorites" : g.logged_in_user["username"] }  , "$inc" : {"fav_amount": -1 } } )
        else:
          db.db.art.update({"_id" : art}, {"$addToSet" : {"favorites" : g.logged_in_user["username"] } , "$inc" : {"fav_amount": 1 } } )
        return "1"
      else: return "0"
    else:
      # The GET method returns 1 if the user has fav'd this art, and a 0 if they're not. 
      fav = db.db.art.find_one({"_id" : art})
      if g.logged_in_user["username"] in fav["favorites"]: return "1"
      else:                                              return "0"
  else: abort(401)

@app.route('/users/welcome', methods=['GET'])
def welcome():
  return render_template("welcome.html")

@app.route('/<username>/gallery/', defaults={'folder': "all", 'page': 0}, methods=['GET'])
@app.route('/<username>/gallery/<folder>', defaults={'page': 0}, methods=['GET'])
@app.route('/<username>/gallery/<folder>/<int:page>', methods=['GET'])
def view_gallery(username,folder,page):
  author_lookup = db.db.users.find_one({'lowername' : username.lower()})
  if not author_lookup: abort(404)
  else:
    sort  = "d"
    order = "d"
    if "sort" in request.args: sort = request.args["sort"]
    if "order" in request.args: order = request.args["order"]
    if order == "d": useOrder = -1
    else:            useOrder = 1
    if   sort == "t": useSort = "title"
    elif sort == "p": useSort = "fav_amount"
    else:             useSort = "_id"
    if folder=="all":
      art_lookup = db.db.art.find({'author' : author_lookup["username"]}).skip(config.displayed_works_per_page * page).limit( config.displayed_works_per_page ).sort(useSort,useOrder)
    elif folder=="mature":
      art_lookup = db.db.art.find({'author' : author_lookup["username"], 'mature' : True}).skip(config.displayed_works_per_page * page).limit( config.displayed_works_per_page ).sort(useSort,useOrder)
    elif folder=="favorites":
      art_lookup = db.db.art.find({'favorites' : {"$in" : [author_lookup["username"] ] } } ).skip(config.displayed_works_per_page * page).limit( config.displayed_works_per_page ).sort(useSort,useOrder)
    else:
      art_lookup = db.db.art.find({'author' : author_lookup["username"], 'folder' : folder}).skip(config.displayed_works_per_page * page).limit( config.displayed_works_per_page ).sort(useSort,useOrder)
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
  if g.logged_in_user:
    if request.method == 'GET':
        return render_template("submit.html")
    else:
      messages = []
      # Image
      if request.form["artType"] == "image":
        image = request.files['upload']
        if not util.allowed_file(image.filename, config.image_extensions):
          flash(config.file_type_error + "The allowed filetypes are " + util.print_list(config.image_extensions) + ". ")
        elif image.content_length >= config.max_image_size:
          flash(config.file_size_error + "Your image must be at most " + config.max_image_size_text + ". ")
        elif not ("title" in request.form and "description" in request.form) : 
          abort(500)
        elif not request.form["title"]:
          flash("Your title must not be left blank. ")
        else:
          fileType = util.fileType(request.files['upload'].filename)
          key = keys_model.next("art")
          db.db.art.insert({
            "_id"         : key
          , "title"       : request.form["title"]
          , "description" : request.form["description"]
          , "code_desc"    : usercode.parse(request.form["description"])
          , "author"      : g.logged_in_user["username"]
          , "author_ID"    : g.logged_in_user["_id"]
          , "keywords"    : filter (lambda keyword: not keyword in ignored_keywords.commonWords, map(lambda keyword: keyword.lower() , request.form["title"].split() ) )
          , "mature"      : False
          , "folder"      : "complete"
          , "favorites"   : []
          , "fav_amount"   : 0
          , "views"       : 0
          , "date"        : datetime.datetime.today()
          , "filetype"    : fileType
          , "type"        : "image"
          })
          file_location = os.path.join(config.art_dir, str(key) + "." + fileType)
          image.save(file_location)
          storage.push(file_location, file_location)
          autocrop(key)
          return redirect(url_for('crop',art=key))
    # Audio
    # Literature
    # Craft
    # Cullinary
    # Performance
    return redirect(url_for('submit_art'))
  else: abort(401)

@app.route('/art/do/autocrop/<int:art>',methods=['POST'])
def autocrop(art):
  if g.logged_in_user:
    art_lookup = db.db.art.find_one({'_id' : art})
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
  if g.logged_in_user:
    art_lookup = db.db.art.find_one({'_id' : art})
    if not art_lookup: abort(404)
    if not g.logged_in_user["_id"] == art_lookup["author_ID"] and not g.logged_in_user["permissions"]["crop_art"]: abort(401)
    if request.method == 'GET':
      if not art_lookup: abort(404)
      return render_template("crop.html",art=art_lookup)
    else: 
      image_location = os.path.join(config.art_dir, str(art_lookup["_id"]) + "." + art_lookup["filetype"] )
      storage.download(image_location)
      image = Image.open(image_location)
      cropArea = int(request.form["x"]),int(request.form["y"]),int(request.form["x"]) + int(request.form["w"]), int(request.form["y"]) + int(request.form["h"])
      cropped = image.crop(cropArea).resize(config.thumbnail_dimensions,Image.ANTIALIAS)
      cropped_location = os.path.join(config.thumb_dir, str(art_lookup["_id"]) + config.thumbnail_extension)
      cropped.save(cropped_location, config.thumbnail_format, quality=100)
      storage.push(cropped_location, cropped_location)
      return redirect(url_for('view_art',art=art))
  else: abort(401)

@app.route('/<username>/journals', methods=['GET'])
def viewUserJournals(username):
  owner_result = db.db.users.find_one({"lowername" : username.lower() })
  if not owner_result: abort(404)
  journal_result = db.db.journals.find({"author_ID" : owner_result["_id"] }).limit(1).sort("_id",-1)
  if journal_result.count() == 0: abort(404)
  return redirect(url_for('view_journal', journal = journal_result[0]["_id"]) )

@app.route('/journal/view/<int:journal>', methods=['GET'])
def view_journal(journal):
  journal_result = db.db.journals.find_one({"_id" : journal })
  if not journal_result: abort(404)
  db.db.journals.update({"_id": journal}, {"$inc": {"views": 1} })
  allJournals = db.db.journals.find({"author_ID" : journal_result['author_ID'] }).sort("_id",-1)
  return render_template("view_journal.html", journal=journal_result, allJournals=allJournals)

@app.route('/journal/edit/<int:journal>', methods=['GET', 'POST'])
def edit_journal(journal):
  if g.logged_in_user:
    journal_result = db.db.journals.find_one({"_id" : journal })
    if not journal_result: abort(404)
    if g.logged_in_user["_id"] != journal_result['author_ID']:
      abort(401)
    if request.method == 'GET':
      allJournals = db.db.journals.find({"author_ID" : g.logged_in_user['_id'] }).sort("_id",-1)
      return render_template("edit_journal.html", journal=journal_result, allJournals=allJournals)
    elif request.method == 'POST':
        if "journal_title" in request.form and "journal_content" in request.form and "journal_mood" in request.form:
          if request.form["journal_title"].strip() != "":
            db.db.journals.update({"_id": journal}, {"$set": {"title": request.form["journal_title"], "content": request.form["journal_content"], "code_content": usercode.parse(request.form["journal_content"]), "mood": request.form["journal_mood"] }})
            return redirect(url_for('view_journal', journal = journal) )

  else: abort(401)

@app.route('/journal/manage', methods=['GET','POST'])
def manage_journal():
  if g.logged_in_user:
    if request.method == 'GET':
      allJournals = db.db.journals.find({"author_ID" : g.logged_in_user['_id'] }).sort("_id",-1)
      return render_template("manage_journals.html", allJournals = allJournals)
    else:
      if not "journal_title" in request.form or not "journal_content" in request.form or not "journal_mood" in request.form: abort(500)
      if request.form["journal_title"].strip() != "":
        key = keys_model.next("journals")
        db.db.journals.insert({
          "_id"         : key
        , "title"       : request.form["journal_title"]
        , "content"     : request.form["journal_content"]
        , "code_content" : usercode.parse(request.form["journal_content"])
        , "mood"        : request.form["journal_mood"]
        , "author"      : g.logged_in_user["username"]
        , "author_ID"    : g.logged_in_user["_id"]
        , "views"       : 0
        , "date"        : datetime.datetime.today()
        })
        return redirect(url_for('view_journal',journal=key))
      else: return 0
      
  else: abort(401)    

@app.route('/clubs/')
def clubs():
  return render_template("clubs.html")

@app.route('/clubs/edit',  methods=['GET','POST'])
def clubs_edit():
  return render_template("club_edit.html")

@app.route('/clubs/view/<clubName>')
def clubpage(clubName):
  return render_template("clubpage.html")

@app.route('/search/', defaults={'page': 0} )
@app.route('/search/<int:page>', methods=['GET'])
def search(page):
  sort  = "d"
  order = "d"
  keywords = []
  if "sort" in request.args: sort = request.args["sort"]
  if "order" in request.args: order = request.args["order"]
  if "keywords" in request.args: keywords = request.args["keywords"].split()
  if order == "d": useOrder = -1
  else:            useOrder = 1
  if   sort == "t": useSort = "title"
  elif sort == "p": useSort = "fav_amount"
  else:             useSort = "_id"
  if keywords:
    art_lookup = db.db.art.find({"keywords" : {"$in": map(lambda keyword: keyword.lower(), keywords) } } ).skip(config.displayed_works_per_page * page).limit( config.displayed_works_per_page ).sort(useSort,useOrder)
  else:
    art_lookup = db.db.art.find().skip(config.displayed_works_per_page * page).limit( config.displayed_works_per_page ).sort(useSort,useOrder)
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

@app.route('/staff/')
def staff():
  if g.logged_in_user:
    if any(util.dict_to_list(g.logged_in_user["permissions"]) ): 
      users = db.db.users.find()
      art   = db.db.art.find()
      return render_template("staff.html", userCount=users.count(), art_count=art.count() )
    else: abort(401)
  else: abort(401)

@app.route('/art/uploads/<filename>')
def artFile(filename):
  return redirect( storage.get(os.path.join(config.art_dir,filename ) ) )

@app.route('/art/uploads/thumbs/<filename>')
def thumb_file(filename):
  return redirect( storage.get(os.path.join(config.thumb_dir,filename ) ) )

@app.route('/icons/<filename>')
def iconFiles(filename):
  return redirect( storage.get(os.path.join(config.icons_dir,filename ) ) )
  '''
  filename = filename.lower()
  icon = None
  for f in os.listdir(config.icons_dir):
    (name,ext) = f.split(".")
    if name == filename: 
      try: icon = send_from_directory(config.icons_dir,f)
      except: abort(404)
  if icon: return icon
  else: abort(404)
  '''

@app.route('/util/parseUsercode/<text>')
def parseUsercode(text):
  return usercode.parse(text)

@app.route('/admin/generate_beta_pass',methods=['POST'])
def generate_beta_pass():
  if g.logged_in_user:
    if g.logged_in_user["permissions"]["generate_beta_pass"]:
      return db.generate_beta_pass(ownerName=g.logged_in_user["username"])
    elif g.logged_in_user["beta_keys"] > 0:
      db.db.users.update({"_id" : g.logged_in_user["_id"]}, {"$inc" : {"beta_keys" : -1} } )
      return db.generate_beta_pass(ownerName=g.logged_in_user["username"])
    else: abort(401)
  else: abort(401)

@app.route('/api/updateCount',methods=['GET'])
def updateCount():
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

@app.errorhandler(401)
def unauthorized(e):
  return render_template('401.html'), 401

@app.errorhandler(404)
def page_not_found(e):
  rando = random.randint(0,6)
  if   rando == 0: randimg = "scary404.png"
  elif rando == 1: randimg = "vonderdevil404.png"
  elif rando == 2: randimg = "cute404.png"
  elif rando == 3: randimg = "bomb404.png"
  elif rando == 4: randimg = "bile404.png"
  elif rando == 5: randimg = "sexy404.png"
  elif rando == 6: randimg = "browniexxx404.png"
  return render_template('404.html',randimg=randimg), 404

@app.errorhandler(405)
def unauthorized(e):
  return page_not_found(e)

@app.errorhandler(500)
def internalError(e):
  return render_template('500.html'), 500
