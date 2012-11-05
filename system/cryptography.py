from math import floor
from hashlib import sha512

import config

def saltPassword(password): 
  if len(password) > 4: password = config.shortSalt1 + password.upper() + config.shortSalt2
  else: password = config.longSalt1 + password + config.longSalt2
  return password

def encryptPassword(password, salt = False):
  if salt: password = saltPassword(password)
  return sha512(password).hexdigest()
