from google.appengine.ext import ndb

class UserData(ndb.Model):
    username = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    password = ndb.StringProperty(required=True)
    likes = ndb.StringProperty(repeated=True, default=None)
    dislikes = ndb.StringProperty(repeated=True, default=None)
    comment = ndb.StringProperty(repeated=True, default=None)