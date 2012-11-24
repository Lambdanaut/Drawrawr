import sys, pymongo
import betaGenerator

class Users:
  def __init__ (self, db):
    self.con = db
    self.db = self.con.db
    self.users = db.users

  def get (self, series = {}):
    return self.users.find(series)

  def get_one (self, series = {}):
    return self.users.find_one(series)

  def insert (self, data):
    return self.users.insert(data)

  def update (self, series, data):
    return self.users.update(series, data)

  def delete(self, series):
    return self.users.remove(series)

  def userPassCheck(self, username, password):
    user = self.get_one({'lowername' : username.lower(), 'password' : password})
    if user == None:
      return False
    else: return True

class Keys:
  def __init__ (self, db):
    self.con = db
    self.db = self.con.db
    self.users = db.users

  def get(self, collection):
    key = self.db.seq.find_one({"_id" : collection})
    if key:
      return key["next"]
    else: return key

  def next(self, collection):
    self.db.seq.update({"_id": collection}, {"$inc" : {"next" : 1 } })
    return self.get(collection)