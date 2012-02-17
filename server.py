from flask import *

import os, shutil, sys, random, logging, datetime, base64

from PIL import Image
from system.database import Database
from werkzeug import secure_filename

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
app.config["betaKey"] = config.betaKey
app.config["uploadsDir"] = config.uploadsDir
app.config["iconsDir"] = config.iconsDir
app.config["artDir"] = config.artDir
app.config["thumbDir"] = config.thumbDir
app.config["imageExtensions"] = config.imageExtensions
app.config["iconExtensions"] = config.iconExtensions
app.config["thumbnailExtension"] = config.thumbnailExtension
app.config["captchaSecretKey"] = config.captchaSecretKey
app.config["captchaPublicKey"] = config.captchaPublicKey
app.config['MAX_CONTENT_LENGTH'] = config.maxFileSize
app.config["fileTypeError"] = config.fileTypeError

db = Database(config.dbHost,config.dbPort)

if config.logging: logging.basicConfig(filename='logs/DR.log',level=logging.DEBUG)

def main():
  # First Start Setup
  setup.main()

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
  return dict (loggedInUser = g.loggedInUser, showAds = showAds)

@app.route('/')
def index():
  recentArt = db.db.art.find().limit(30).sort("_id",-1)
  return render_template("index.html",recentArt=recentArt)

@app.route('/<username>')
def userpage(username):
  user = db.getUser(username)
  if user:
    # Increment Page Views
    db.db.users.update({"lowername": user['lowername']}, {"$inc": {"pageViews": 1} })
    # Gallery Module
    if user["layout"]["gallery"] != "h":
      gallery = db.db.art.find({"authorID": user["_id"]}).limit(15).sort("_id",-1)
      if gallery.count() == 0: gallery = None
    else: gallery = None
    return render_template("user.html", user=user, userGallery=gallery, inList=util.inList, showAds=False)
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
  shutil.copy("static/images/newbyicon.png", os.path.join(config.iconsDir, request.form['username'].lower() + ".png"))
  key = db.nextKey("users")
  db.db.users.insert({
    "_id"         : key,
    "username"    : request.form['username'],
    "lowername"   : request.form['username'].lower(),
    "password"    : hashed, 
    "email"       : None, #request.form['email'],
    "ip"          : [request.remote_addr],
    "dob"         : None,
    "betaKey"     : betaKey,
    "dateJoined"  : datetime.datetime.today(),
    "showAds"     : True,
    "layout"      : {
      # t == top; l == left; r == right; b == bottom; h == hidden
      "profile"  : "t",
      "gallery"  : "l",
      "watches"  : "r",
      "comments" : "b"
    },
    "permissions" : {
      "deleteComments"   : False,
      "deleteArt"        : False,
      "banUsers"         : False,
      "makeProps"        : False,
      "vote"             : False,
      "generateBetaPass" : False,
      "cropArt"          : False
    },
    "theme"       : "default",
    "profile"     : "",
    "codeProfile" : "",
    "pageViews"   : 0,
    "watchers"    : [],
    "bground"     : None,
    "icon"        : "png",
    "glued"       : 1,
    # m == Male; f == Female; h == Hide Gender
    "gender"      : "h"
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
        watchedUserResult = db.db.users.find_one({"lowername" : watchedUser.lower()})
        watchers = watchedUserResult["watchers"]
        try: watchers.remove(g.loggedInUser["username"])
        except ValueError: watchers.insert(0, g.loggedInUser["username"])
        db.db.users.update({"lowername" : watchedUser.lower()},{"$set" : {"watchers" : watchers}})
        return "1"
      else:
        if config.logging: logging.warning("User \"" + watchedUser + "\" tried to watch themself. The procedure failed, but it's a bit weird that they should even be able to do this. Keep a watch out for them. ")
        return "0"
    else: abort(401)

@app.route('/users/welcome', methods=['GET'])
def welcome():
  return render_template("welcome.html")

@app.route('/users/settings', methods=['GET','POST'])
def settings():
  if request.method == 'GET':
    if g.loggedInUser:
      return render_template("settings.html")
    else: abort(401)
  elif request.method == 'POST':
    if g.loggedInUser:
      # User Messages
      messages = []
      # User Icon
      icon = request.files['iconUpload']
      if icon:
        if not icon.content_length <= config.maxIconSize:
          flash(app.config["fileSizeError"] + "Your icon must be at most \"" + config.maxIconSizeText + "\". ")
        else:
          if not util.allowedFile(icon.filename,config.iconExtensions):
            flash(app.config["fileTypeError"] + "The allowed extensions are \"" + util.printList(config.iconExtensions) + "\"")
          else: 
            try: os.remove(os.path.join(app.config["iconsDir"], g.loggedInUser['lowername'] + "." + g.loggedInUser["icon"]))
            except: 
              if config.logging: logging.warning("Couldn't remove user \"" + g.loggedInUser['username']+ "\"'s old icon while attempting to upload a new icon. ")
            fileName = g.loggedInUser['lowername'] + "." + util.fileType(icon.filename)
            fileLocation = os.path.join(app.config["iconsDir"], fileName)
            db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"icon": util.fileType(fileName) }})
            icon.save(fileLocation)
            image = Image.open(fileLocation)
            resized = image.resize(config.iconSize, Image.ANTIALIAS)
            try: resized.save(fileLocation, quality=100)
            except: 
              if config.logging: logging.warning("Couldn't save user \"" + g.loggedInUser['username'] + "\"'s new icon while attempting to upload a new icon. ")
            messages.append("User Icon")
      # Password
      if request.form["changePassCurrent"] and request.form["changePassNew1"] and request.form["changePassNew2"]:
        if system.cryptography.encryptPassword(request.form["changePassCurrent"], True) == g.loggedInUser['password']:
          if request.form["changePassNew1"] == request.form["changePassNew2"]:
            hashed = system.cryptography.encryptPassword(request.form['changePassNew1'], True)
            db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"password": hashed}})
            session['password']=hashed
            messages.append("Password")
      # Gender
      if request.form["changeGender"] != g.loggedInUser["gender"]:
        db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"gender": request.form["changeGender"] }})
        messages.append("Gender")
      # Profile
      if request.form["changeProfile"] != g.loggedInUser["profile"]:
        db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"profile": request.form["changeProfile"], "codeProfile": usercode.parse(request.form["changeProfile"]) } })
        messages.append("Profile")
      # Color Theme
      if request.form["changeColorTheme"] != g.loggedInUser["theme"]:
        db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"theme": request.form["changeColorTheme"]} })
        messages.append("Color Theme")
      return render_template("settingsSuccess.html",messages=messages, len=len)
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

