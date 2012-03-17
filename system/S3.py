# A module defining interaction with the S3 Amazon Service

import os

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from storage import Storage

class S3 (Storage):
  def __init__(self):
    try: import secrets
    except: exit("Error: Amazon's S3 service requires a username and password that can be specifed as the variables wsPublic and wsSecret in the file system/secrets.py")

    self.conn = S3Connection(secrets.wsPublic, secrets.wsSecret)
    self.bucket = self.conn.get_bucket("drawrawr")

  def push(self,loc,dest):
    k = Key(self.bucket)
    k.key = dest
    k.set_contents_from_filename(loc)

  def get(self,filepath):
    k = Key(self.bucket)
    k.key = filepath
    return k.generate_url(5)

  def delete(self,filepath):
    pass
