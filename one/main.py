#!/usr/bin/python
# -*- coding: utf-8 -*-
# main.py

"""
README:
STANDARD WAY OF GETTING ARTICLEID IS AS FOLLOWS:
bigstr = link + title + author + source
newArticle.articleid = hash(bigstr)
"""


import webapp2
import jinja2
from authomatic import Authomatic
from authomatic.adapters import Webapp2Adapter
from google.appengine.ext import ndb
import os

from webapp2_extras import sessions
from authomatic.extras import gae
import authomatic

from config import CONFIG

THIS_SECRET = "asodf9823r823r0jdfjsd90jv08xuv0312rdfgg389ty89uf"

def isAdmin(ident):
    return (ident == 1378560375496743 or ident == '1378560375496743' or ident == 1349891298407897 or ident == '1349891298407897')
# Instantiate Authomatic.
authomatic = Authomatic(config=CONFIG, secret='some random secret string')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# Create a simple request handler for the login procedure.
class Rating(ndb.Model):
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    userid = ndb.IntegerProperty(indexed=False)
    articleid = ndb.IntegerProperty(indexed=False)
    rating = ndb.IntegerProperty(indexed=False)

class DAUser(ndb.Model):
    daid = ndb.IntegerProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)
    age = ndb.IntegerProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    apilink = ndb.StringProperty(indexed=False)
    politic = ndb.StringProperty(indexed=False)

class Article(ndb.Model):
    articleid = ndb.IntegerProperty(indexed=False)
    title = ndb.StringProperty(indexed=True)
    link = ndb.StringProperty(indexed=False)
    author = ndb.StringProperty(indexed=False)
    source = ndb.StringProperty(indexed=False)
    text = ndb.StringProperty(indexed=False)

class Politics(webapp2.RequestHandler):
    def post(self, idthing):
        politic = self.request.get('politic')
        # result = authomatic.login(Webapp2Adapter(self), 'fb')
        # if not (result.user.name and result.user.id):
        #     result.user.update()
        key = ndb.Key(DAUser, str(idthing))

        theuser = key.get()
        theuser.politic = politic
        theuser.put()
        context = {'ident':idthing}
        template = JINJA_ENVIRONMENT.get_template('finished.html')
        self.response.write(template.render(context))
    def get(self, idthing):
        self.redirect('/nextStep/' + str(idthing))

class NextStep(webapp2.RequestHandler):
    def get(self):
        session = gae.Webapp2Session(self, secret=THIS_SECRET)
        idthing = session.get('ident')
        key = ndb.Key(DAUser, str(idthing))
        theuser = key.get()
        politic = theuser.politic
        if politic == None or politic == 'None':
            context = {'name':theuser.name,
                       'id':idthing}
            template = JINJA_ENVIRONMENT.get_template('politics.html')
            self.response.write(template.render(context))
        else:
            context = {'name':theuser.name,
                       'id':idthing,
                       'admin':isAdmin(idthing)}
            template = JINJA_ENVIRONMENT.get_template('existingUser.html')
            self.response.write(template.render(context))

class AddArticle(webapp2.RequestHandler):
    def get(self):
        session = gae.Webapp2Session(self, secret=THIS_SECRET)
        idthing = session.get('ident')
        if not isAdmin(idthing):
            self.redirect('/')
        context = {'ident':idthing}
        template = JINJA_ENVIRONMENT.get_template('addArticle.html')
        self.response.write(template.render(context))
    def post(self):
        session = gae.Webapp2Session(self, secret=THIS_SECRET)
        idthing = session.get('ident')
        if not isAdmin(idthing):
            self.redirect('/')
        link = self.request.get('link')
        title = self.request.get('title')
        author = self.request.get('author')
        source = self.request.get('source')
        bigstr = link + title + author + source
        articleid = hash(bigstr)
        newArticle = Article()
        key = ndb.Key(Article, str(articleid))
        newArticle.key = key
        newArticle.title = title
        newArticle.author = author
        newArticle.source = source
        newArticle.link = link
        newArticle.articleid = articleid
        newArticle.put()
        self.redirect('/addArticle')

class ViewArticles(webapp2.RequestHandler):
    def get(self):
        session = gae.Webapp2Session(self, secret=THIS_SECRET)
        idthing = session.get('ident')
        if not isAdmin(idthing):
            self.redirect('/')
        articles = Article.query().fetch(10)
        realarts = []
        for article in articles:
            realarts.append(article.title)
        context = {'articles':realarts}
        template = JINJA_ENVIRONMENT.get_template('viewArticles.html')
        self.response.write(template.render(context))
        
class ExtensionConnection(webapp2.RequestHandler):
    def get(self, idthing):
        file = open('toSend.txt', 'r')
        towrite = file.read()
        self.response.write(towrite)

class Login(webapp2.RequestHandler):
    
    # The handler must accept GET and POST http methods and
    # Accept any HTTP method and catch the "provider_name" URL variable.

    def any(self, provider_name):                
        # It all begins with login.
        # Webapp2 session
        session = gae.Webapp2Session(self, secret=THIS_SECRET)

        result = authomatic.login(Webapp2Adapter(self),
                                  provider_name,
                                  session=session,
                                  session_saver=session.save)

        #result = authomatic.login(Webapp2Adapter(self), provider_name)
        # Do not write anything to the response if there is no result!
        if result:
            # If there is result, the login procedure is over and we can write to response.
            
            if result.error:
                # Login procedure finished with an error.
                self.response.write(u'<h2>Damn that error: {}</h2>'.format(result.error.message))
            
            elif result.user:
                # Hooray, we have the user!
                
                # OAuth 2.0 and OAuth 1.0a provide only limited user data on login,
                # We need to update the user to get more info.
                if not (result.user.name and result.user.id):
                    result.user.update()
                #id, name, age, email
                #we're going to use the ID as the key
                ident = result.user.id
                name = result.user.name
                email = result.user.email
                key = ndb.Key(DAUser, str(ident))
                session['ident'] = ident
                session.save()
                potuser = key.get()
                if potuser == None:
                    newuser = DAUser()
                    newuser.key = key
                    newuser.daid = int(ident)
                    newuser.name = name
                    newuser.email = email
                    newuser.put()
                self.response.write('<meta http-equiv="refresh" content="0; url=/nextStep/" /><p>Click <a href="/nextStep/">here</a> if you are not redirected quickly.</p>')
                

# Create a home request handler just that you don't have to enter the urls manually.
class Home(webapp2.RequestHandler):
    def get(self):
        context = {'thing':1}
        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.write(template.render(context))
        

# Create routes.
ROUTES = [webapp2.Route(r'/login/<:.*>', Login, handler_method='any'),
          webapp2.Route(r'/finished/<:.*>', Politics),
          webapp2.Route(r'/nextStep/', NextStep),
          webapp2.Route(r'/nextStep', NextStep),
          webapp2.Route(r'/addArticle/', AddArticle),
          webapp2.Route(r'/addArticle', AddArticle),
          webapp2.Route(r'/viewArticles/', ViewArticles),
          webapp2.Route(r'/viewArticles', ViewArticles),
          webapp2.Route(r'/extensionConnection/<:.*>', ExtensionConnection),
          webapp2.Route(r'/', Home)]

# Instantiate the webapp2 WSGI application.
config1 = {}
config1['webapp2_extras.sessions'] = {
    'secret_key': THIS_SECRET,
}
app = webapp2.WSGIApplication(ROUTES, debug=True, config=config1)