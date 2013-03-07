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
import threading


from Characteristic import *

startFlag = 0x01
stopFlag = 0x00
readFromCardFlag = 0x11

        
stateRef =  "State machine specifically for ECG's\n\
            0: has just started,\n\
            1: start signal sent\n\
            2: start signal received\n\
            3: stop signal sent\n\
            4: stop signal received\n\
            5: readFromCard signal sent\n\
            6: readFromCard signal received\n\
            will never wait to send signal stop, but wait for send others"



class ECGSet(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 2

    def setRole(self):
        self.service.setter = self
        self.service.sampleRecorded = False # create a flag to indicate the samples hasn't been recorded
        #self.service.startState = 0 # 0: just initialized; 1: has checked any status
        self.service.state = 0
        self.lock = threading.Condition();
        
    def process(self):
        self.lock.acquire()
        #print self.instance._.value
        value = self.instance._.value
        (start,) = struct.unpack("@B", value)
        #val = binascii.hexlify(start)
        print 'FEC5 value: ', start

        if start == stopFlag: # idle, ready to record   
            # if there is a job in queue, processQueue
            if self.service.state == 0 or self.service.state == 3 or self.service.state == 4:
                if len(self.service.delayQueue) != 0:
                    self.processQueue()       
                else:
                    # send UI a 'ready' signal
                    data = {'type': 'ECG',
                            'value': {'type': 'state',
                                      'value': 0 # stopped == ready signal
                                      }
                            }
                    self.peripheralWorker.peripheral.type = 'ECG'
                    self.peripheralWorker.delegateWorker.getQueue().put(data)
                    self.service.state = 4
                    '''
                    if not hasattr(self.service, 'record_cnt'):
                        NSLog("START ECG RECORD")
                        self.peripheralWorker.writeValueForCharacteristic(self.createStartFlag(), self)
                    '''
            else: 
                #self.service.state = 4
                #if len(self.service.delayQueue) != 0:
                #    self.processQueue()
                NSLog("OUT OF SEQUENCE!!!")
                self.tryToSaveStateByResend()
        # check if the node's beginning state is start, if yes, then invalid, stop it, toggle beginning state
        elif self.service.state == 0: # need reseting
            NSLog("RESETING...")
            self.service.state = 3       
            self.peripheralWorker.writeValueForCharacteristic(self.createStopFlag(), self)
            self.lock.release()
            return     
        elif start == startFlag:
            if self.service.state == 1 or self.service.state == 2:
                if not self.service.sampleRecorded: # has not recorded 10 second samples  
                    # stop recording first
                    # read ecg from sd card then
                    NSLog("STOP RECORDING IN 12 SECONDS")
                    self.service.record_cnt = 1          
                    #de = DelayExecutor(10, self.peripheralWorker.writeValueForCharacteristic, # memory leak reported from objc
                    #               self.createStopFlag(), self.createReadFromCardFlag(), self.instance)                
                    NSLog("PUTTING READ RECORDING SIGNAL TO DELAY QUEUE")
                    self.service.PushToDelayQueue('ReadStart') 
                    # place of sleep in critical!!! has to be right before sending stop       
                    self.service.state = 3
                    time.sleep(12) 
                    NSLog("SENDING STOP RECORDING SIGNAL")             
                    self.peripheralWorker.writeValueForCharacteristic(self.createStopFlag(), self) 
                    #self.recorded = True # set to true so that it won't be recorded automatically again, waiting for UI to send command
                elif self.service.sampleRecorded == True: # sample recorded, start real recording!!!!
                    NSLog("START REAL RECORDING")
                    self.service.record_cnt = 1        
                    self.service.state = 2
            else:
                NSLog("OUT OF SEQUENCE!!!")
                self.tryToSaveStateByResend()
        elif start == readFromCardFlag or start == 62 or start == 63:
            if self.service.state == 5 or self.service.state == 6:
                self.service.state = 6
                NSLog("START READING FROM CARD, RECEIVING...")   
                # start reading data, expect to see 'FEC6' and 'FEC7'
                # do nothing further, maybe can throw a message to UI said I am reading? 
            else:
                NSLog("OUT OF SEQUENCE!!!")   
                self.tryToSaveStateByResend()
        else:
            # stop and restart
            NSLog("INVALID STATUS FOUND...")
            #self.peripheralWorker.writeValueForCharacteristic(self.createStopFlag(), self)  
            
        print "ECG service's state: ", self.service.state
        print stateRef
        self.lock.release()
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
    
    def tryToSaveStateByResend(self):
        self.lock.acquire()
        NSLog("TRYING TO RESEND SIGNAL TO SAVE THE STATE MACHINE...")
        #time.sleep(5)
        if self.service.state == 1:
            self.peripheralWorker.writeValueForCharacteristic(self.createStartFlag(), self)
        elif self.service.state == 3:
            self.peripheralWorker.writeValueForCharacteristic(self.createStopFlag(), self)
        elif self.service.state == 5:
            self.peripheralWorker.writeValueForCharacteristic(self.createReadFromCardFlag(), self)
            self.lock.release()

            
    def processQueue(self):
        self.lock.acquire()
        job = self.service.delayQueue.pop(0)
        if job == 'WriteStart':
            NSLog("SENDING DELAYED START RECORDING SIGNAL")
            self.service.state = 1
            self.peripheralWorker.writeValueForCharacteristic(self.createStartFlag(), self)
        if job == 'ReadStart':
            NSLog("SENDING DELAYED READ RECORDING SIGNAL")
            self.service.state = 5
            self.peripheralWorker.writeValueForCharacteristic(self.createReadFromCardFlag(), self)
        self.lock.release()

    def startECG(self):
        self.lock.acquire()
        # clear delay Queue
        self.service.delayQueue = []
        # not creating a flag to indicate the samples hasn't been recorded 
        if self.service.state == 0 or self.service.state == 4:  
            NSLog("SENDING START REAL RECORDING SIGNAL")
            self.service.state = 1
            self.peripheralWorker.writeValueForCharacteristic(self.createStartFlag(), self)
        elif self.service.state == 3:
            NSLog("PUTTING START REAL RECORDING SIGNAL TO DELAY QUEUE")
            self.service.PushToDelayQueue('WriteStart')            
        else:
            NSLog("PUTTING START REAL RECORDING SIGNAL TO DELAY QUEUE")
            self.service.state = 3 # stop signal sent
            self.service.PushToDelayQueue('WriteStart')
            self.peripheralWorker.writeValueForCharacteristic(self.createStopFlag(), self)
            #self.peripheralWorker.writeValueForCharacteristic(self.createStartFlag(), self)
        self.lock.release()

    def stopECG(self):
        self.lock.acquire()
        # clear delay Queue
        self.service.delayQueue = []        
        if self.service.state != 0 or self.service.state != 4:
            NSLog("SENDING STOP REAL RECORDING SIGNAL")
            self.service.state = 3
            self.peripheralWorker.writeValueForCharacteristic(self.createStopFlag(), self)
        self.lock.release()
        
    '''                            
    def readECGData(self):
        NSLog("SENDING RECORDED SAMPLES TO CLIENT")
        service = self.findServiceByUUID("FEC0")
        data = service.queue.get()
        service.queue.task_done()
        return data           
    '''
        
    def startTestECG(self): #address could be the pNum or address  
        self.lock.acquire()
        # clear delay Queue
        self.service.delayQueue = []
        self.service.sampleRecorded = False # create/reset a flag to indicate the samples hasn't been recorded   
        if self.service.state == 0 or self.service.state == 4:  
            NSLog("SENDING START TEST RECORDING SIGNAL")
            self.service.state = 1  
            self.peripheralWorker.writeValueForCharacteristic(self.createStartFlag(), self)          
        elif self.service.state == 3:
            NSLog("PUTTING START TEST RECORDING SIGNAL TO DELAY QUEUE")
            self.service.PushToDelayQueue('WriteStart')            
        else:  
            NSLog("PUTTING START TEST RECORDING SIGNAL TO DELAY QUEUE")
            self.service.state = 3   
            self.service.PushToDelayQueue('WriteStart')   
            self.peripheralWorker.writeValueForCharacteristic(self.createStopFlag(), self)
        self.lock.release()
    


    