#! /usr/bin/python2

import web

from Config import *

urls = (
  '/',                      'index',
  '/art/(.*)',              'art',
  '/policy/(.*)',           'policy',
  '/util/redirect/(.*)',    'redirect',
  '/(.*)',                  'userpage',
)

app = web.application(urls, globals())

render = web.template.render('templates/', base='layout')
render_plain = web.template.render('templates/')

class index():
  def GET(self):
    return render.index()

class userpage():
  def GET(self,name):
    return render.user(name)

class art():
  def GET(self,artID):
    return render.art(artID)

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
