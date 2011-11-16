#!/usr/bin/python2
#  ____                _____                  ___   ___
# |    \ ___ ___ _ _ _| __  |___ _ _ _ ___   |_  | |   |
# |  |  |  _| .'| | | |    -| .'| | | |  _|  |  _|_| | | 
# |____/|_| |__,|_____|__|__|__,|_____|_|    |___|_|___|
# ------------ A social website for artists ------------

__version__ = '2.0'
__author__  = 'DrawRawr'

import system.cryptography, os, sys, MySQLdb

from Config import *
import flask
from optparse import OptionParser

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

app = flask.Flask(__name__)

#render = web.template.render('templates', base='layout', globals={'session':session})

def userPassCheck(username,password):
  if len (db.select("users", where="username='"+username+"' and password='"+password+"'") ) > 0:
    return True
  else: return False

def userExists(username):
  if len (db.select("users", where="username='"+username+"'") ) > 0:
    return True
  else: return False

@app.route('/')
def index():
  return flask.render_template("index.html")

@app.route('/<username>')
def userpage(username):
    return username

#class login():
#  def POST(self):
#    postData = web.input()
#    userData = db.select("users", where="username='"+postData.username+"'")
#    if len(userData) > 0:
#      userData = userData[0]
#      if system.cryptography.encryptPassword(postData.password, True) == userData.password:
#        session.username=userData.username
#        session.password=userData.password
#        web.setcookie("user",userData.username)
#        web.setcookie("pass",userData.password)
#        return "1"
#      else: return "0"
#    else:
#      return "0"

#class signup():
#  def POST(self):
#    data = web.input()
#    if not userExists(data.username) and len(data.username) > 0 and data.password1 == data.password2:
#      hashed = system.cryptography.encryptPassword(data.password1, True)
#      db.insert("users",username=data.username,password=hashed,email=data.email)
#      return "1" #SUCCESS
#    else: return "0" #ERROR, User doesn't exist or username is too small

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
