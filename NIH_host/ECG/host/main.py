'''
Created on Nov 14, 2012

@author: cjhuo
'''
import sys
sys.dont_write_bytecode = True

import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.options
import os.path
import threading

from config import *

from EcoBTApp import EcoBTApp
from Sockets import Sockets
from EcoBTWebSocket import EcoBTWebSocket
from webHandlers import ECGHandler

from tornado.options import define, options
define("port", default=hostPort, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self, ecoBTApp):
        self.globalSockets = Sockets()
        self.ecoBTApp = ecoBTApp
        handlers = [
            (r"/socket", EcoBTWebSocket, dict(globalSockets = self.globalSockets, 
                                              ecoBTApp = self.ecoBTApp)),
            (r"/ecgHandler", ECGHandler, dict(ecoBTApp = self.ecoBTApp))
        ]
        settings = dict(
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)
    
    def setEcoBTApp(self, app):
        self.EcoBTApp = app 
        
        
def main():
    '''
    logFile = open('EcoBTlog.txt','a+', 0)
    stdOut = sys.stdout
    stdErr = sys.stderr
    sys.stdout = logFile
    sys.stderr = logFile
    '''
    ecoBTApp = EcoBTApp(enableKeyboardInterrupt)
    
    print "Running on localhost:8001"
    tornado.options.parse_command_line()
    app = Application(ecoBTApp)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    
    ecoBTApp.setSockets(app.globalSockets)
    
    #open a browser for the web interface
    #webbrowser.open_new('http://localhost:8000/')
    
    #start web server
    t = threading.Thread(target = tornado.ioloop.IOLoop.instance().start)
    t.setDaemon(True)
    #t.daemon = True
    t.start()
    ecoBTApp.start()
    
    '''    
    sys.stdout = stdOut
    sys.stderr = stdErr
    '''
    
if __name__ == "__main__":
    main()
