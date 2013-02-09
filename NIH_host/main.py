import tornado.httpserver
import tornado.ioloop
import tornado.options


import sys
import webbrowser

from webEngine.config import *
from webEngine.webApp import *

#sys.dont_write_bytecode = True

from tornado.options import define, options
#define("port", default=webGUIPort, help="run on the given port", type=int)


        
def writeToLog(flag):
    if flag == True:
        logFile = open('log.txt','a+', 0)
        stdOut = sys.stdout
        stdErr = sys.stderr
        sys.stdout = logFile
        sys.stderr = logFile
        
if __name__ == "__main__":
    
    writeToLog(isWriteToLog)
    
    print "Running on localhost:", webGUIPort
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(webGUIPort)
    
    #open a browser for the web interface
    #webbrowser.open_new('http://localhost:8000/')
    
    #start web server
    tornado.ioloop.IOLoop.instance().start()
    
    '''
    sys.stdout = stdOut
    sys.stderr = stdErr
    '''
