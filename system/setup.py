from database import Database
import config, os, commands

db = Database(config.dbHost,config.dbPort)

#if config.production: db = Database(config.dbHost,config.dbPort)
#else: db = Database(config.dbHost,config.dbPort,config.dbUsername,config.dbPassword)

def databaseSetup():
  # Incremental Key Setup
  art   = db.db.seq.find_one({"_id" : "art"})
  users = db.db.seq.find_one({"_id" : "users"})
  if not art:
    db.db.seq.insert({"_id" : "art", "next" : 0})
  if not users:
    db.db.seq.insert({"_id" : "users", "next" : 0})  

def directorySetup():
  # /uploads/ setup
  if not os.path.exists("uploads"):
    os.mkdir("uploads")
    os.mkdir(os.path.join("uploads","icons") )
    os.mkdir(os.path.join("uploads","art") )

def javascriptSetup():
  # Compile coffeescript files
  jsPath = os.path.join("static","js")
  if not os.path.exists(os.path.join(jsPath,"main.js")):
    commands.getoutput("coffee -c " + os.path.join(jsPath,"main.coffee") + " " + os.path.join(jsPath,"tabs.coffee") + " " + os.path.join(jsPath,"submit.coffee") + " " + os.path.join(jsPath,"settings.coffee") )

def main():
  databaseSetup()
  directorySetup()
  javascriptSetup()
