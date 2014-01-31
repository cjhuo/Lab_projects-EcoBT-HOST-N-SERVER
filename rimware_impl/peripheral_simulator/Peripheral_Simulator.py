'''
Created on Jan 20, 2014

@author: cjhuo
'''

import sys
sys.dont_write_bytecode = True

from Foundation import * 
from objc import *
from threading import Event

from PeripheralManager import PeripheralManagerWorker


class Peripheral_Simulator(object):
    
    def __init__(self, enableKeyboardInterrupt):
        self.peripheralManagerWorker = PeripheralManagerWorker.alloc().init()
        self.enableKeyboardInterrupt = enableKeyboardInterrupt 

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
            print >> sys.stderr, 'Exception caught found in Simulator_MAIN'
            
        self.peripheralManagerWorker.stop()
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


# testing
if __name__ == "__main__":
    app = Simulator_MAIN(True)
    app.start()