import sys, pymongo
import betaGenerator

# To execute a general query: 
# db.db.CollectionName.QueryType(QUERY)
# For example: 
# user = db.db.users.find_one({"username" : "Lambdanaut"})

class Database:
  def __init__ (self,host,port,username=None,password=None):
    self.con = pymongo.Connection(host, port)
    if username and password:
      self.db  = self.con.heroku_app2925802
      self.db.authenticate(username, password)
    else: self.db  = self.con.DR
  def userPassCheck(self,username,password):
    user = self.db.users.find_one({'lowername' : username.lower(),'password' : password})
    if user == None:
      return False
    else: return True
  def userExists(self,username):
    user = self.db.users.find_one({"lowername": username.lower()})
    if user == None:
      return False
    else: return True
  def getUser(self,username):
    return self.db.users.find_one({"lowername": username.lower()})
  def getKey(self,collection):
    key = self.db.seq.find_one({"_id" : collection})
    if key:
      return key["next"]
    else: return key
  def nextKey(self,collection):
    self.db.seq.update({"_id": collection}, {"$inc" : {"next" : 1 } })
    return self.getKey(collection)
  def generateBetaPass(self,length=8,ownerName=None):
    password = betaGenerator.generatePassword(length)
    if not self.db.betaPass.find_one({"password": password}):
      self.db.betaPass.insert({"owner": ownerName, "password": password})
      return password
    else: self.generateBetaPass(length,ownerName)
  def checkBetaPass(self, password):
    if self.db.betaPass.find_one({"password": password.lower()}):
      self.db.betaPass.remove({"password": password.lower()})
      return True
    else: return False
