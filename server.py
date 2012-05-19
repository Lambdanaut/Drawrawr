from flask import *
import werkzeug

import os, math, mimetypes, sys, random, logging, datetime, base64

from PIL import Image

from system.database import Database
from system.S3 import S3

import system.captcha as captcha
import system.config as config
import system.cryptography
import system.setup as setup
import system.usercode as usercode
import system.util as util

# Create Application
app = Flask(__name__)
app.jinja_env.trim_blocks = True

# Secret Key
if config.randomSecretKey: app.secret_key = os.urandom(24)
else                     : app.secret_key = "0"

# Add Config
app.config['MAX_CONTENT_LENGTH'] = config.maxFileSize

if config.production: db = Database(config.dbHost,config.dbPort,config.dbUsername,config.dbPassword)
else: db = Database(config.dbHost,config.dbPort)

storage = S3()

if config.logging: logging.basicConfig(filename='logs/DR.log',level=logging.DEBUG)

def main():
  # First Start Setup
  setup.main(db)

  # Run Server
  app.run(host=config.host,port=config.port,debug=config.debug)

@app.before_request
def beforeRequest():
  if "username" and "password" in session:
    user = db.db.users.find_one({'lowername' : session["username"].lower(), 'password' : session["password"] }) 
    g.loggedInUser = user
  else: g.loggedInUser = None

@app.context_processor
def injectUser():
  if g.loggedInUser: showAds = g.loggedInUser["showAds"]
  else:              showAds = True
  return dict (loggedInUser = g.loggedInUser, showAds = showAds, util = util, config=config, any = any, str = str)

@app.route('/')
def index():
  recentArt = db.db.art.find().limit(30).sort("_id",-1)
  popularArt = db.db.art.find( {"favAmount" : {"$gt" : 0 } } ).sort("favorites",-1).limit(12)
  return render_template("index.html",recentArt=recentArt,popularArt=popularArt)

@app.route('/<username>')
def userpage(username):
  user = db.getUser(username)
  if user:
    # Increment Page Views
    db.db.users.update({"lowername": user['lowername']}, {"$inc": {"pageViews": 1} })
    # Gallery Module
    gallery = None
    if user["layout"]["gallery"][0] != "h":
      gallery = db.db.art.find({"authorID": user["_id"]}).limit(15).sort("_id",-1)
      if gallery.count() == 0: gallery = None
    else: gallery = None
    # Nearby Users Module
    # It's rather naive in that the processing is done by the server and not the database. It may be a problem in the future. 
    closeUsers = None
    if user["layout"]["nearby"][0] != "h" and user["latitude"] and user["longitude"]:
      allUsers = db.db.users.find({"_id": {"$ne" : user["_id"]} , "latitude" : {"$ne" : None}, "longitude" : {"$ne" : None} })
      closeUsers = []
      for aUser in allUsers:
        if math.sqrt( (user["latitude"] - aUser["latitude"])**2 + (user["longitude"] - aUser["longitude"])**2 ) < config.maxNearbyUserDistance: closeUsers.append(aUser["username"])
    # Journal Module
    journal = None
    if user["layout"]["journal"][0] != "h":
      journalResult = db.db.journals.find({"authorID" : user["_id"] }).sort("_id",-1).limit(1)
      if journalResult.count() == 0: journal = None
      else: journal = journalResult[0]
    # Comment Module
    comments = None
    if user["layout"]["comments"][0] != "h":
      comments = db.db.comments.find({"home": user["_id"], "homeType" : "u"}).sort("_id",1).limit(config.maxCommentsOnUserpages)
      if comments.count() == 0: comments = None

    return render_template("user.html", user=user, userGallery=gallery, nearbyUsers=closeUsers, journalResult=journal, commentResult=comments, showAds=False)
  else: abort(404)

