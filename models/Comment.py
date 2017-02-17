from google.appengine.ext import ndb

class Comment(ndb.Model):
    blog_id = ndb.TextProperty(required=True)
    status = ndb.BooleanProperty(default=True)
    content = ndb.TextProperty(required=True)
    comment_id = ndb.StringProperty(required=True)
    created_by = ndb.StringProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)
