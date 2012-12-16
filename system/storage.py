# A template class for storage

class Storage:
  def __init__(self):
    pass
  def push(self,loc,dest,mimetype=None):
    """Saves a file from one location to a destination"""
    pass
  def get(self,filepath):
    """Given a short filepath like /uploads/art/image.jpg, returns a direct URL to the file in storage. """
    pass
  def download(self,filepath):
    """Gets the file for use"""
    pass
  def delete(self,filepath):
    """Deletes a file given its short filepath"""
    pass
