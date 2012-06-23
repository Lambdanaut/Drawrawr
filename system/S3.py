# A module defining interaction with the S3 Amazon Service
# The bucket needs to be publically readable in order to serve the files 

import os

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from storage import Storage

class S3 (Storage):
  def __init__(self):
    try: import secrets
    except: exit("Error: Amazon's S3 service requires a username and password that can be specifed as the variables wsPublic and wsSecret in the file \"system/secrets.py\"")

    self.bucketName = "drawrawr"

    self.conn = S3Connection(secrets.wsPublic, secrets.wsSecret)
    self.bucket = self.conn.get_bucket(self.bucketName)

  def push(self,loc,dest,mimetype = None):
    k = Key(self.bucket)
    k.key = dest
    if mimetype: k.set_metadata('Content-Type', mimetype)
    
    k.set_contents_from_filename(loc)

  def get(self,filepath): return "https://s3.amazonaws.com/drawrawr/" + filepath

  def download(self,filepath): 
    if not os.path.exists(filepath):
      k = Key(self.bucket)
      k.key = filepath
      k.get_contents_to_filename(filepath)

  def delete(self,filepath): 
    k = Key(self.bucket)
    k.key = filepath
    self.bucket.delete_key(k)
