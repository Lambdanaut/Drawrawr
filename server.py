from flask import *

import os, shutil, sys, random, logging, datetime

from modules.database import Database
from werkzeug import secure_filename
from PIL import Image

import system.usercode as usercode
import system.config as config
import system.util as util
import system.cryptography

app = Flask(__name__)
app.secret_key = os.urandom(24)

db = Database(config.dbHost,config.dbPort)

if config.logging: logging.basicConfig(filename='logs/DR.log',level=logging.DEBUG)

@app.before_request
def beforeRequest():
  if "username" and "password" in session:
    user = db.db.users.find_one({'lowername' : session["username"].lower(), 'password' : session["password"] }) 
    g.loggedInUser = user
  else: g.loggedInUser = None

@app.context_processor
def injectUser():
  return dict (loggedInUser = g.loggedInUser)

@app.route('/')
def index():
  return render_template("index.html")

@app.route('/<username>')
def userpage(username):
  user = db.db.users.find_one({'lowername' : username.lower() })
  if user != None:
    return render_template("user.html", user=user)
  else:
    abort(404)

@app.route('/users/login', methods=['POST'])
def login():
  if request.method == 'POST':
    userResult = db.db.users.find_one({'lowername' : request.form['username'].lower() })
    if userResult != None:
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
  if not db.userExists(request.form['username']) and len(request.form['username']) > 0 and request.form['password1'] == request.form['password2'] and request.form['tosAgree'] == 'true':
    hashed = system.cryptography.encryptPassword(request.form['password1'], True)
    shutil.copy("static/images/newbyicon.png", "uploads/icons/" + request.form['username'].lower() + ".png")
    db.db.users.insert({
      "username"    : request.form['username'],
      "lowername"   : request.form['username'].lower(),
      "password"    : hashed, 
      "email"       : request.form['email'],
      "ip"          : [request.remote_addr],
      "dob"         : None,
      "dateJoined"  : datetime.datetime.today(),
      "layout"      : {
        # t == top; l == left; r == right; b == bottom; h == hidden
        "profile"  : "t",
        "gallery"  : "l",
        "watches"  : "r",
        "comments" : "b"
      },
      "theme"       : "default",
      "profile"     : "",
      "codeProfile" : "",
      "bground"     : None,
      "icon"        : "png",
      "glued"      : 1,
      # m == Male; f == Female; h == Hide Gender
      "gender"     : "h"
    }) 
    session['username'] = request.form['username']
    session['password'] = hashed
    session.permanent = True
    return "1" #SUCCESS
  else: return "0" #ERROR, User doesn't exist or username is too small

@app.route('/users/glue', methods=['GET','POST'])
def glue():
  if request.method == 'GET':
    if 'username' in session:
      if g.loggedInUser != None:
        return str(g.loggedInUser["glued"])
      else: return "1"
    else: return "1"
  elif request.method == 'POST':
    if g.loggedInUser != None:
      db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"glued": request.form['glued']}})
      return "1"
    else: return "0"

@app.route('/users/settings', methods=['GET','POST'])
def settings():
  if request.method == 'GET':
    if g.loggedInUser != None:
      return render_template("settings.html")
    else: abort(401)
  elif request.method == 'POST':
    if g.loggedInUser != None:
      # User Icon
      icon = request.files['iconUpload']
      if icon and util.allowedFile(icon.filename,config.iconExtensions):
        try: os.remove(config.iconsDir + g.loggedInUser['lowername'] + "." + g.loggedInUser["icon"])
        except: 
          if config.logging: logging.warning("Error: Couldn't remove user \"" + g.loggedInUser['username']+ "\"'s old icon while attempting to upload a new icon. ")
        fileName = g.loggedInUser['lowername'] + "." + util.fileType(icon.filename)
        fileLocation = os.path.join(config.iconsDir, fileName)
        db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"icon": util.fileType(fileName) }})
        icon.save(fileLocation)
        image = Image.open(fileLocation)
        resized = image.resize(config.iconSize)
        try: resized.save(fileLocation)
        except: 
          if config.logging: logging.warning("Error: Couldn't save user \"" + g.loggedInUser['username'] + "\"'s new icon while attempting to upload a new icon. ")
      # Password
      if request.form["changePassCurrent"] and request.form["changePassNew1"] and request.form["changePassNew2"]:
        if system.cryptography.encryptPassword(request.form["changePassCurrent"], True) == g.loggedInUser['password']:
          if request.form["changePassNew1"] == request.form["changePassNew2"]:
            hashed = system.cryptography.encryptPassword(request.form['changePassNew1'], True)
            db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"password": hashed}})
            session['password']=hashed
      # Gender
      if request.form["changeGender"] != g.loggedInUser["gender"]:
        db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"gender": request.form["changeGender"] }})
      # Profile
      if request.form["changeProfile"] != g.loggedInUser["profile"]:
        db.db.users.update({"lowername": g.loggedInUser['lowername']}, {"$set": {"profile": request.form["changeProfile"], "codeProfile": usercode.parse(request.form["changeProfile"]) } })

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

@app.route('/icons/<filename>')
def iconFiles(filename):
    return send_from_directory(config.iconsDir,filename)

@app.route('/art/submit', methods=['GET','POST'])
def submitArt():
  return render_template("submit.html")

@app.route('/art/<filename>')
def artFiles(filename):
  return send_from_directory(config.artDir,filename)

@app.route('/util/parseUsercode/<text>')
def parseUsercode(text):
  return usercode.parse(text)

@app.errorhandler(404)
def page_not_found(e):
  rando = random.randint(0,5)
  print rando
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
