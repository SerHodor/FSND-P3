import os
import jinja2
import webapp2

import re
import hmac
import json
# import models
from models.BlogData import BlogData
from models.Comment import Comment
from models.EmailData import EmailData
from models.UserData import UserData

from google.appengine.ext import ndb
public_dir = os.path.join(os.path.dirname(__file__), 'public')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(public_dir), autoescape=True)

Secret = "659c45c6-5179-4a7d-917d-d4e4b32c7c4b"


class Handler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# Main page handler


class MainPage(Handler):

    def get(self):
        # check if user is logged in
        usernameCookie = self.request.cookies.get("userid", 0)
        username = vaild_cookie(usernameCookie)

        # fetch blogs
        blogs = BlogData.query().order(-BlogData.created).fetch(10)

        if username:

            user = ndb.Key('UserData', encrypt(username)).get()
            # Check if user has already liked/disliked the post
            # or it is user's own blog
            for blog in blogs:
                blog.userResponse = 0
                if blog.blog_id in user.likes:
                    blog.userResponse = 1
                elif blog.blog_id in user.dislikes:
                    blog.userResponse = 2
                # userResponse 3 for self blogs
                if blog.created_by == user.username:
                    blog.userResponse = 3

        else:
            for blog in blogs:
                blog.userResponse = 0

        # Fetching comments
        for blog in blogs:
            comments = []
            for comment in blog.comment:
                get_comment = ndb.Key('Comment', encrypt(comment)).get()
                comments.append(get_comment)
            blog.fetchedComments = comments

        self.render("front.html", username=username, blogs=blogs)


class SignUp(Handler):

    def get(self):
        self.render("signup.html")

    def post(self):
        # input validity regex
        Username = "^[a-zA-Z0-9_-]{3,20}$"
        Password = "^.{3,20}$"
        Email = "^[\S]+@[\S]+.[\S]+$"

        username = self.request.get("username")
        email = self.request.get("email")
        password = self.request.get("password")
        re_password = self.request.get("re_password")

        username_error = False
        email_error = False
        password_error = False
        re_password_error = False

        if not username or not valid_string(username, Username):
            username_error = "Enter a valid Username"
        if email and not valid_string(email, Email):
            email_error = "Enter a valid email address"
        if not password or (password and not valid_string(password, Password)):
            password_error = "Enter a valid Password"
        if re_password != password:
            re_password_error = "Passwords don't match"

        try:
            if username and ndb.Key('UserData', encrypt(
                    username)).get().username == username:
                username_error = "Username already exists."
        except:
            pass

        try:
            if email and ndb.Key(
                'EmailData',
                    encrypt(email)).get().email == email:
                email_error = "Email already exists."
        except:
            pass

        x = username_error or email_error
        x = x or password_error or re_password_error
        if x:
            self.render(
                "signup.html",
                username_old=username,
                email_old=email,
                username_error=username_error,
                password_error=password_error,
                email_error=email_error,
                re_password_error=re_password_error)
        else:

            if not email:
                email = ""

            password = encrypt(password)
            userData = UserData(username=username,
                                password=password, email=email)
            userData.key = ndb.Key('UserData', encrypt(username))

            if email != "":
                emailData = EmailData(username=username, email=email)
                emailData.key = ndb.Key('EmailData', encrypt(email))
                ndb.put_multi([userData, emailData])
            else:
                user_key = userData.put()
            usernameCookie = str('userid=' + username +
                                 "|" + encrypt(username))
            self.response.headers.add_header(
                'Set-Cookie', usernameCookie)
            self.response.headers.add_header(
                'Set-Cookie', 'Path=/')
            self.redirect("/Welcome")

# Encrypt Password


def encrypt(password):
    return hmac.new(Secret, password).hexdigest()

# check validity of input string against its regex


def valid_string(string, string_regex):
    return re.compile(string_regex).match(string)

# make sure cookie isn't tempered


def vaild_cookie(string):
    return_value = False
    try:
        value = string.split("|")[0]
        encryptedvalue = string.split("|")[1]
        if value and encryptedvalue:
            if encryptedvalue == encrypt(value):
                return_value = value
    except:
        pass
    return return_value

# Welcome page


class Welcome(Handler):

    def get(self):
        usernameCookie = self.request.cookies.get("userid", 0)
        username = vaild_cookie(usernameCookie)

        if username:
            welcomeMsg = "Welcome! " + username
            self.render("welcome.html", username=username,
                        welcomeMsg=welcomeMsg)
        else:
            self.redirect("/SignUp")