@app.route('/users/login', methods=['POST'])
def login():
  if request.method == 'POST':
    userResult = db.db.users.find_one({'lowername' : request.form['username'].lower() })
    if userResult:
      if system.cryptography.encryptPassword(request.form['password'], True) == userResult['password']: 
        session['username']=userResult['username']
        session['password']=userResult['password']
        session.permanent = True
        # Add the user's IP to the front of the list of his IPs
        ip = userResult["ip"]
        try: ip.remove(request.remote_addr)
        except ValueError: pass
        ip.insert(0,request.remote_addr)
        db.db.users.update({"lowername": userResult['lowername']}, {"$set": {"ip": ip} })
        return "1"
      else: return "0"
    else: return "0"
  else: return "None"

@app.route('/users/logout', methods=['POST'])
def logout():
  if "username" and "password" in session:
    session.pop('username')
    session.pop('password')
    return "1"
  else: return "0"

@app.route('/users/signup', methods=['GET', 'POST'])
def signup(): 
  if db.userExists(request.form['username']) or len(request.form['username']) == 0 or request.form['password1'] != request.form['password2'] or request.form['tosAgree'] != 'true':
    return "0" #ERROR, User doesn't exist or username is too small
  if captcha.check(request.form['recaptcha_challenge_field'], request.form['recaptcha_response_field'],config.captchaSecretKey,request.remote_addr):
    return "2" #ERROR, Captcha Fail
  if config.betaKey:
    betaKey = db.checkBetaPass(request.form["betaCode"])
    if not betaKey:
      return "3" #ERROR, Beta Code Fail
  else: betaKey = None
  hashed = system.cryptography.encryptPassword(request.form['password1'], True)
  storage.push("static/images/newbyicon.png", os.path.join(config.iconsDir, request.form['username'].lower() ), mimetype="image/png")
  key = db.nextKey("users")
  db.db.users.insert({
    "_id"         : key
  , "username"    : request.form['username']
  , "lowername"   : request.form['username'].lower()
  , "password"    : hashed
  , "email"       : None #request.form['email']
  , "ip"          : [request.remote_addr]
  , "dob"         : None
  , "betaKey"     : betaKey
  , "betaKeys"    : config.startingBetaKeys
  , "dateJoined"  : datetime.datetime.today()
  , "showAds"     : True
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
      "deleteComments"   : True
    , "editArt"          : True
    , "deleteArt"        : True
    , "banUsers"         : True
    , "makeProps"        : True
    , "vote"             : True
    , "generateBetaPass" : True
    , "cropArt"          : True
    }
  , "latitude"    : None
  , "longitude"   : None
  , "theme"       : "default"
  , "profile"     : ""
  , "codeProfile" : ""
  , "pageViews"   : 0
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
      if g.loggedInUser:
        return str(g.loggedInUser["glued"])
      else: return "1"
    else: return "1"
  elif request.method == 'POST':
    if g.loggedInUser:
      db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"glued": request.form['glued']}})
      return "1"
    else: return "0"

