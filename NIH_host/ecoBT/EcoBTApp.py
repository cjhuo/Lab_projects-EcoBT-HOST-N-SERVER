from Foundation import * 
from objc import *
import threading

from EcoBTCentralManagerWorker import EcoBTCentralManagerWorker
from threading import Event

class EcoBTApp(NSObject):

    def init(self):       
        # initialize NSAutoreleasePool
        self.pool = NSAutoreleasePool.alloc().init()
        
        #initialize CMManagerWorker
        self.managerWorker = EcoBTCentralManagerWorker.alloc().init()    
        
        # handle keyboard interrupt. Hit "Enter" to exit the program
        stdIn = NSFileHandle.fileHandleWithStandardInput().retain()
        s = objc.selector(self.handler,signature='v@:')
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_\
                        (self, s, NSFileHandleReadCompletionNotification, stdIn)
        #self.manager.setSocket(self.sockets)
        self.runLoop = NSRunLoop.currentRunLoop()
        self.running = Event()
        stdIn.readInBackgroundAndNotify()
        
        # run NSRunLoop infinitely
        while (not self.running.isSet()) and self.runLoop.runMode_beforeDate_(NSDefaultRunLoopMode, NSDate.distantFuture()):
            pass # do nothing
        
        self.managerWorker.stop()
        print 'Program Terminated'

        del self.pool
        
    def handler(self):
        self.running.set()


if __name__ == '__main__':
    #main()

    EcoBTApp.alloc().init()


