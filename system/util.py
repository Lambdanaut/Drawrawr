def allowedFile(filename,extensions):
  return '.' in filename and \
    filename.rsplit('.', 1)[1] in extensions

def fileType(filename):
  return filename.rsplit('.', 1)[1]