@app.route('/users/watch', methods=['GET','POST'])
def watch():
  if request.method == 'GET':
    # This needs to return a list of watchers or something
    return "0"
  elif request.method == 'POST':
    if g.loggedInUser:
      watchedUser = request.form["watchedUser"]
      if g.loggedInUser["lowername"] != watchedUser.lower():
        userResult = db.db.users.find_one({"lowername" : watchedUser.lower()})
        if util.inList(g.loggedInUser["username"], userResult["watchers"]):
          db.db.users.update({"lowername" : watchedUser.lower()},{"$pull" : {"watchers" : g.loggedInUser["username"] } })
        else:
          watchers = userResult["watchers"]
          watchers.insert(0, g.loggedInUser["username"])
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
  if request.method == 'GET':
    if g.loggedInUser:
      if config.betaKey: betaKeys = db.db.betaPass.find({"owner" : g.loggedInUser["username"] })
      else: betaKeys = None
      return render_template("settings.html", betaKeys = betaKeys)
    else: abort(401)
  elif request.method == 'POST':
    if g.loggedInUser:
      # User Messages
      messages = []
      # User Icon
      icon = request.files['iconUpload']
      if icon:
        if not icon.content_length <= config.maxIconSize:
          flash(config.fileSizeError + "Your icon must be at most " + config.maxIconSizeText + ". ")
        else:
          if not util.allowedFile(icon.filename,config.iconExtensions):
            flash(config.fileTypeError + "The allowed extensions are " + util.printList(config.iconExtensions) + ". ")
          else: 
            try: os.remove(os.path.join(config.iconsDir, g.loggedInUser['lowername'] + "." + g.loggedInUser["icon"]))
            except: 
              if config.logging: logging.warning("Couldn't remove user \"" + g.loggedInUser['username']+ "\"'s old icon while attempting to upload a new icon. ")
            fileName = g.loggedInUser['lowername']
            fileType = util.fileType(icon.filename)
            if fileType.lower() == "jpg": fileType = "jpeg" # Change filetype for PIL
            (mimetype,i) = mimetypes.guess_type(icon.filename)
            fileLocation = os.path.join(config.iconsDir, fileName)
            db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"icon": fileType } } )
            icon.save(fileLocation)
            image = Image.open(fileLocation)
            resized = image.resize(config.iconSize, Image.ANTIALIAS)
            resized.save(fileLocation, fileType, quality=100)
            storage.push(fileLocation, fileLocation, mimetype = mimetype )
            messages.append("User Icon")
      # Password
      if request.form["changePassCurrent"] and request.form["changePassNew1"] and request.form["changePassNew2"]:
        if system.cryptography.encryptPassword(request.form["changePassCurrent"], True) != g.loggedInUser['password']:
          flash("The new password you gave didn't match the one in the database! ):")
        elif request.form["changePassNew1"] != request.form["changePassNew2"]:
          flash("The new passwords you gave don't match! Try retyping them carefully. ")
        else:
          hashed = system.cryptography.encryptPassword(request.form['changePassNew1'], True)
          db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"password": hashed}})
          session['password']=hashed
          messages.append("Password")
      # Gender
      if request.form["changeGender"] != g.loggedInUser["gender"]:
        db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"gender": request.form["changeGender"] }})
        messages.append("Gender")
      # Location
      if request.form["changeLatitude"] != str(g.loggedInUser["latitude"]) or request.form["changeLongitude"] != str(g.loggedInUser["longitude"]):
        try:
          latFloat = float(request.form["changeLatitude"])
          lonFloat = float(request.form["changeLongitude"])
          db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"latitude": latFloat, "longitude": lonFloat } } )
          messages.append("Location")
        except ValueError:
          flash("The locations you gave were invalid latitude and longitude coordinates! ): ")
      # Profile
      if request.form["changeProfile"] != g.loggedInUser["profile"]:
        db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"profile": request.form["changeProfile"], "codeProfile": usercode.parse(request.form["changeProfile"]) } })
        messages.append("Profile")
      # Color Theme
      if request.form["changeColorTheme"] != g.loggedInUser["theme"]:
        db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"theme": request.form["changeColorTheme"]} })
        messages.append("Color Theme")
      # Layout
      l1 = util.urlDecode(request.form["changeLayout"])
      l2 = util.urlDecode(request.form["changeLayoutOrder"])
      for key in l2: l2[key] = int(l2[key]) # Converts orderings to integers
      layout = util.concDictValues(l1,l2)
      if not util.compareDicts(layout, g.loggedInUser["layout"]):
        if util.compareDictKeys(layout, g.loggedInUser["layout"]):
          layoutToPush = {}
          for key in layout:
            layoutToPush["layout." + key] = layout[key]
          db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": layoutToPush })
          messages.append("Layout")
      return render_template("settingsSuccess.html",messages=messages,len=len)
    else: abort(401)

