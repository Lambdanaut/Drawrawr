from math import floor
from hashlib import sha512

def saltPassword(password): 
  if len(password) > 4: password = "SDDG$##@Hfa" + password.upper() + "3r#$^&2andgjngds"
  else: password = "#%!DD" + password + "$#&#N%JN323##)(#@#fmmhsppf{s}{[|11^^^43n4jfw@-"
  return password

def encryptPassword(password, salt = False):
  if(salt): password = saltPassword(password)
  return sha512(password).digest()
