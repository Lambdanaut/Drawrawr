import sys, pymongo
import betaGenerator

class Database:
  def __init__ (self,host,port,username=None,password=None):
    self.con = pymongo.Connection(host, port)
    if username and password:
      self.db  = self.con.heroku_app2925802
      self.db.authenticate(username, password)
    else: self.db  = self.con.DR
  def userExists(self,username):
    user = self.db.users.find_one({"lowername": username.lower()})
    if user == None:
      return False
    else: return True
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
