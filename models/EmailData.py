from google.appengine.ext import ndb

class EmailData(ndb.Model):
    username = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)