@app.route('/<username>/comment/<int:commentID>', methods=['GET'])
@app.route('/art/<int:art>/comment/<int:commentID>', methods=['GET'])
@app.route('/journal/view/<int:journal>/comment/<int:commentID>', methods=['GET'])
@app.route('/<username>/comment', methods=['POST'])
@app.route('/art/<int:art>/comment', methods=['POST'])
@app.route('/journal/view/<int:journal>/comment', methods=['POST'])
def comment(username=None,art=None,journal=None,commentID=None):
  if request.method == 'GET':
    commentResult = db.db.comments.find_one({"_id" : commentID})
    if not commentResult: abort(404)
    return render_template("comment.html", comment=commentResult)
  else:
    if g.loggedInUser:
      # Filter out broken or incomplete comments
      if "parent" not in request.form or "commentMap" not in request.form or "content" not in request.form: abort(500)
      if len(request.form["content"]) < config.minimumCommentLengthInCharacters: return "0"
      parent = request.form["parent"]
      commentMap = request.form["commentMap"]
      # Comment Reply
      if parent != "" and commentMap != "": 
        try: 
          parent     = int(request.form["parent"])
          commentMap = util.parseCommentMap(request.form["commentMap"])
        except ValueError: abort(500)
        db.db.comments.update( { "_id" : parent }, {
          "$push" : { commentMap : {
            "authorID"    : g.loggedInUser["_id"]
          , "author"      : g.loggedInUser["username"]
          , "content"     : request.form["content"]
          , "codeContent" : usercode.parse(request.form["content"])
          , "r"           : []
          , "date"        : datetime.datetime.today()
          } }
        })
        return "1"
      # Top Level Comment
      else:
        if username:
          location = "u"
          userLookup = db.db.users.find_one({"lowername" : username.lower()})
          if userLookup: home = userLookup["_id"]
          else: abort(500)
        elif art:
          location = "a"
          home = art
        elif journal:
          location = "j"
          home = journal
        else         : abort(500)
        key = db.nextKey("comments")
        db.db.comments.insert({
          "_id"         : key
        , "authorID"    : g.loggedInUser["_id"]
        , "author"      : g.loggedInUser["username"]
        , "content"     : request.form["content"]
        , "codeContent" : usercode.parse(request.form["content"])
        , "r"           : []
        , "home"        : home
        , "homeType"    : location
        , "date"        : datetime.datetime.today()
        })
        return "1"

    else: abort(401)

@app.route('/meta/terms-of-service', methods=['GET'])
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
def viewArt(art):
  try: 
    artLookup = db.db.art.find_one({'_id' : art})
  except ValueError: abort(404)
  if not artLookup: abort(404)
  if request.method == 'GET':
    authorLookup = db.db.users.find_one({'_id' : artLookup["authorID"]})
    # Increment Art Views
    incViews = True
    if g.loggedInUser: incViews = not g.loggedInUser["_id"] == authorLookup["_id"]
    if config.pageViewsRequireAlternateIP: not util.inList(request.remote_addr,authorLookup["ip"])
    if incViews: db.db.art.update({"_id": art}, {"$inc": {"views": 1} })
    return render_template("art.html", art=artLookup, author=authorLookup )
  elif request.method == 'DELETE':
    if g.loggedInUser:
      if artLookup["authorID"] == g.loggedInUser["_id"] or g.loggedInUser["permissions"]["deleteArt"]:
        # Delete File
        storage.delete(os.path.join(config.artDir , str(artLookup['_id']) + "." + artLookup['filetype'] ) )
        # Delete From Database
        db.db.art.remove({'_id' : artLookup['_id']})
        return "1"
      else: abort(401)

@app.route('/art/<int:art>/feature', methods=['POST'])
def featureArt(art):
  try: 
    artLookup = db.db.art.find_one({'_id' : art})
  except ValueError: abort(404)
  if not artLookup: abort(404)
  if not "featuredText" in request.form: abort(500)
  db.db.feature.insert({
    "author"  : g.loggedInUser["username"]
  , "artID"   : art
  , "content" : request.form["featuredText"]
  , "date"    : datetime.datetime.today()
  })
  featureCount = db.db.feature.find({"artID" : art}).count()
  flash("Your feature suggestion was submitted successfully. If " + str(config.featuresBeforeConsideration - featureCount) + " more users request this artwork to be featured, then staff will be notified. " )
  return redirect(url_for("viewArt", art=art))

