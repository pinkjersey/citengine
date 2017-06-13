#!/usr/bin/env python

import webapp2
import urllib2
import json
import os
import cgi
import logging
import datetime

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import webapp
from book_model import Book
from time import mktime

query_opts = {}

class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        jsonstr = memcache.get('books')
        if jsonstr is None:
            bookList = []
            q = Book.query().order(-Book.priority).order(Book.name)
            q_iter = q.iter(**query_opts)
            for b in q_iter:
                det = b.to_dict()
                bookList.append(det)
                           
            jsonstr = json.dumps(bookList, ensure_ascii=False, cls=MyEncoder).encode('utf8')
            memcache.add('books', jsonstr)

        self.response.headers['Access-Control-Allow-Origin'] = "*"
        self.response.headers['Content-Type'] = "application/json; charset=UTF-8"
        self.response.write(jsonstr)

app = webapp2.WSGIApplication([
        (r'/', MainHandler)
        ], debug=True)

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    webapp.util.run_wsgi_app(app)

if __name__ == '__main__':
    main()