class AddNewPost(Handler):

    def get(self):
        usernameCookie = self.request.cookies.get("userid", 0)
        username = vaild_cookie(usernameCookie)
        # Redirect to login if not logged in
        if not username:
            self.redirect("/LogIn")
            return
        self.render("addnewpost.html", username=username)

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content").replace('\n', '<br>')
        # check user validity
        usernameCookie = self.request.cookies.get("userid", 0)
        username = vaild_cookie(usernameCookie)
        if not username:
            self.redirect("/LogIn")
            return

        error = True
        if subject and content:
            error = False
        if error:
            self.render("addnewpost.html", error=error,
                        subject=subject, content=content)
            return
        # Create new blog
        blog_id = BlogData.query().count() + 1
        blog_id = str(blog_id)
        blog = BlogData(subject=subject, content=content,
                        blog_id=blog_id, created_by=username)
        blog.key = ndb.Key('BlogData', encrypt(blog_id))
        blog_key = blog.put()
        # Redirect to blog website
        self.redirect("/" + blog_id)

# Handles Permalink Page


class PostPage(Handler):

    def get(self, blog_id):
        # check input validity
        error = True
        try:
            if str(
                ndb.Key(
                    'BlogData',
                    encrypt(blog_id)).get().blog_id) == blog_id:
                error = False
        except:
            pass

        if error is True:
            self.error(404)
            return

        usernameCookie = self.request.cookies.get("userid", 0)
        username = vaild_cookie(usernameCookie)

        blog = ndb.Key('BlogData', encrypt(blog_id)).get()
        blog.userResponse = 0
        # check if user has already liked/disliked the post
        # or it is user's post
        if username:
            user = ndb.Key('UserData', encrypt(username)).get()
            if blog.blog_id in user.likes:
                blog.userResponse = 1
            elif blog.blog_id in user.dislikes:
                blog.userResponse = 2
            # userResponse 3 for self blogs
            if blog.created_by == user.username:
                blog.userResponse = 3

        self.render("permalink.html", blog=blog, username=username)


