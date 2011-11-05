from math import floor
from hashlib import sha512

def saltPassword(password): 
  if len(password) > 4:
    password = password[:-floor(len(password) / 3)].lower() + "df$%#@!!h" + password.upper() + password[floor(len(password) / 4):floor(len(password) / 2)] + "!!DR!."
  else:
    password = "#%!DD" + password + "$#&#N%JN323##)(#@#fmmhsppf{s}{[|11^^^43n4jfw@"
  
  return password

def encryptPassword(password, salt):
  if(salt): password = saltPassword(password)
  return sha512(password).digest()