@app.route('/art/<int:art>/favorite', methods=['POST','GET'])
def favorite(art):
  if request.method == 'POST':
    if g.loggedInUser:
      fav = db.db.art.find_one({"_id" : art})
      if g.loggedInUser != fav["author"]:
        if util.inList(g.loggedInUser["username"], fav["favorites"]):
          db.db.art.update({"_id" : art}, {"$pull" : {"favorites" : g.loggedInUser["username"] }  , "$inc" : {"favAmount": -1 } } )
        else:
          db.db.art.update({"_id" : art}, {"$addToSet" : {"favorites" : g.loggedInUser["username"] } , "$inc" : {"favAmount": 1 } } )
        return "1"
      else: return "0"
    else: abort(401)
  else:
    # The GET method returns 1 if the user has fav'd this art, and a 0 if they're not. 
    if g.loggedInUser:
      fav = db.db.art.find_one({"_id" : art})
      if util.inList(g.loggedInUser["username"], fav["favorites"]): return "1"
      else:                                                         return "0"

@app.route('/users/welcome', methods=['GET'])
def welcome():
  return render_template("welcome.html")

@app.route('/<username>/gallery/', defaults={'folder': "all", 'page': 0}, methods=['GET'])
@app.route('/<username>/gallery/<folder>', defaults={'page': 0}, methods=['GET'])
@app.route('/<username>/gallery/<folder>/<int:page>', methods=['GET'])
def viewGallery(username,folder,page):
  authorLookup = db.db.users.find_one({'lowername' : username.lower()})
  if not authorLookup: abort(404)
  else:
    sort  = "d"
    order = "d"
    if "sort" in request.args: sort = request.args["sort"]
    if "order" in request.args: order = request.args["order"]
    if order == "d": useOrder = -1
    else:            useOrder = 1
    if   sort == "t": useSort = "title"
    elif sort == "p": useSort = "favAmount"
    else:             useSort = "_id"
    if folder=="all":
      artLookup = db.db.art.find({'author' : authorLookup["username"]}).skip(config.displayedWorksPerPage * page).limit( config.displayedWorksPerPage ).sort(useSort,useOrder)
    elif folder=="mature":
      artLookup = db.db.art.find({'author' : authorLookup["username"], 'mature' : True}).skip(config.displayedWorksPerPage * page).limit( config.displayedWorksPerPage ).sort(useSort,useOrder)
    elif folder=="favorites":
      artLookup = db.db.art.find({'favorites' : {"$in" : [authorLookup["username"] ] } } ).skip(config.displayedWorksPerPage * page).limit( config.displayedWorksPerPage ).sort(useSort,useOrder)
    else:
      artLookup = db.db.art.find({'author' : authorLookup["username"], 'folder' : folder}).skip(config.displayedWorksPerPage * page).limit( config.displayedWorksPerPage ).sort(useSort,useOrder)
    # Create page index
    artCount = artLookup.count()
    if not artCount: artLookup = None
    if artCount % config.displayedWorksPerPage: extraPage = 1
    else:                                       extraPage = 0
    pages = range(0,(artCount / config.displayedWorksPerPage) + extraPage)
    pageCount = len(pages)
    pagesLeft = len(pages[page:])
    if pagesLeft > config.pageIndexes:
      pages = pages[page: page + config.pageIndexes]
      more = True
    else:
      pages = pages[page: page + pagesLeft]
      more = False
    return render_template("gallery.html", art=artLookup, author=authorLookup, folder=folder, sort=sort, order=order, currentPage=page, pages=pages, last=pageCount - 1)

