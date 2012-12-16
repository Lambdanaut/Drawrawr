"""
  A module defining interaction with the S3 Amazon Service
  The bucket needs to be publically readable in order to serve the files 
"""

import flask
from boto.s3.connection import S3Connection
from boto.s3.key import Key

import os

from storage import Storage
import config

class S3 (Storage):
  def __init__(self):
    try: import secrets
    except: exit("Error: Amazon's S3 service requires a username and password that can be specifed as the variables wsPublic and wsSecret in the file \"system/secrets.py\"")

    self.bucket_name = config.S3_bucket_name

    self.conn = S3Connection(secrets.wsPublic, secrets.wsSecret)
    self.bucket = self.conn.get_bucket(self.bucket_name)

  def push(self,loc,dest,mimetype = None):
    k = Key(self.bucket)
    k.key = dest
    if mimetype: k.set_metadata('Content-Type', mimetype)
    
    return k.set_contents_from_filename(loc)

  def get(self,filepath): return flask.redirect("https://s3.amazonaws.com/" + self.bucket_name + "/" + filepath)

  def download(self,filepath): 
    """Downloads a file from S3 to the given filepath"""
    if not os.path.exists(filepath):
      k = Key(self.bucket)
      k.key = filepath
      return k.get_contents_to_filename(filepath)

  def delete(self,filepath): 
    k = Key(self.bucket)
    k.key = filepath
    self.bucket.delete_key(k)
