def allowedFile(filename,extensions):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in extensions

def fileType(filename):
  return filename.rsplit('.', 1)[1]

def printList(l):
  newL = ""
  while not len(l) == 0:
    newL += l.pop()
    if len(l) > 0:
      newL += ", "
  return newL

def inList(v,l):
  for item in l:
    if v == item:
      return True
  return False

def dictToList(d):
  l = []
  for k in d:
    l.append(d[k])
  return l

# Despite the name, this just checks to make sure every key in d1 has a counterpart in d2 that's value is the same. 
def compareDicts(d1,d2):
  for key in d1:
    if key in d2:
      if not d1[key] == d2[key]: return False
    else: return False
  return True

# Same as above, but compares the key names rather than the key values. 
def compareDictKeys(d1,d2):
  for key in d1:
    if not key in d2: return False
  return True

# Takes two dicts with the same keys and puts the key's values together like this: concDictValues({1:"o",2:"tw"},{1:"ne",2:"o"}) == {1:["o","ne"],2:["tw","o"]}
def concDictValues(d1,d2):
  newD = {}
  for key in d1:
    if key in d2:
      newD[key] = [d1[key], d2[key] ]
  return newD

# Decodes a URL string to a dict of strings
# Example: urlDecode("name=lambdanaut&age=20&") = {"name" : "lambdanaut", "age" : "20"}
# Note: Last character in string must be ampersand
def urlDecode(string):
  result = {}
  curVal  = ""
  curName = ""
  isName=True
  for letter in string:
    if isName:
      if letter != "=": curName += letter
      else: isName=False
    else:
      if letter != "&": curVal += letter
      else:
        result[curName] = curVal
        curVal = curName = ""
        isName=True
  return result