class LogIn(Handler):

    def get(self):
        self.render("login.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        valid = False
        try:
            if username and ndb.Key('UserData', encrypt(
                    username)).get().password == encrypt(password):
                valid = True
        except:
            pass

        if valid:
            usernameCookie = str('userid=' + username +
                                 "|" + encrypt(username))
            self.response.headers.add_header(
                'Set-Cookie', usernameCookie)
            self.response.headers.add_header(
                'Set-Cookie', 'Path=/')
            self.redirect("/Welcome")
        else:
            error = "Invalid Username or Password"
            self.render("login.html", error=error)


class LogOut(Handler):

    def get(self):
        # Remove cookie
        self.response.headers.add_header(
            'Set-Cookie', 'userid=')
        self.response.headers.add_header(
            'Set-Cookie', 'Path=/')
        self.redirect("/LogIn")

# Handles like, dislike and creates comment


class UserResponse(Handler):

    def post(self, blog_id):
        # Check user login validity
        usernameCookie = self.request.cookies.get("userid", 0)
        username = vaild_cookie(usernameCookie)

        toDo = self.request.get("toDo")

        if (not username) and (toDo == "Like" or toDo == "DisLike"):
            self.write("Please Log in to register your response")
            return

        if username:
            user = ndb.Key('UserData', encrypt(username)).get()

        blog = ndb.Key('BlogData', encrypt(blog_id)).get()

        if toDo == "Like" or toDo == "DisLike":
            if blog.created_by == user.username:
                self.write(
                    "You can't respond to Like/Dislike your own own post")
                return

        if toDo == "Like":

            # Like
            if user.username not in blog.liked_by:
                # Remove Dislike
                if user.username in blog.disliked_by:
                    blog.disliked_by.remove(user.username)
                    user.dislikes.remove(blog_id)
                    blog.dislike_count -= 1

                blog.liked_by.append(user.username)
                blog.like_count += 1
                user.likes.append(blog.blog_id)

            # Unlike
            else:
                blog.liked_by.remove(user.username)
                user.likes.remove(blog.blog_id)
                blog.like_count -= 1

            ndb.put_multi([user, blog])
            return

        elif toDo == "DisLike":

            # Dislike
            if user.username not in blog.disliked_by:
                # Remove Dislike
                if user.username in blog.liked_by:
                    blog.liked_by.remove(user.username)
                    user.likes.remove(blog_id)
                    blog.like_count -= 1

                blog.disliked_by.append(user.username)
                blog.dislike_count += 1
                user.dislikes.append(blog.blog_id)

            # UnDislike
            else:
                blog.disliked_by.remove(user.username)
                user.dislikes.remove(blog.blog_id)
                blog.dislike_count -= 1

            ndb.put_multi([user, blog])
            return

        elif toDo == "Comment" and username:
            # Create comment entity
            content = self.request.get("content")
            if content:
                comment_id = Comment.query().count() + 1
                comment_id = str(comment_id)
                comment = Comment(
                    content=content,
                    comment_id=comment_id,
                    created_by=user.username,
                    blog_id=blog.blog_id)
                comment.key = ndb.Key('Comment', encrypt(comment_id))

                user.comment.append(comment_id)
                blog.comment.append(comment_id)

                ndb.put_multi([user, blog, comment])

        if toDo == "Comment":
            # Fetch comments
            comments = []
            for comment in blog.comment:
                hold = {}
                get_comment = ndb.Key('Comment', encrypt(comment)).get()
                hold["comment_id"] = get_comment.comment_id
                hold["content"] = get_comment.content
                hold["created_by"] = get_comment.created_by
                comments.append(hold)

            self.write(json.dumps(comments))
            return


class EditBlog(Handler):

    def get(self, blog_id):
        # Check login validity
        error = True
        try:
            if str(
                ndb.Key(
                    'BlogData',
                    encrypt(blog_id)).get().blog_id) == blog_id:
                error = False
        except:
            pass

        if error is True:
            self.error(404)
            return

        usernameCookie = self.request.cookies.get("userid", 0)
        username = vaild_cookie(usernameCookie)
        # Show error if user not logged in
        if not username:
            error = "Please Log in to register your response"
            self.render("error.html", username=username, error=error)
            return

        blog = ndb.Key('BlogData', encrypt(blog_id)).get()
        user = ndb.Key('UserData', encrypt(username)).get()
        # Show error if id not matched
        if blog.created_by != user.username:
            error = "You are not authorized to access this page."
            self.render("error.html", username=username, error=error)
            return

        self.render("edit.html", username=username, blog=blog)

    def post(self, blog_id):
        subject = self.request.get("subject")
        content = self.request.get("content").replace('\n', '<br>')
        # Check login validity
        error = True
        try:
            if str(
                ndb.Key(
                    'BlogData',
                    encrypt(blog_id)).get().blog_id) == blog_id:
                error = False
        except:
            pass

        if error is True:
            self.error(404)
            return

        usernameCookie = self.request.cookies.get("userid", 0)
        username = vaild_cookie(usernameCookie)
        if not username:
            self.redirect("/LogIn")
            return

        error = True
        if subject and content:
            error = False
        if error:
            self.render("addnewpost.html", error=error,
                        subject=subject, content=content)
            return
        # Get entity and modify content
        blog = ndb.Key('BlogData', encrypt(blog_id)).get()
        user = ndb.Key('UserData', encrypt(username)).get()

        if blog.created_by != user.username:
            error = "You are not authorized to access this page."
            self.render("error.html", username=username, error=error)
            return

        blog.subject = subject
        blog.content = content
        blog.put()

        self.redirect("/" + blog_id)


class ModifyComment(Handler):

    def post(self, command, comment_id):
        # check login validity
        usernameCookie = self.request.cookies.get("userid", 0)
        username = vaild_cookie(usernameCookie)
        if not username:
            self.write("You are not authorized to access this page")
            return

        comment = ndb.Key('Comment', encrypt(comment_id)).get()

        if comment.created_by != username:
            self.write("You are not authorized to access this page")
            return

        user = ndb.Key('UserData', encrypt(username)).get()

        content = self.request.get("content")
        # Edit comment
        if command == "edit":
            comment.content = content
            comment.put()
            self.write("success")
            return
        # Delete comment
        if command == "delete":
            blog_id = comment.blog_id
            blog = ndb.Key('BlogData', encrypt(blog_id)).get()
            user.comment.remove(comment_id)
            blog.comment.remove(comment_id)
            ndb.put_multi([blog, user])
            comment.key.delete()
            self.write("success")
            return

        self.write(command + comment_id)


class DeleteBlog(Handler):

    def post(self, blog_id):
        error = True
        try:
            if str(
                ndb.Key(
                    'BlogData',
                    encrypt(blog_id)).get().blog_id) == blog_id:
                error = False
        except:
            pass

        if error is True:
            self.error(404)
            return
        # check login validity
        usernameCookie = self.request.cookies.get("userid", 0)
        username = vaild_cookie(usernameCookie)
        if not username:
            error = "You are not authorized to access this page."
            self.render("error.html", username=username, error=error)
            return

        blog = ndb.Key('BlogData', encrypt(blog_id)).get()
        user = ndb.Key('UserData', encrypt(username)).get()

        if blog.created_by != user.username:
            error = "You are not authorized to access this page."
            self.render("error.html", username=username, error=error)
            return

        # remove comments
        for comment in blog.comment:
            thisComment = ndb.Key('Comment', encrypt(comment)).get()
            username = thisComment.created_by
            username = ndb.Key('UserData', encrypt(username)).get()
            username.comment.remove(thisComment.comment_id)
            username.put()
            thisComment.key.delete()

        blog.key.delete()

        self.write("success")


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/SignUp', SignUp),
    ('/Welcome', Welcome),
    ('/AddNewPost', AddNewPost),
    ('/LogIn', LogIn),
    ('/LogOut', LogOut),
    ('/([0-9]+)', PostPage),
    ('/([0-9]+)/UserResponse', UserResponse),
    ('/([0-9]+)/EditBlog', EditBlog),
    ('/([0-9]+)/DeleteBlog', DeleteBlog),
    ('/comments/(.+)/([0-9]+)', ModifyComment)
], debug=True)
