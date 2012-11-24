import config, os, commands

def database_setup(db):
  # Incremental Key Setup
  art      = db.seq.find_one({"_id" : "art"})
  users    = db.seq.find_one({"_id" : "users"})
  journals = db.seq.find_one({"_id" : "journals"})
  comments = db.seq.find_one({"_id" : "comments"})
  if not art:
    db.seq.insert({"_id" : "art", "next" : 0})
  if not users:
    db.seq.insert({"_id" : "users", "next" : 0})  
  if not journals:
    db.seq.insert({"_id" : "journals", "next" : 0})  
  if not comments:
    db.seq.insert({"_id" : "comments", "next" : 0})  

def directory_setup():
  # /uploads/ setup
  if not os.path.exists("uploads"):
    os.mkdir("uploads")
    os.mkdir(os.path.join("uploads","icons") )
    os.mkdir(os.path.join("uploads","art") )
    os.mkdir(os.path.join("uploads","thumbs") )

def javascript_setup():
  # Compile coffeescript files
  jsPath = os.path.join("static","js")
  if not os.path.exists(os.path.join(jsPath,"main.js")):
    commands.getoutput("coffee -c " + os.path.join(jsPath,"main.coffee") + " " + os.path.join(jsPath,"tabs.coffee") + " " + os.path.join(jsPath,"submit.coffee") + " " + os.path.join(jsPath,"settings.coffee") )

def main(db):
  database_setup(db)
  directory_setup()
  javascript_setup()
