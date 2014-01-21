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
    container = tornado.wsgi.WSGIContainer(application)
    http_server = tornado.httpserver.HTTPServer(container)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()