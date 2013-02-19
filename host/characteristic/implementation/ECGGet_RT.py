'''
Created on Feb 9, 2013

@author: cjhuo
'''
from Foundation import *

import binascii
import struct
import array
from Queue import Queue 

from Characteristic import *
from misc.PeriodicExecutor import PeriodicExecutor

firstHalf = 'FEC6' # V6, I, II, V2
secondHalf = 'FEC7' # V3, V4, V5, V1

class ECGGet(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0
        self.queue = Queue()
    
    def setRole(self):
        self.service.getter = self

    def process(self):
        # starting from a brand new recording, means ECGSet doesn't assign it an initial value, reading a remnant data
        if not hasattr(self.service, "record_cnt"):
            if not hasattr(self.service, "sendStopFromGetter") or self.service.sendStopFromGetter == False: 
                NSLog("READING A REMNANT DATA, STOP NODE FROM READING SD CARD")
                self.peripheralWorker.writeValueForCharacteristic(self.service.setter.createStopFlag(), self.service.setter)
                self.service.sendStopFromGetter = True
            return 
        value = self.instance._.value # continued from an unknown sequence number
        hex_str = binascii.hexlify(value)
        if self.UUID == "FEC6": # data1
            value = self.instance._.value
            ret = struct.unpack("16B", value)
            self.service.data_prefix = ret[0]
            (temp,) = struct.unpack(">I", chr(ret[1]) + chr(ret[2]) + chr(ret[3]) + chr(0))
            self.service.status = temp >> 8
            (temp,) = struct.unpack(">i", chr(ret[4]) + chr(ret[5]) + chr(ret[6]) + chr(0))
            self.service.V6 = temp >> 8
            (temp,) = struct.unpack(">i", chr(ret[7]) + chr(ret[8]) + chr(ret[9]) + chr(0))
            self.service.LeadI = temp >> 8
            (temp,) = struct.unpack(">i", chr(ret[10]) + chr(ret[11]) + chr(ret[12]) + chr(0))
            self.service.LeadII = temp >> 8
            (temp,) = struct.unpack(">i", chr(ret[13]) + chr(ret[14]) + chr(ret[15]) + chr(0))
            self.service.V2 = temp >> 8
            self.service.LeadIII = self.service.LeadII - self.service.LeadI
            self.service.aVR = 0 - ((self.service.LeadI + self.service.LeadII) / 2)
            self.service.aVL = self.service.LeadI - (self.service.LeadII / 2)
            self.service.aVF = self.service.LeadII - (self.service.LeadI / 2)

        if self.UUID == "FEC7": # data2
            value = self.instance._.value
            ret = struct.unpack("16B", value)
            if self.service.data_prefix != None and self.service.data_prefix == ret[0]:
                data_prefix = ret[0]
            else:
                print "miss match"
                return
            (temp,) = struct.unpack(">i", chr(ret[1]) + chr(ret[2]) + chr(ret[3]) + chr(0))
            self.service.V3 = temp >> 8
            (temp,) = struct.unpack(">i", chr(ret[4]) + chr(ret[5]) + chr(ret[6]) + chr(0))
            self.service.V4 = temp >> 8
            (temp,) = struct.unpack(">i", chr(ret[7]) + chr(ret[8]) + chr(ret[9]) + chr(0))
            self.service.V5 = temp >> 8
            (temp,) = struct.unpack(">i", chr(ret[10]) + chr(ret[11]) + chr(ret[12]) + chr(0))
            self.service.V1 = temp >> 8
            output = ""
            if self.service.status != None:
                output += "Record  number       : %8d            status: %06X\n" % \
                (self.service.record_cnt, self.service.status)
            output += " V1: %8d  V2: %8d  V3: %8d    V4: %8d     V5: %8d      V6: %8d\n" % \
            (self.service.V1, self.service.V2, self.service.V3, self.service.V4, self.service.V5, self.service.V6)
            output += "aVR: %8d aVL: %8d aVF: %8d LeadI: %8d LeadII: %8d LeadIII: %8d\n" % \
            (self.service.aVR, self.service.aVL, self.service.aVF, self.service.LeadI, self.service.LeadII, self.service.LeadIII)
            self.queue.put({
                             'V1': self.service.V1,
                             'V2': self.service.V2,
                             'V3': self.service.V3,
                             'V4': self.service.V4,
                             'V5': self.service.V5,
                             'V6': self.service.V6,
                             'aVR': self.service.aVR,
                             'aVL': self.service.aVL,
                             'aVF': self.service.aVF,
                             'I': self.service.LeadI,
                             'II': self.service.LeadII,
                             'III': self.service.LeadIII,                 
                            })
            if self.service.record_cnt == 1:    # set sampleRecorded flag to True to prevent recording a sample again;
                                                # start from begnning, start periodic executor
                self.service.sampleRecorded = True
                pe = PeriodicExecutor()
                pe.setParams(1, self.sentOutDataToDelegateQueue, pe, self.queue)
                pe.start()
            
            if not hasattr(self.service, "fd"):
                import os
                path = os.path.join(os.path.dirname(__file__), "log.txt")
                self.service.fd = open(path, 'w')
            if self.service.record_cnt % 10 == 1:
                print output
            self.service.fd.write(output)

                
            
            self.service.record_cnt = self.service.record_cnt + 1    
            if self.service.record_cnt > 10: # time to stop reading from sd card after reading the first 10-second samples
                NSLog("10 SAMPLES READING COMPLETE, STOPPING FROM READING SD CARD")
                self.peripheralWorker.writeValueForCharacteristic(self.service.setter.createStopFlag(), self.service.setter)
                  
        # TBD
        '''
        data = {
                'type': 'ECG',
                'value': ''
                }
        self.peripheralWorker.delegateWorker.getQueue().put(data)
        '''
    def sentOutDataToDelegateQueue(self, pExecutor, queue):
        if not queue.empty():
            data = queue.get()
            queue.task_done()
            tmpData = {
                        'type': 'ecg',
                        'data': data
                    }
            self.peripheralWorker.delegateWorker.getQueue().put(tmpData)
        else: # quiting
            print "ECG Data Queue is empty, stop sending data to client"
            pExecutor.setFlag.set()
                