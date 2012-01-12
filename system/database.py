import sys, pymongo, pymongo.objectid

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
  def getUser(self,username):
    return self.db.users.find_one({"lowername": username.lower()})
  def mkUserID(self,passedID):
    try: newID = pymongo.objectid.ObjectId(passedID)
    except: return None
    return newID
  def getKey(self,collection):
    key = self.db.seq.find_one({"_id" : collection})
    if key:
      return key["next"]
    else: return key
  def nextKey(self,collection):
    self.db.seq.update({"_id": collection}, {"$inc" : {"next" : 1 } })
    return self.getKey(collection)
