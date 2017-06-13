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
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from book_model import Book
from time import mktime

def InputToBook(book, data):
    book.name = cgi.escape(data['name'])
    book.isbn = cgi.escape(data['isbn'])
    book.priority = data['priority']
    book.image = cgi.escape(data['image'])
    book.pageLink = cgi.escape(data['pageLink'])
    book.featured = data['featured']


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)

class UploadFormHandler(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/books/upload_json')
        self.response.out.write('<html><body>')
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write('''Upload File: <input type="file" name="file"><br> <input type="submit" name="submit" value="Upload"> </form></body></html>''')
        


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload = self.get_uploads()[0]
        upload_key = upload.key()
        blob_reader = blobstore.BlobReader(upload_key)
        jsonstring = blob_reader.read()
        
        books = json.loads(jsonstring)
        for book in books:
            b = Book(name=book["bookname"], isbn=book["isbn"])
            b.put()
                     
        memcache.delete('books')
        
        blob_info = blobstore.BlobInfo.get(upload_key)
        blob_info.delete()
        self.redirect('/books.html')
        

class BookHandler(webapp2.RequestHandler):
    def put(self, key):
        content = self.request.body
        if (content == ''):
            logging.error('content not set')
            return
        
        data = json.loads(content)
        book_key = ndb.Key(urlsafe=key)
        book = book_key.get()
        InputToBook(book, data)
        book_key = book.put()
        memcache.delete('books')
        self.get(book_key.urlsafe())

    def delete(self, key):
        book_key = ndb.Key(urlsafe=key)
        book_key.delete()
        memcache.delete('books')

    def get(self, key):
        content = self.request.body
        if (content == ''):
            logging.error('content not set')
            return
        
        data = json.loads(content)
        book_key = ndb.Key(urlsafe=key)
        book = book_key.get()
        det = book.to_dict()
        det['key'] = book.key.urlsafe()
        jsonstr = json.dumps(det, ensure_ascii=False, cls = MyEncoder).encode('utf8')
        self.response.headers['Access-Control-Allow-Origin'] = "*"
        self.response.headers['Content-Type'] = "application/json; charset=UTF-8"
        self.response.write(jsonstr)

class MainHandler(webapp2.RequestHandler):
    def post(self):
        content = self.request.body
        if (content == ''):
            logging.error('content not set')
            return

        data = json.loads(content)
        newBook = Book()
        InputToBook(newBook, data)
        newBook.put()
        memcache.delete('books')
        det = newBook.to_dict()
        det['key'] = newBook.key.urlsafe()
        jsonstr = json.dumps(det, ensure_ascii=False, cls=MyEncoder).encode('utf8')
        self.response.headers['Access-Control-Allow-Origin'] = "*"
        self.response.headers['Content-Type'] = "application/json; charset=UTF-8"
        self.response.write(jsonstr)


    def get(self):
        bookList = []
        for b in Book.query().fetch():
            if b.priority == None:
                b.priority = 0.1
                b.put()

            det = b.to_dict()
            det['key'] = b.key.urlsafe()
            bookList.append(det)
        
        
        jsonstr = json.dumps(bookList, ensure_ascii=False, cls=MyEncoder).encode('utf8')
        self.response.headers['Access-Control-Allow-Origin'] = "*"
        self.response.headers['Content-Type'] = "application/json; charset=UTF-8"
        self.response.write(jsonstr)

app = webapp2.WSGIApplication([
        (r'/books', MainHandler),
        (r'/books/upload', UploadFormHandler),
        (r'/books/upload_json', UploadHandler),
        (r'/books/(.+)', BookHandler),
        ], debug=True)

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    webapp.util.run_wsgi_app(app)

if __name__ == '__main__':
    main()
