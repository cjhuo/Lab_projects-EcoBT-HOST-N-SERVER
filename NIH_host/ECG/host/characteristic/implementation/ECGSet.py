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

import threading
import time

from Characteristic import *

startFlag = 0x01
stopFlag = 0x00
readFromCardFlag = 0x11


class ECGSet(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 2
    
    def setRole(self):
        self.service.setter = self
        
    def process(self):
        self.recorded = False
        #print self.instance._.value
        value = self.instance._.value
        (start,) = struct.unpack("@B", value)
        #val = binascii.hexlify(start)
        print start
        
        if start == stopFlag and self.recorded == False:
            # send UI a 'ready' signal
            data = {'type': 'ECG',
                    'value': {'type': 'state',
                              'value': 0 # stopped == ready signal
                              }
                    }
            self.peripheralWorker.peripheral.type = 'ECG'
            self.peripheralWorker.delegateWorker.getQueue().put(data)
            '''
            if not hasattr(self.service, 'record_cnt'):
                NSLog("START ECG RECORD")
                self.peripheralWorker.writeValueForCharacteristic(self.createStartFlag(), self)
            '''
        if start == startFlag:
            # stop recording first
            # read ecg from sd card then
            NSLog("STOP RECORDING IN 10 SECONDS")
            self.service.record_cnt = 1
            #de = DelayExecutor(10, self.peripheralWorker.writeValueForCharacteristic, # memory leak reported from objc
            #               self.createStopFlag(), self.createReadFromCardFlag(), self.instance)
            time.sleep(1)
            self.peripheralWorker.writeValueForCharacteristic(self.createStopFlag(), self)
            self.peripheralWorker.writeValueForCharacteristic(self.createReadFromCardFlag(), self)
            self.recorded = True # set to true so that it won't be recorded automatically again, waiting for UI to send command
           
        elif start == readFromCardFlag or start == 62 or start == 63:
            NSLog("START READING FROM CARD, RECEIVING...")   
            # start reading data, expect to see 'FEC6' and 'FEC7'
            # do nothing further, maybe can throw a message to UI said I am reading?    
        else:
            # stop and restart
            NSLog("INVALID STATUS FOUND...")
            #self.peripheralWorker.writeValueForCharacteristic(self.createStopFlag(), self)  
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
        self.setDaemon(1)
    def run(self):
        time.sleep(self.sleep)
        self.func(self.param1, self.param3)
        self.func(self.param2, self.param3)
    