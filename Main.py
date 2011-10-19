import web

render = web.template.render("public/")

urls = (
  '/',   'index',
  '.*',  'userpage',
)

app = web.application(urls, globals())

class index:
  def GET(self):
    return render.index()

class userpage:
  def GET(self):
    return "arf"

if __name__ == "__main__": app.run()
