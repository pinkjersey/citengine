'''
Created on Jul 7, 2012

@author: omx
'''
from google.appengine.ext import ndb



class Book(ndb.Model):
    isbn = ndb.StringProperty()
    name = ndb.StringProperty(required=True)
    priority = ndb.FloatProperty(indexed=True)
    image = ndb.StringProperty(default="")
    lastModified = ndb.DateTimeProperty(auto_now=True)
    citlembikNo = ndb.IntegerProperty()
    pageLink = ndb.StringProperty(default="")
    featured = ndb.BooleanProperty(default=False)