@app.route('/art/do/submit', methods=['GET','POST'])
def submitArt():
  if request.method == 'GET':
    if g.loggedInUser:
      return render_template("submit.html")
    else: abort(401)
  else:
    if not g.loggedInUser:
      abort(401)
    messages = []
    # Image
    if request.form["artType"] == "image":
      image = request.files['upload']
      if not util.allowedFile(image.filename, config.imageExtensions):
        flash(app.config.fileTypeError + "The allowed filetypes are " + util.printList(config.imageExtensions) + ". ")
      elif image.content_length >= config.maxImageSize:
        flash(app.config.fileSizeError + "Your image must be at most " + config.maxImageSizeText + ". ")
      else:
        fileType = util.fileType(request.files['upload'].filename)
        key = db.nextKey("art")
        db.db.art.insert({
          "_id"         : key
        , "title"       : request.form["title"]
        , "description" : request.form["description"]
        , "codeDesc"    : usercode.parse(request.form["description"])
        , "author"      : g.loggedInUser["username"]
        , "authorID"    : g.loggedInUser["_id"]
        , "mature"      : False
        , "folder"      : "complete"
        , "favorites"   : []
        , "favAmount"   : 0
        , "views"       : 0
        , "date"        : datetime.datetime.today()
        , "filetype"    : fileType
        , "type"        : "image"
        })
        fileLocation = os.path.join(config.artDir, str(key) + "." + fileType)
        image.save(fileLocation)
        storage.push(fileLocation, fileLocation)
        autocrop(key)
        return redirect(url_for('crop',art=key))
  # Audio
  # Literature
  # Craft
  # Cullinary
  # Performance
  return redirect(url_for('submitArt'))

@app.route('/art/do/autocrop/<int:art>',methods=['POST'])
def autocrop(art):
  if g.loggedInUser:
    artLookup = db.db.art.find_one({'_id' : art})
    if not artLookup: abort(404)
    if not g.loggedInUser["_id"] == artLookup["authorID"] and not g.loggedInUser["permissions"]["cropArt"]: abort(401)
    imageLocation = os.path.join(config.artDir, str(artLookup["_id"]) + "." + artLookup["filetype"] )
    storage.download(imageLocation)
    image = Image.open(imageLocation)
    cropped = image.resize(config.thumbnailDimensions,Image.ANTIALIAS)
    croppedLocation = os.path.join(config.thumbDir, str(artLookup["_id"]) + config.thumbnailExtension)
    cropped.save( croppedLocation, config.thumbnailFormat, quality=100)
    storage.push(croppedLocation, croppedLocation)
    return "1"
  else: abort(401)

@app.route('/art/do/crop/<int:art>', methods=['GET','POST'])
def crop(art):
  if g.loggedInUser:
    artLookup = db.db.art.find_one({'_id' : art})
    if not artLookup: abort(404)
    if not g.loggedInUser["_id"] == artLookup["authorID"] and not g.loggedInUser["permissions"]["cropArt"]: abort(401)
    if request.method == 'GET':
      if not artLookup: abort(404)
      return render_template("crop.html",art=artLookup)
    else: 
      imageLocation = os.path.join(config.artDir, str(artLookup["_id"]) + "." + artLookup["filetype"] )
      storage.download(imageLocation)
      image = Image.open(imageLocation)
      cropArea = int(request.form["x"]),int(request.form["y"]),int(request.form["x"]) + int(request.form["w"]), int(request.form["y"]) + int(request.form["h"])
      cropped = image.crop(cropArea).resize(config.thumbnailDimensions,Image.ANTIALIAS)
      croppedLocation = os.path.join(config.thumbDir, str(artLookup["_id"]) + config.thumbnailExtension)
      cropped.save( croppedLocation, config.thumbnailFormat, quality=100)
      storage.push(croppedLocation, croppedLocation)
      return redirect(url_for('viewArt',art=art))
  else: abort(401)

@app.route('/<username>/journals', methods=['GET'])
def viewUserJournals(username):
  ownerResult = db.db.users.find_one({"lowername" : username.lower() })
  if not ownerResult: abort(404)
  journalResult = db.db.journals.find({"authorID" : ownerResult["_id"] }).limit(1).sort("_id",-1)
  if journalResult.count() == 0: abort(404)
  return redirect(url_for('viewJournal', journal = journalResult[0]["_id"]) )

@app.route('/journal/view/<int:journal>', methods=['GET'])
def viewJournal(journal):
  journalResult = db.db.journals.find_one({"_id" : journal })
  if not journalResult: abort(404)
  db.db.journals.update({"_id": journal}, {"$inc": {"views": 1} })
  return render_template("viewJournal.html", journal=journalResult)

