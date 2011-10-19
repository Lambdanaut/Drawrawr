import web

render = web.template.render("templates/")

urls = (
  '/',   'index',
  '.*',  'userpage',
)

app = web.application(urls, globals())

class SitePage:
  def render(self,pageToRender):
    head = render.header()
    return str(head) + str(pageToRender)

class index(SitePage):
  def GET(self):
    return render.index()

class userpage(SitePage):
  def GET(self):
    return "arf"

if __name__ == "__main__": app.run()
