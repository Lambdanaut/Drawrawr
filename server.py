from flask import *

import os, shutil, sys, random, logging

from modules.database import Database
from werkzeug import secure_filename
from PIL import Image
         
import system.config as config
import system.util as util
import system.cryptography

app = Flask(__name__)
app.secret_key = os.urandom(24)

db = Database(config.dbHost,config.dbPort)

if config.logging: logging.basicConfig(filename='logs/DR.log',level=logging.DEBUG)

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
    user = db.db.users.find_one({'lowername' : request.form['username'].lower() })
    if user != None:
      if system.cryptography.encryptPassword(request.form['password'], True) == user['password']: 
        session['username']=user['username']
        session['password']=user['password']
        session.permanent = True
        return "1"
      else: return "0"
    else:
      return "0"
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
  if not db.userExists(request.form['username']) and len(request.form['username']) > 0 and request.form['password1'] == request.form['password2']:
    hashed = system.cryptography.encryptPassword(request.form['password1'], True)
    shutil.copy("static/images/newbyicon.png", "uploads/icons/" + request.form['username'].lower() + ".png")
    db.db.users.insert({
      "username"   : request.form['username'],
      "lowername"  : request.form['username'].lower(),
      "password"   : hashed, 
      "email"      : request.form['email'],
      "layout"     : {
        #t == top; l == left; r == right; b == bottom; h == hidden
        "profile"  : "t",
        "gallery"  : "l",
        "watches"  : "r",
        "comments" : "b"
      },
      "theme"      : "default",
      "bground"    : "",
      "icon"       : request.form['username'].lower() + ".png",
      "glued"      : 1
    }) 
    session['username'] = request.form['username']
    session['password'] = hashed
    session.permanent = True
    return "1" #SUCCESS
  else: return "0" #ERROR, User doesn't exist or username is too small

@app.route('/users/glued', methods=['GET'])
def glued():
  if 'username' in session:
    user = db.db.users.find_one({'username' : session['username']})
    if user != None:
      return str(user["glued"])
    else: return "1"
  else: return "1"

@app.route('/users/glue', methods=['POST'])
def glue():
  if 'username' in session:
    db.db.users.update({"username": session['username']}, {"$set": {"glued": request.form['glued']}})
    return "1"
  else: return "0"

@app.route('/users/settings', methods=['GET','POST'])
def settings():
  if request.method == 'GET':
    if "username" and "password" in session:
      user = db.db.users.find_one({'lowername' : session['username'].lower() })
      if user != None:
        return render_template("settings.html", user=user)
      else: abort(401)
    else: abort(401)
  elif request.method == 'POST':
    if "username" and "password" in session:
      user = db.db.users.find_one({'lowername' : session['username'].lower(), 'password' : session['password'] })
      if user != None:
        # User Icon
        icon = request.files['iconUpload']
        if icon and util.allowedFile(icon.filename,config.iconExtensions):
          try: os.remove(config.iconsDir + user["icon"])
          except: 
            if config.logging: logging.warning("Error: Couldn't remove user \"" + session['username']+ "\"'s old icon while attempting to upload a new icon. ")
          fileName = user['lowername'] + "." + util.fileType(icon.filename)
          fileLocation = os.path.join(config.iconsDir, fileName)
          db.db.users.update({"username": session['username']}, {"$set": {"icon": fileName}})
          icon.save(fileLocation)
          image = Image.open(fileLocation)
          resized = image.resize(config.iconSize)
          try: resized.save(fileLocation)
          except: 
            if config.logging: logging.warning("Error: Couldn't save user \"" + session['username'] + "\"'s new icon while attempting to upload a new icon. ")
          else: return "1"
        else: abort(401)
      else: abort(401)
    else: abort(401)

@app.route('/meta/terms-of-service', methods=['GET'])
def policy():
  f = open("static/legal/tos")
  tos = f.read()
  return render_template("tos.html", tos=tos)

@app.route('/icons/<filename>')
def iconFiles(filename):
    return send_from_directory(config.iconsDir,filename)

@app.route('/art/<filename>')
def artFiles(filename):
    return send_from_directory(config.artDir,filename)

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
