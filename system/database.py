import sys, pymongo
import betaGenerator

class Database:
  def __init__ (self,host,port,username=None,password=None):
    self.con = pymongo.Connection(host, port)
    if username and password:
      self.db  = self.con.heroku_app2925802
      self.db.authenticate(username, password)
    else: self.db  = self.con.DR
