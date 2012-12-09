import sys
import pymongo

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

  def update (self, series, data, method = "$set"):
    set_data = {} 
    set_data[method] = data
    return self.users.update(series, set_data)

  def increment (self, series, data):
    return self.update(series, data, "$inc")

  def increment_views (self, series, value = 1):
    return self.increment(series, {"page_views" : value})

  def increment_beta_keys (self, series, value = 1):
    return self.increment(series, {"beta_keys" : value})

  def delete (self, series):
    return self.users.remove(series)

  def user_pass_check (self, username, password):
    user = self.get_one({'lowername' : username.lower(), 'password' : password})
    if user == None:
      return False
    else: return True

  def username_taken (self, username):
    user = self.get_one({'lowername' : username.lower()})
    if user == None:
      return False
    else: return True

class Art:
  def __init__ (self, db):
    self.con = db
    self.db = self.con.db
    self.art = db.art
    self.feature = db.feature

  def get (self, series = {}):
    return self.art.find(series)

  def get_one (self, series = {}):
    return self.art.find_one(series)

  def insert (self, data):
    return self.art.insert(data)

  def update (self, series, data, method = "$set"):
    set_data = {}
    set_data[method] = data
    return self.art.update(series, set_data)

  def increment (self, series, data):
    return self.update(series, data, "$inc")

  def increment_fav_amount (self, series, value = 1):
    return self.increment(series, {"fav_amount" : value})

  def increment_views (self, series, value = 1):
    return self.increment(series, {"views" : value})

  def delete (self, series):
    return self.art.remove(series)

  def get_feature (self, series):
    return self.feature.find(series)

  def suggest_feature (self, data):
    return self.feature.insert(data)

class Journals:
  def __init__ (self, db):
    self.con = db
    self.db = self.con.db
    self.journals = db.journals

  def get (self, series = {}):
    return self.journals.find(series)

  def get_one (self, series = {}):
    return self.journals.find_one(series)

  def insert (self, data):
    return self.journals.insert(data)

  def update (self, series, data, method = "$set"):
    set_data = {}
    set_data[method] = data
    return self.journals.update(series, set_data)

  def increment (self, series, data):
    return self.update(series, data, "$inc")

  def increment_views (self, series, value = 1):
    return self.increment(series, {"views" : value})

  def delete(self, series):
    return self.journals.remove(series)

class Comments:
  def __init__ (self, db):
    self.con = db
    self.db = self.con.db
    self.comments = db.comments

  def get (self, series = {}):
    return self.comments.find(series)

  def get_one (self, series = {}):
    return self.comments.find_one(series)

  def insert (self, data):
    return self.comments.insert(data)

  def update (self, series, data, method = "$set"):
    set_data = {}
    set_data[method] = data
    return self.comments.update(series, set_data)

  def increment (self, series, data):
    return self.update(series, data, "$inc")

  def delete(self, series):
    return self.comments.remove(series)

class Keys:
  def __init__ (self, db):
    self.con = db
    self.db = self.con.db
    self.users = db.users

  def get (self, collection):
    key = self.db.seq.find_one({"_id" : collection})
    if key:
      return key["next"]
    else: return key

  def next (self, collection):
    self.db.seq.update({"_id": collection}, {"$inc" : {"next" : 1 } })
    return self.get(collection)

class Beta_Pass:
  def __init__ (self, db):
    import betaGenerator

    self.con = db
    self.db = self.con.db
    self.beta_pass = db.beta_pass

  def generate (self, length=8, owner_name=None):
    password = beta_generator.generate_password(length)
    if not self.beta_pass.find_one({"password": password}):
      self.beta_pass.insert({"owner": owner_name, "password": password})
      return password
    else: self.generate(length, ownerName)

  def check (self, password):
    if self.beta_pass.find_one({"password": password.lower()}):
      self.beta_pass.remove({"password": password.lower()})
      return True
    else: return False