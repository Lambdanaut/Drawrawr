#! /usr/bin/python2

import web

from Config import *
from Crypto import *

urls = (
  '/',                      'index',
  '/art/(.*)',              'art',
  '/users/login',           'login',
  '/users/signup',          'signup',
  '/policy/(.*)',           'policy',
  '/util/redirect/(.*)',    'redirect',
  '/(.*)',                  'userpage',
)

app = web.application(urls, globals())
db  = web.database(dbn='mysql', db=mysqlDatabase, user=mysqlUsername)
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={})

render = web.template.render('templates', base='layout', globals={'session':session})
render_plain = web.template.render('templates/')

class index():
  def GET(self):
    session.username = "arfenhauze"
    return render.index()

class userpage():
  def GET(self,name):
    return render.user(name)

class art():
  def GET(self,artID):
    return render.art(artID)

class login():
  def POST(self,username,password):
    users = db.select("users", where="username='"+username+"'")
    if len(users) > 0:
      return render.index()
    else:
      return render.art("anus")

class signup():
  def GET(self):
    return render.signup()
  def POST(self):
    data = web.data()
    db.insert("users",username=data.username,hash=data.password)

class policy():
  def GET(self,page):
    if   page == 'terms-of-service':
      return render.tos()
    elif page == 'staff':
      return render.staff()
    else:
      raise app.notfound()

class redirect():
  def POST(self,pageToRedirectTo):
    raise web.seeother("/"+pageToRedirectTo)

def notfound(): 
  return web.notfound(render.notfound())

app.notfound = notfound

if __name__ == "__main__": app.run()
