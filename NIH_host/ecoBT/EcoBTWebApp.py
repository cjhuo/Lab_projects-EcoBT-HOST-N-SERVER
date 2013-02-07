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

from EcoBTApp import EcoBTApp

import sys
sys.dont_write_bytecode = True
from tornado.options import define, options
define("port", default=8001, help="run on the given port", type=int)


class Sockets(object):
    def __init__(self):
        self.sockets = []
        
    def append(self, socket):
        self.sockets.append(socket)
        
    def remove(self, socket):
        self.sockets.remove(socket)
    
    def __len__(self):
        return len(self.sockets)
        

class Application(tornado.web.Application):
    def __init__(self):
        self.globalSockets = Sockets()
        handlers = [
            (r"/socket", EcoBTWebSocket, dict(globalSockets = self.globalSockets))
        ]
        settings = dict(
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        
        
class EcoBTWebSocket(tornado.websocket.WebSocketHandler):
    def initialize(self, globalSockets):
        self.globalSockets = globalSockets                   
        
    def open(self):
        self.globalSockets.append(self)
        print "WebSocket opened"

    def on_close(self):
        self.globalSockets.remove(self)
        print "WebSocket closed"
        
if __name__ == "__main__":
    '''
    logFile = open('EcoBTlog.txt','a+', 0)
    stdOut = sys.stdout
    stdErr = sys.stderr
    sys.stdout = logFile
    sys.stderr = logFile
    '''
    print "Running on localhost:8001"
    tornado.options.parse_command_line()
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    
    #open a browser for the web interface
    #webbrowser.open_new('http://localhost:8000/')
    
    #start web server
    t = threading.Thread(target = tornado.ioloop.IOLoop.instance().start)
    t.setDaemon(True)
    #t.daemon = True
    t.start()
    ecoBTApp = EcoBTApp(app.globalSockets)
    
    '''    
    sys.stdout = stdOut
    sys.stderr = stdErr
    '''