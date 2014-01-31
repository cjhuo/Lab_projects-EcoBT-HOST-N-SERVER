from ladon.server.wsgi import LadonWSGIApplication

import tornado.httpserver
import tornado.wsgi
import tornado.autoreload
from os.path import abspath,dirname

from CentralServerApp import CentralServerApp

application = LadonWSGIApplication(
    ['Services'],
    [dirname(abspath(__file__))],
    catalog_name='My Ladon webservice catalog',
    catalog_desc='This is the root of my cool webservice catalog')


if __name__ == "__main__":
    app = CentralServerApp()
    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(8881)
    
    container = tornado.wsgi.WSGIContainer(application)
    http_server = tornado.httpserver.HTTPServer(container)
    http_server.listen(8880)    

    ioloop = tornado.ioloop.IOLoop.instance()
    '''
    following handle autoreload for WSGI which by default doesn't
    work on WSGI and GoogleApp. 
    Idea borrowed from http://kevbradwick.wordpress.com/
    2011/10/15/getting-python-tornado-web-autoreload-to-work/
    This feature is suitable for realizing dynamically 
    add/remove
    '''    
    tornado.autoreload.start(ioloop)
    ioloop.start()