import sys
sys.dont_write_bytecode = True

import tornado.httpserver
import tornado.ioloop
import tornado.options

import webbrowser

from config import *
from webApp import *

from tornado.options import define, options
#define("port", default=webGUIPort, help="run on the given port", type=int)

def main():
    writeToLog(isWriteToLog)
    
    print "Running on localhost:", webGUIPort
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(webGUIPort)
    
    #open a browser for the web interface
    #webbrowser.open_new('http://localhost:8000/')
    
    #start web server
    
    '''
    sys.stdout = stdOut
    sys.stderr = stdErr
    '''
    
        
def writeToLog(flag):
    if flag == True:
        logFile = open('log.txt','a+', 0)
        stdOut = sys.stdout
        stdErr = sys.stderr
        sys.stdout = logFile
        sys.stderr = logFile
        
if __name__ == "__main__":
    main()
    tornado.ioloop.IOLoop.instance().start()

