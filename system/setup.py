from database import Database
import config

db = Database(config.dbHost,config.dbPort)

def databaseSetup():
  art   = db.db.seq.find_one({"_id" : "art"})
  users = db.db.seq.find_one({"_id" : "users"})
  if not art:
    db.db.seq.insert({"_id" : "art", "next" : 0})
  if not users:
    db.db.seq.insert({"_id" : "users", "next" : 0})
  

def main():
  databaseSetup()
