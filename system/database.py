import sys, MySQLdb
from config import *

try:
  con = MySQLdb.connect(mysqlHost, mysqlUsername, mysqlPassword, mysqlDatabase);

  cur = con.cursor(MySQLdb.cursors.DictCursor)
  cur.execute("SELECT VERSION()")

  data = cur.fetchone()
    
  print "Database version : %s " % data
    
except MySQLdb.Error, e:
  print "Error %d: %s" % (e.args[0],e.args[1])
  sys.exit(1)
