import sys
sys.dont_write_bytecode = True

import tornado.httpserver
import tornado.ioloop
import tornado.options

import threading
import webbrowser

from config import *
from webApp import *
from host.EcoBTApp import EcoBTApp

from tornado.options import define, options
#define("port", default=webGUIPort, help="run on the given port", type=int)

def main():
    writeToLog(isWriteToLog)
    
    ecoBTApp = EcoBTApp(enableKeyboardInterrupt)
    tornado.options.parse_command_line()
    app = Application(ecoBTApp)
    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(webGUIPort)
    
    ecoBTApp.setSockets(app.globalSockets)
    
    #open a browser for the web interface
    #webbrowser.open_new('http://localhost:8000/')
    
    #start web server
    t = threading.Thread(target = tornado.ioloop.IOLoop.instance().start)
    t.setDaemon(True)
    #t.daemon = True
    t.start()
    print "Running on localhost: %s" % webGUIPort
    print "Self IP Addres: %s" % ipAddr
    ecoBTApp.start()
    
    
    #open a browser for the web interface
    #webbrowser.open_new('http://localhost:8000/')
    
    #start web server
import logging    
def writeToLog(flag):
    class LogFile(object):
        """File-like object to log text using the `logging` module."""
    
        def __init__(self, name=None):
            self.logger = logging.getLogger(name)
            self.msg = ''
            #self.formatStdoutLog(name)
    
        def write(self, msg, level=logging.INFO):
            if msg != '\n': # keep information until hit line return mark
                self.msg += msg
            else:
                self.logger.log(level, self.msg)
                self.msg = ''
    
        def flush(self):
            for handler in self.logger.handlers:
                handler.flush()
                
        def formatStdoutLog(self, name):
            tornado.log.enable_pretty_logging(logger=logging.getLogger(name))

                
    if flag == True:
        tornado.options.options.log_file_prefix = "log.txt"
        tornado.options.options.log_to_stderr = False
        
        sys.stdout = LogFile('stdout')
        sys.stderr = LogFile('stderr')
        '''
        logFile = open('log.txt','a+', 0)
        stdOut = sys.stdout
        stdErr = sys.stderr
        sys.stdout = logFile
        sys.stderr = logFile
        '''
        
    
if __name__ == "__main__":
    main()

