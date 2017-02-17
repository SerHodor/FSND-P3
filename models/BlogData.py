from google.appengine.ext import ndb

class BlogData(ndb.Model):
    status = ndb.BooleanProperty(default=True)
    blog_id = ndb.StringProperty(required=True)
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    like_count = ndb.IntegerProperty(default=0)
    liked_by = ndb.StringProperty(repeated=True, default=None)
    dislike_count = ndb.IntegerProperty(default=0)
    disliked_by = ndb.StringProperty(repeated=True, default=None)
    created_by = ndb.StringProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)
    comment = ndb.StringProperty(repeated=True, default=None)