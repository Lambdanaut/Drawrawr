""" A module for storing and accessing files on the local server. """
import flask
import os
import magic

from storage import Storage

import config

class Local_Storage (Storage):
  def get(self,filepath):
    (directory, filename) = os.path.split(filepath.lower())
    try: return flask.send_from_directory(directory,filename)
    except: flask.abort(404)

  def delete(self,filepath): 
    return os.remove(filepath)