import random

def intsToString(numbers):
  string = ""
  for number in numbers:
    string += chr(number)
  return string

def generatePassword(length):
  pos = 0
  password = []
  while pos < length:
    password.append(random.randint(97,122))
    pos+=1
  return intsToString(password)