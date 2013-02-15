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

firstHalf = 'FEC6' # V6, I, II, V2
secondHalf = 'FEC7' # V3, V4, V5, V1
ECG_CHANNELLABELS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']

class ECGGet(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0
    
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
        
        if self.service.record_cnt == 1:    # set sampleRecorded flag to True to prevent recording a sample again;
                                            # initial array each every channel
            self.service.sampleRecorded = True
            self.service.queue = Queue()
            self.service.datasets = []
            for i in range(12):
                self.service.datasets.append(list())    
        
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
            self.service.datasets[0].append(self.service.LeadI/80000)
            self.service.datasets[1].append(self.service.LeadII/80000)
            self.service.datasets[2].append(self.service.LeadIII/80000)
            self.service.datasets[3].append(self.service.V1/80000)
            self.service.datasets[4].append(self.service.V2/80000)
            self.service.datasets[5].append(self.service.V3/80000)
            self.service.datasets[6].append(self.service.V4/80000)
            self.service.datasets[7].append(self.service.V5/80000)
            self.service.datasets[8].append(self.service.V6/80000)
            self.service.datasets[9].append(self.service.aVR/80000)
            self.service.datasets[10].append(self.service.aVL/80000)
            self.service.datasets[11].append(self.service.aVF/80000)

            if not hasattr(self.service, "fd"):
                import os
                path = os.path.join(os.path.dirname(__file__), "log.txt")
                self.service.fd = open(path, 'w')
            if self.service.record_cnt % 10 == 1:
                print output
            self.service.fd.write(output)
            
            self.service.record_cnt = self.service.record_cnt + 1    
            if self.service.record_cnt % 5 == 1 and self.service.record_cnt <= 501:
                progress = {
                            'type': 'ECG',
                            'value': {
                                     'type': 'progress',
                                     'value': self.service.record_cnt/5
                                     }
                            }
                self.peripheralWorker.delegateWorker.getQueue().put(progress)
            if self.service.record_cnt > 500: # time to stop reading from sd card after reading the first 10-second samples
                # send data to peripheral delegate worker
                if not hasattr(self.service, 'send'): # make sure it only send once!!!!!!   
                    NSLog("10 SAMPLES READING COMPLETE, STOPPING FROM READING SD CARD")
                    self.peripheralWorker.writeValueForCharacteristic(self.service.setter.createStopFlag(), self.service.setter)             
                    tmpDatasets = []
                    for i in range(len(self.service.datasets)):
                        data = [self.service.datasets[i][j] for j in range(len(self.service.datasets[i]))]
                        label = ECG_CHANNELLABELS[i]            
                        #label = "channel " + str(i)
                        tmpDatasets.append(dict())
                        tmpDatasets[i]['data'] = data 
                        tmpDatasets[i]['label'] = label
                        
                    val = {
                           'type': 'ecg',
                           'data': tmpDatasets
                           }
                    #self.service.queue.put(val)
                    #print val
                    self.peripheralWorker.delegateWorker.getQueue().put(val)
                    self.service.send = True
                  
        # TBD
        '''
        data = {
                'type': 'ECG',
                'value': ''
                }
        self.peripheralWorker.delegateWorker.getQueue().put(data)
        '''