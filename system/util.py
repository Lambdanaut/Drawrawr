def allowedFile(filename,extensions):
  return '.' in filename and \
    filename.rsplit('.', 1)[1] in extensions

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
