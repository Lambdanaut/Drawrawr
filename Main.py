#!/usr/bin/python2
#  ____                _____                  ___   ___
# |    \ ___ ___ _ _ _| __  |___ _ _ _ ___   |_  | |   |
# |  |  |  _| .'| | | |    -| .'| | | |  _|  |  _|_| | | 
# |____/|_| |__,|_____|__|__|__,|_____|_|    |___|_|___|
# ------------ A social website for artists ------------

__version__ = '2.0'
__author__  = 'DrawRawr'

from flask import *
import os, sys

from optparse import OptionParser

from modules.database import Database

import system.cryptography, system.config

parser = OptionParser()
parser.add_option("-q", "--quiet", action="store_false", dest="verbose", 
                  default=True, help="Silence all output from DrawRawr")

## Loading engines
engines = {}
enginesDirectory = os.listdir(os.path.join(sys.path[0], 'system', 'engines'))

for engine in enginesDirectory:
  engineParts = os.path.splitext(engine)
  
  if engineParts[1] is '.py' and engineParts[0] is not '__init__':
    engines[engineParts[0]] = __import__("system.engines." + engineParts[0])

app = Flask(__name__)
app.secret_key = os.urandom(24)

db = Database(system.config.dbHost,system.config.dbPort)

@app.route('/')
def index():
  return render_template("index.html", session=session)

@app.route('/<username>')
def userpage(username):
    return username

@app.route('/users/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    user = db.db.users.find_one({"username": request.form['username']})
    if user != None:
      if system.cryptography.encryptPassword(request.form['password'], True) == user['password']: 
        session['username']=user['username']
        session['password']=user['password']
        return "1"
      else: return "0"
    else:
      return "0"
  else: return "None"

@app.route('/users/signup', methods=['GET', 'POST'])
def signup():
  if not db.userExists(request.form['username']) and len(request.form['username']) > 0 and request.form['password1'] == request.form['password2']:
    hashed = system.cryptography.encryptPassword(request.form['password1'], True)
    print db.db.users.insert({"username" : request.form['username'],"password" : hashed, "email" : request.form['email'], "glued" : 1}) 
    session['username'] = request.form['username']
    session['password'] = hashed
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

@app.route('/meta/terms-of-service', methods=['GET'])
def policy():
  return render_template("tos.html", session=session)

if __name__ == "__main__": app.run(host='0.0.0.0',debug=True)
else: print("DrawRawr isn't a module, silly.")
