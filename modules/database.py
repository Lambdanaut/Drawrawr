import sys, pymongo

# To execute a general query: 
# db.db.CollectionName.QueryType(QUERY)
# For example: 
# user = db.db.users.find_one({"username" : "Lambdanaut"})

class Database:
  def __init__ (self,host,port):
    self.con = pymongo.Connection(host, port)
    self.db  = self.con.DR
  def userPassCheck(self,username,password):
    user = self.db.users.find_one({'lowername' : username.lower(),'password' : password})
    if user == None:
      return False
    else: return True
  def userExists(self,username):
    user = self.db.users.find_one({"lowername":username.lower()})
    if user == None:
      return False
    else: return True
  def getUser(self,session):
    if "username" in session:
      return self.db.users.find_one({"lowername":session["username"].lower()})
