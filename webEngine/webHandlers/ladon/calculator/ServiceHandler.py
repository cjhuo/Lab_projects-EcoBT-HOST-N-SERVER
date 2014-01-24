'''
Created on Jan 21, 2014

@author: cjhuo
'''

from ladon.server.wsgi import LadonWSGIApplication
from os.path import abspath,dirname


application = LadonWSGIApplication(
    ['Calculator'],
    [dirname(abspath(__file__))],
    catalog_name='My Ladon webservice catalog',
    catalog_desc='This is the root of my cool webservice catalog')

def simple_app(environ, start_response):
    status = "200 OK"
    response_headers = [("Content-type", "text/plain")]
    start_response(status, response_headers)
    return ["Hello world!\n"]


# test cases
if __name__ == "__main__":
    import tornado.httpserver
    import tornado.wsgi
    import tornado.autoreload
    container = tornado.wsgi.WSGIContainer(application)
    http_server = tornado.httpserver.HTTPServer(container)
    http_server.listen(8888)
    '''
    following handle autoreload for WSGI which by default doesn't
    work on WSGI and GoogleApp. 
    Idea borrowed from http://kevbradwick.wordpress.com/
    2011/10/15/getting-python-tornado-web-autoreload-to-work/
    This feature is suitable for realizing dynamically 
    add/remove
    '''
    ioloop = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.start(ioloop)
    ioloop.start()
    