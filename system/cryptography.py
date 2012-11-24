from math import floor
from hashlib import sha512

import config

def salt_password(password): 
  if len(password) > 4: password = config.short_salt_1 + password.upper() + config.short_salt_2
  else: password = config.long_salt_1 + password + config.long_salt_2
  return password

def encrypt_password(password, salt = False):
  if salt: password = salt_password(password)
  return sha512(password).hexdigest()
