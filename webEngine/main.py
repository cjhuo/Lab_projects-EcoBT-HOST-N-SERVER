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
    
    print "Running on localhost:", webGUIPort
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
    '''
    # test websockets
    from characteristic.implementation.misc.PeriodicExecutor import PeriodicExecutor
    test = PeriodicExecutor()
    test.setParams(2, sendFakeData, app.globalSockets, 'Demo')
    test.start()
    '''

    #t.daemon = True
    t.start()
    ecoBTApp.start()
    
    
    #open a browser for the web interface
    #webbrowser.open_new('http://localhost:8000/')
    
    #start web server
    
def sendFakeData(sockets, address):
    data = dict()
    data['address'] = address
    data['type'] = 'SIDsRead'
    data['value'] = [1,2,3,4,5,6,7,8,9,10]
    packet = {'from': 'node', 'data': data}
    if len(sockets) != 0:
        for socket in sockets.sockets:
            socket.write_message(packet) 
    
def writeToLog(flag):
    if flag == True:
        logFile = open('log.txt','a+', 0)
        stdOut = sys.stdout
        stdErr = sys.stderr
        sys.stdout = logFile
        sys.stderr = logFile
        
if __name__ == "__main__":
    main()

