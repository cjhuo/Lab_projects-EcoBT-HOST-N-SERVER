'''
Created on Feb 9, 2013

@author: cjhuo
'''
from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *

import array
import binascii
import binascii
import struct
import array

from Characteristic import *

startFlag = 0x01
stopFlag = 0x00
readFromCardFlag = 0x11


class ECGSet(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 2
        
    def process(self):
        #print self.instance._.value
        value = self.instance._.value
        (start,) = struct.unpack("@B", value)
        #val = binascii.hexlify(start)
        print 'value is : ', start
        if start == stopFlag:
            print "START ECG RECORD"
            self.peripheralWorker.writeValueForCharacteristic(self.createStartFlag(), self)
        if start == startFlag:
            # stop recording first
            # read ecg from sd card then
            print "stop recording in 10 seconds"
            DelayExecutor(10, self.peripheralWorker.writeValueForCharacteristic,
                           self.createStopFlag(), self.createReadFromCardFlag(), self.instance).start()
            
        if start == readFromCardFlag:

            # start reading data, expect to see 'FEC6' and 'FEC7'
            # do nothing further, maybe can throw a message to UI said I am reading? 
            pass      
        
        # TBD
        
    def createStartFlag(self):
        return self.createFlag(startFlag)
        
    def createStopFlag(self):
        return self.createFlag(stopFlag)
    
    def createReadFromCardFlag(self):
        return self.createFlag(readFromCardFlag)
        
    def createFlag(self, flag):
        data = struct.pack("@B", flag)
        val_data = NSData.dataWithBytes_length_(data, len(data))     
        return val_data
    
import threading
import time

# only can functions with 2 argument...
class DelayExecutor(threading.Thread):
    def __init__(self,sleep,func, param1, param2, param3):
        """ execute func(params) after 'sleep' seconds """
        self.func = func
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3
        self.sleep = sleep
        threading.Thread.__init__(self,name = "DelayExecutor")
        print 'init'
        self.setDaemon(1)
    def run(self):
        time.sleep(self.sleep)
        print 'writing'
        self.func(self.param1, self.param3)
        self.func(self.param2, self.param3)
    