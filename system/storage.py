# Defines the methods of storing uploaded files. 

class Filesystem:
  def __init__(self):
    pass

class Storage:
  def __init__(self,s3 = False):
    if s3:
      import S3
      self.device = S3.S3()
    else:  self.device = Filesystem() 
