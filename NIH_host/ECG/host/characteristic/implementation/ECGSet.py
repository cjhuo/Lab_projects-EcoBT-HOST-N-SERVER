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
import struct
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
        self.service.sampleRecorded = False # create a flag to indicate the samples hasn't been recorded
        self.service.startState = 0 # 0: just initialized; 1: has checked any status
        
    def process(self):
        #print self.instance._.value
        value = self.instance._.value
        (start,) = struct.unpack("@B", value)
        #val = binascii.hexlify(start)
        print 'FEC5 value: ', start
        
        if start == stopFlag: # idle, ready to record          
            # send UI a 'ready' signal
            data = {'type': 'ECG',
                    'value': {'type': 'state',
                              'value': 0 # stopped == ready signal
                              }
                    }
            self.peripheralWorker.peripheral.type = 'ECG'
            self.peripheralWorker.delegateWorker.getQueue().put(data)
            self.service.startState = 1
            '''
            if not hasattr(self.service, 'record_cnt'):
                NSLog("START ECG RECORD")
                self.peripheralWorker.writeValueForCharacteristic(self.createStartFlag(), self)
            '''
        elif start == startFlag:
            # check if the node's beginning state is start, if yes, then invalid, stop it, toggle beginning state
            if self.service.startState == 0:
                NSLog("RESETTING NODE TO READY")
                self.peripheralWorker.writeValueForCharacteristic(self.createStopFlag(), self)
                self.service.startState = 1
            elif not self.service.sampleRecorded: # has not recorded 10 second samples  
                # stop recording first
                # read ecg from sd card then
                NSLog("STOP RECORDING IN 12 SECONDS")
                self.service.record_cnt = 1          
                #de = DelayExecutor(10, self.peripheralWorker.writeValueForCharacteristic, # memory leak reported from objc
                #               self.createStopFlag(), self.createReadFromCardFlag(), self.instance)
                time.sleep(12)
                NSLog("SENDING STOP RECORDING SIGNAL")      
                self.peripheralWorker.writeValueForCharacteristic(self.createStopFlag(), self) 
                time.sleep(5)
                NSLog("SENDING START READ SIGNAL")
                self.peripheralWorker.writeValueForCharacteristic(self.createReadFromCardFlag(), self)
                #self.recorded = True # set to true so that it won't be recorded automatically again, waiting for UI to send command
            elif self.service.sampleRecorded == True: # sample recorded, start real recording!!!!
                NSLog("START REAL RECORDING")
                self.service.record_cnt = 1        
        elif start == readFromCardFlag or start == 62 or start == 63:
            if self.service.startState == 0:
                NSLog("RESETTING NODE TO READY")
                self.peripheralWorker.writeValueForCharacteristic(self.createStopFlag(), self)
                self.service.startState = 1
            else:
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



    