@app.route('/journal/manage', methods=['GET','POST'])
def manageJournal():
  if g.loggedInUser:
    if request.method == 'GET':
      return render_template("manageJournals.html")
    else:
      if not "journalTitle" in request.form or not "journalContent" in request.form: abort(500)
      key = db.nextKey("journals")
      db.db.journals.insert({
        "_id"         : key
      , "title"       : request.form["journalTitle"]
      , "content"     : request.form["journalContent"]
      , "codeContent" : usercode.parse(request.form["journalContent"])
      , "mood"        : request.form["journalMood"]
      , "author"      : g.loggedInUser["username"]
      , "authorID"    : g.loggedInUser["_id"]
      , "views"       : 0
      , "date"        : datetime.datetime.today()
      })
      return redirect(url_for('viewJournal',journal=key))
      
  else: abort(401)    

@app.route('/clubs/')
def clubs():
  return render_template("clubs.html")

@app.route('/clubs/edit',  methods=['GET','POST'])
def clubsEdit():
  return render_template("clubedit.html")

@app.route('/clubs/view/<clubName>')
def clubsPage(clubName):
  return render_template("clubpage.html")

@app.route('/search/', defaults={'page': 0} )
@app.route('/search/<int:page>', methods=['GET'])
def search(page):
  sort  = "d"
  order = "d"
  if "sort" in request.args: sort = request.args["sort"]
  if "order" in request.args: order = request.args["order"]
  if order == "d": useOrder = -1
  else:            useOrder = 1
  if   sort == "t": useSort = "title"
  elif sort == "p": useSort = "favAmount"
  else:             useSort = "_id"
  artLookup = db.db.art.find().skip(config.displayedWorksPerPage * page).limit( config.displayedWorksPerPage ).sort(useSort,useOrder)
  # Create page index
  artCount = artLookup.count()
  if not artCount: artLookup = None
  if artCount % config.displayedWorksPerPage: extraPage = 1
  else:                                       extraPage = 0
  pages = range(0,(artCount / config.displayedWorksPerPage) + extraPage)
  pageCount = len(pages)
  pagesLeft = len(pages[page:])
  if pagesLeft > config.pageIndexes:
    pages = pages[page: page + config.pageIndexes]
    more = True
  else:
    pages = pages[page: page + pagesLeft]
    more = False
  return render_template("search.html", art=artLookup, sort=sort, order=order, currentPage=page, pages=pages, last=pageCount - 1)

@app.route('/staff/')
def staff():
  if g.loggedInUser:
    if any(util.dictToList(g.loggedInUser["permissions"]) ): 
      users = db.db.users.find()
      art   = db.db.art.find()
      return render_template("staff.html", userCount=users.count(), artCount=art.count() )
    else: abort(401)
  else: abort(401)

@app.route('/art/uploads/<filename>')
def artFile(filename):
  return redirect( storage.get(os.path.join(config.artDir,filename ) ) )

@app.route('/art/uploads/thumbs/<filename>')
def thumbFile(filename):
  return redirect( storage.get(os.path.join(config.thumbDir,filename ) ) )

@app.route('/icons/<filename>')
def iconFiles(filename):
  return redirect( storage.get(os.path.join(config.iconsDir,filename ) ) )
  '''
  filename = filename.lower()
  icon = None
  for f in os.listdir(config.iconsDir):
    (name,ext) = f.split(".")
    if name == filename: 
      try: icon = send_from_directory(config.iconsDir,f)
      except: abort(404)
  if icon: return icon
  else: abort(404)
  '''

@app.route('/util/parseUsercode/<text>')
def parseUsercode(text):
  return usercode.parse(text)

@app.route('/admin/generateBetaPass',methods=['POST'])
def generateBetaPass():
  if g.loggedInUser:
    if g.loggedInUser["permissions"]["generateBetaPass"]:
      return db.generateBetaPass(ownerName=g.loggedInUser["username"])
    elif g.loggedInUser["betaKeys"] > 0:
      db.db.users.update({"_id" : g.loggedInUser["_id"]}, {"$inc" : {"betaKeys" : -1} } )
      return db.generateBetaPass(ownerName=g.loggedInUser["username"])
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
    if db.userPassCheck(username,password):
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
