'''
Created on Nov 14, 2012

@author: cjhuo
'''

import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.options
import os.path
import threading

from EcoBTWorker import EcoBTWorker
from EcoBTApp import EcoBTApp

from tornado.options import define, options
define("port", default=8001, help="run on the given port", type=int)
global worker

class Application(tornado.web.Application):
    def __init__(self):
        worker = EcoBTWorker()
        worker.start()
        handlers = [
            (r"/socket", EcoBTWebSocket, dict(worker = worker))
        ]
        settings = dict(
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        
        print 'test'
        
class EcoBTWebSocket(tornado.websocket.WebSocketHandler):
    def initialize(self, worker):
        self.worker = worker                   
        
    def open(self):
        self.worker.getGlobalSockets().append(self)
        print "WebSocket opened"

    def on_close(self):
        self.worker.getGlobalSockets().remove(self)
        print "WebSocket closed"
        
if __name__ == "__main__":
    print "Running on localhost:8001"
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    
    #open a browser for the web interface
    #webbrowser.open_new('http://localhost:8000/')
    
    #start web server
    t = threading.Thread(target = tornado.ioloop.IOLoop.instance().start)
    #t.daemon = True
    t.start()
    app = EcoBTApp(worker)
