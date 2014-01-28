import sys
sys.dont_write_bytecode = True

from Foundation import * 
from objc import *
import threading, json
from config_gateway import *

from GWManager import GWManager
from threading import Event

class GatewayApp(object):

    def __init__(self, enableKeyboardInterrupt):
        #initialize CMManagerWorker
        self.managerWorker = GWManager.alloc().init()  
        self.enableKeyboardInterrupt = enableKeyboardInterrupt 
        self.connection2Gateway = Connection2Gateway(self.managerWorker)
        self.managerWorker.setConnection2Central(self.connection2Gateway)
                
    def start(self):
        # initialize NSAutoreleasePool
        self.pool = NSAutoreleasePool.alloc().init()
        if self.enableKeyboardInterrupt != False:
            self.handleKeyboardInterrupt()
        self.running = Event()
        self.runLoop = NSRunLoop.currentRunLoop()
        try:
            # run NSRunLoop infinitely
            while (not self.running.isSet()) and self.runLoop.runMode_beforeDate_(NSDefaultRunLoopMode, NSDate.distantFuture()):
                # do nothing
                pass
        except:
            print >> sys.stderr, 'Exception caught found in EcoBTApp'
         
        # clean up       
        self.managerWorker.stop()
        self.connection2Gateway.close()
        NSLog("Program Terminated")
        del self.pool
                               
    def handleKeyboardInterrupt(self):
        # handle keyboard interrupt. Hit "Enter" to exit the program
        stdIn = NSFileHandle.fileHandleWithStandardInput().retain()
        
        # magic letters 'v@:@': void return, instance method, has 1 object argument.
        s = objc.selector(self.keyboardHandler_,signature='v@:@') 
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_\
                        (self, s, NSFileHandleReadCompletionNotification, stdIn)


        stdIn.readInBackgroundAndNotify()
       
    def keyboardHandler_(self, notification): # handlder must has a function name ended by a single "_"        
        NSLog("Keyboard Interrupt Captured")
        self.running.set()
        '''
        data = notification.userInfo().objectForKey_(NSFileHandleNotificationDataItem)
        string = NSString.alloc().initWithData_encoding_(data, NSUTF8StringEncoding).autorelease()
        NSLog("Got string: %@", string)
        print str(string)
        
        # stop NSRunLoop
        if(string == 'stop\n'): 
            self.running.set()
        else:
            stdIn = NSFileHandle.fileHandleWithStandardInput().retain()
            stdIn.readInBackgroundAndNotify()
            #self.handleKeyboardInterrupt()
        '''
from ws4py.client.threadedclient import WebSocketClient
import time
class Connection2Gateway(object):
    def __init__(self, peripheralWoker, connectionType='WebSocket'):
        self.peripheralWorker = peripheralWoker
        self.connection = None
        self.connectionType = connectionType
        self.connect(self.connectionType)      
        
    def connect(self, connectionType):    
        if connectionType == 'WebSocket':
            success = False
            while not success:
                try:
                    self.connection = WebSocketConnection('ws://localhost:8888/socket', protocols=['http-only', 'chat'])
                    self.connection.setOwner(self)
                    self.connection.connect()
                    success = True
                except:
                    print '\nConnection to gateway refused\nTry again in ', GATEWAY_RECONNECT_WAIT_INTERVAL, ' seconds'
                    for i in range(GATEWAY_RECONNECT_WAIT_INTERVAL, 0, -1):
                        time.sleep(1)
                        if i !=0:
                            print i,
                        else:
                            print i
        else: # no other connection type implemented yet
            pass
    def reconnect(self):
        # wait a moment for reconnection
        print '\nConnection to gateway refused\nTry again in ', GATEWAY_RECONNECT_WAIT_INTERVAL, ' seconds'
        for i in range(GATEWAY_RECONNECT_WAIT_INTERVAL, 0, -1):
            time.sleep(1)
            if i !=0:
                print i,
            else:
                print i
        
        self.connect(self.connectionType)
    
    def send(self, message):
        self.connection.send(message)
    
    def close(self):
        self.connection.close()
        
    def handleIcomingRequest(self, message):
        self.peripheralWorker.handleRequestFromCentral(message)

    
class WebSocketConnection(WebSocketClient):
    def setOwner(self, owner):
        self.owner = owner
        
    def opened(self):
        print 'Connection opened'    

    def closed(self, code, reason):
        print(("Closed down", code, reason))
        # try to connect back
        self.owner.reconnect()

    def received_message(self, message):
        print("=> %d %s" % (len(message), str(message)))       
        request = json.loads(str(message))

        self.owner.handleIcomingRequest(request)    
        
if __name__ == '__main__':
    #main()
    app = GatewayApp(True)
    app.start()


