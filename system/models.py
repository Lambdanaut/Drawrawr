import sys, pymongo

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

  def user_pass_check(self, username, password):
    user = self.get_one({'lowername' : username.lower(), 'password' : password})
    if user == None:
      return False
    else: return True

class Art:
  def __init__ (self, db):
    self.con = db
    self.db = self.con.db
    self.art = db.art

  def get (self, series = {}):
    return self.art.find(series)

  def get_one (self, series = {}):
    return self.art.find_one(series)

  def insert (self, data):
    return self.art.insert(data)

  def update (self, series, data):
    return self.art.update(series, data)

  def delete(self, series):
    return self.art.remove(series)

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

class Beta_Pass:
  def __init__ (self, db):
    import betaGenerator

    self.con = db
    self.db = self.con.db
    self.beta_pass = db.beta_pass
 def generate_beta_pass(self, length=8, owner_name=None):
    password = beta_generator.generate_password(length)
    if not self.beta_pass.find_one({"password": password}):
      self.beta_pass.insert({"owner": owner_name, "password": password})
      return password
    else: self.generate_beta_pass(length, ownerName)

  def check_beta_pass(self, password):
    if self.beta_pass.find_one({"password": password.lower()}):
      self.beta_pass.remove({"password": password.lower()})
      return True
    else: return False