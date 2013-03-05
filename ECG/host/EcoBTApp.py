import sys
sys.dont_write_bytecode = True

from Foundation import * 
from objc import *
import threading

from EcoBTCentralManagerWorker import EcoBTCentralManagerWorker
from threading import Event
from Sockets import Sockets



class EcoBTApp(object):

    def __init__(self, enableKeyboardInterrupt):
        #initialize CMManagerWorker
        self.managerWorker = EcoBTCentralManagerWorker.alloc().init()  
        self.enableKeyboardInterrupt = enableKeyboardInterrupt 
        #self.managerWorker.setSockets(sockets)
        
    def setSockets(self, sockets):
        self.managerWorker.setSockets(sockets)
        
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


if __name__ == '__main__':
    #main()

    app = EcoBTApp(True)
    app.setSockets(Sockets())
    app.start()