@app.route('/art/<int:art>', methods=['GET'])
def viewArt(art):
  try: 
    artLookup = db.db.art.find_one({'_id' : art})
  except ValueError: abort(404)
  if not artLookup: abort(404)
  else:
    authorLookup = db.db.users.find_one({'_id' : artLookup["authorID"]})
    return render_template("art.html", art=artLookup, author=authorLookup)

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
      if not image.content_length <= config.maxImageSize:
        flash(app.config["fileSizeError"] + "Your image must be at most \"" + config.maxImageSizeText + "\". ")
      else:
        if not util.allowedFile(image.filename,config.imageExtensions):
          messages.append(app.config["fileTypeError"])
        else:
          fileType = util.fileType(request.files['upload'].filename)
          key = db.nextKey("art")
          db.db.art.insert({
            "_id"         : key,
            "title"       : request.form["title"],
            "description" : request.form["description"],
            "author"      : g.loggedInUser["username"],
            "authorID"    : g.loggedInUser["_id"],
            "filetype"    : fileType,
            "type"        : "image"
          })
          fileLocation = os.path.join(config.artDir, str(key) + "." + fileType)
          try: image.save(fileLocation)
          except: 
            if config.logging: logging.warning("Couldn't save user \"" + g.loggedInUser['username'] + "\"'s art upload to the server at location \"" + fileLocation + "\". The art _id key was #" + str(key) + ". " )
          autocrop(key)
          return redirect(url_for('crop',art=key))

@app.route('/art/do/autocrop/<int:art>',methods=['POST'])
def autocrop(art):
  if g.loggedInUser:
    artLookup = db.db.art.find_one({'_id' : art})
    if not artLookup: abort(404)
    if not g.loggedInUser["_id"] == artLookup["authorID"] and not g.loggedInUser["permissions"]["cropArt"]: abort(401)
    imageLocation = os.path.join(config.artDir, str(artLookup["_id"]) + "." + artLookup["filetype"] )
    image = Image.open(imageLocation)
    cropped = image.resize(config.thumbnailDimensions,Image.ANTIALIAS)
    croppedLocation = os.path.join(config.thumbDir, str(artLookup["_id"]) + config.thumbnailExtension)
    cropped.save( croppedLocation, config.thumbnailFormat, quality=100)
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
      image = Image.open(imageLocation)
      cropArea = int(request.form["x"]),int(request.form["y"]),int(request.form["x"]) + int(request.form["w"]), int(request.form["y"]) + int(request.form["h"])
      cropped = image.crop(cropArea).resize(config.thumbnailDimensions,Image.ANTIALIAS)
      croppedLocation = os.path.join(config.thumbDir, str(artLookup["_id"]) + config.thumbnailExtension)
      cropped.save( croppedLocation, config.thumbnailFormat, quality=100)
      return redirect(url_for('viewArt',art=art))
  else: abort(401)

@app.route('/art/uploads/<filename>')
def artFile(filename):
  return send_from_directory(config.artDir,filename)

@app.route('/art/uploads/thumbs/<filename>')
def thumbFile(filename):
  return send_from_directory(config.thumbDir,filename)

@app.route('/icons/<filename>')
def iconFiles(filename):
  filename = filename.lower()
  icon = None
  for f in os.listdir(config.iconsDir):
    (name,ext) = f.split(".")
    if name == filename: 
      try: icon = send_from_directory(config.iconsDir,f)
      except: abort(404)
  if icon: return icon
  else: abort(404)

@app.route('/util/parseUsercode/<text>')
def parseUsercode(text):
  return usercode.parse(text)

@app.route('/admin/generateBetaPass',methods=['GET'])
def generateBetaPass():
  if g.loggedInUser:
    if g.loggedInUser["permissions"]["generateBetaPass"]:
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

@app.errorhandler(404)
def page_not_found(e):
  rando = random.randint(0,5)
  if   rando == 0:
    randimg = "scary404.png"
  elif rando == 1:
    randimg = "vonderdevil404.png"
  elif rando == 2:
    randimg = "cute404.png"
  elif rando == 3:
    randimg = "bomb404.png"
  elif rando == 4:
    randimg = "bile404.png"
  elif rando == 5:
    randimg = "sexy404.png"
  return render_template('404.html',randimg=randimg), 404

@app.errorhandler(401)
def unauthorized(e):
  return render_template('401.html'), 401
