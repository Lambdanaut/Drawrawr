#!/usr/bin/python2
#  ____                _____                  ___   ___
# |    \ ___ ___ _ _ _| __  |___ _ _ _ ___   |_  | |   |
# |  |  |  _| .'| | | |    -| .'| | | |  _|  |  _|_| | | 
# |____/|_| |__,|_____|__|__|__,|_____|_|    |___|_|___|
# ------------ A social website for artists ------------

__version__ = '2.0'
__author__  = 'DrawRawr'

from flask import *
from optparse import OptionParser
from system.database import *

import system.cryptography, system.config

import os, sys

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

#render = web.template.render('templates', base='layout', globals={'session':session})

def userPassCheck(username,password):
  cur.execute("select * from users where username='"+username+"' and password='"+password+"'")
  if len (cur.fetchall() ) > 0:
    return True
  else: return False

def userExists(username):
  cur.execute("select * from users where username='"+username+"'")
  if len (cur.fetchall() ) > 0:
    return True
  else: return False

@app.route('/')
def index():
  return render_template("index.html")

@app.route('/<username>')
def userpage(username):
    return username

@app.route('/users/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    cur.execute("select * from users where username='"+request.form['username']+"'")
    userData = cur.fetchall()
    if len(userData) > 0:
      userData = userData[0]
      if system.cryptography.encryptPassword(request.form['password'], True) == userData['password']: 
        session['username']=userData['username']
        session['password']=userData['password']
        return "1"
      else: return "0"
    else:
      return "0"
  else: return "None"

@app.route('/users/signup', methods=['GET', 'POST'])
def signup():
  if not userExists(request.form['username']) and len(request.form['username']) > 0 and request.form['password1'] == request.form['password2']:
    hashed = system.cryptography.encryptPassword(request.form['password1'], True)
    cur.execute("insert into users (username,password,email) values ('"+request.form['username']+"','"+hashed+"','"+request.form['email']+"')")
    return "1" #SUCCESS
  else: return "0" #ERROR, User doesn't exist or username is too small

#class policy():
#  def GET(self,page):
#    if   page == 'terms-of-service':
#      return render.tos()
#    elif page == 'staff':
#      return render.staff()
#    else:
#      raise app.notfound()

#class redirect():
#  def POST(self,pageToRedirectTo):
#    raise web.seeother("/"+pageToRedirectTo)

#def notfound(): 
#  return web.notfound(render.notfound())

if __name__ == "__main__": app.run(host='0.0.0.0',debug=True)
else: print("DrawRawr isn't a module, silly.")
