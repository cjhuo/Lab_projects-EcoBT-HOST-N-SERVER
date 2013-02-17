'''
Created on Feb 9, 2013

@author: cjhuo
'''
from Foundation import *

import binascii
import struct
import array
#from Queue import Queue

from Characteristic import *

firstHalf = 'FEC6' # V6, I, II, V2
secondHalf = 'FEC7' # V3, V4, V5, V1
ECG_CHANNELLABELS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
NUM_OF_SAMPLES = 2500

class ECGReading:
    def __init__(self):
        self.reading = {}
        self.reading['status'] = None
        self.reading['V1'] = None
        self.reading['V2'] = None
        self.reading['V3'] = None
        self.reading['V4'] = None
        self.reading['V5'] = None
        self.reading['V6'] = None
        self.reading['I'] = None
        self.reading['II'] = None
        self.reading['III'] = None
        self.reading['aVR'] = None
        self.reading['aVL'] = None
        self.reading['aVF'] = None

        self.idx_table = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'status']

    def get(self, key=None):
        if key and (key in self.reading):
            return self.reading[key]
        else:
            return self.reading

    def set(self, key=None, value=None, convert=True):
        from types import IntType, DictType
        if key and (key in self.reading):
            if type(value) is IntType:
                if convert and key != 'status':
                    self.reading[key] = int(value * 2.86 / 6 / 10000)  # uint: milliVolt
                else:
                    self.reading[key] = value
        else:
            if type(value) is DictType:
                for key in value:
                    if key in self.reading and type(value[key]) is IntType:
                        self.reading[key] = value[key]
        # update III, aVR, aVL, aVF reading when I and II is updated
        if (key in ('I', 'II')) and (self.reading['I'] and self.reading['II']):
            i = self.reading['I']
            ii = self.reading['II']
            self.reading['III'] = ii - i
            self.reading['aVR'] = 0 - ((i + ii) / 2)
            self.reading['aVL'] = i - (ii / 2)
            self.reading['aVF'] = ii - (i / 2)

    def set_by_idx(self, idx, value):
        from types import IntType
        if idx in range(len(self.idx_table)):
            if type(value) is IntType:
                self.reading[self.idx_table[idx]] = value

    def get_by_idx(self, idx):
        if idx in range(len(self.idx_table)):
            return self.reading[self.idx_table[idx]]
        else:
            return None

    def isValid(self):
        for key in self.reading:
            if self.reading[key] == None:
                return False
        return True

    def isEmpty(self):
        for key in self.reading:
            if self.reading[key] != None:
                return False
        return True

    def __str__(self):
        if not self.isValid():
            return ""
        output = ""
        output += "STATUS: 0x%06X\n" % self.reading['status']
        for key in self.idx_table:
            if key != 'status':
                output += "%3s: %+8d\t" % (key, self.reading[key])
            if key == 'aVF':
                output += "\n"
        return output

class ECGGet(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0

    def setRole(self):
        self.service.getter = self

        if not hasattr(self.service, "read_buffer"):
            self.service.read_buffer = {}
            for idx in range(256):
                self.service.read_buffer[idx] = ECGReading()

    def process(self):
        # starting from a brand new recording, means ECGSet doesn't assign it an initial value, reading a remnant data
        if not hasattr(self.service, "record_cnt"):
            if not hasattr(self.service, "sendStopFromGetter") or self.service.sendStopFromGetter == False:
                NSLog("READING A REMNANT DATA, STOP NODE FROM READING SD CARD")
                self.service.state = 3
                self.peripheralWorker.writeValueForCharacteristic(self.service.setter.createStopFlag(), self.service.setter)
                self.service.sendStopFromGetter = True
            return

        if self.service.record_cnt == 1:
            # initial array each every channel
            #self.service.queue = Queue()
            self.service.datasets = []
            for i in range(12):
                self.service.datasets.append(list())

        value = self.instance._.value # continued from an unknown sequence number
        hex_str = binascii.hexlify(value)
        if self.UUID == "FEC6": # data1
            value = self.instance._.value
            ret = struct.unpack("16B", value)
            """
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
            """

            key = int(ret[0])
            (temp,) = struct.unpack(">I", chr(ret[1]) + chr(ret[2]) + chr(ret[3]) + chr(0))
            self.service.read_buffer[key].set('status', temp >> 8)
            (temp,) = struct.unpack(">i", chr(ret[4]) + chr(ret[5]) + chr(ret[6]) + chr(0))
            self.service.read_buffer[key].set('V6', temp >> 8)
            (temp,) = struct.unpack(">i", chr(ret[7]) + chr(ret[8]) + chr(ret[9]) + chr(0))
            self.service.read_buffer[key].set('I', temp >> 8)
            (temp,) = struct.unpack(">i", chr(ret[10]) + chr(ret[11]) + chr(ret[12]) + chr(0))
            self.service.read_buffer[key].set('II', temp >> 8)
            (temp,) = struct.unpack(">i", chr(ret[13]) + chr(ret[14]) + chr(ret[15]) + chr(0))
            self.service.read_buffer[key].set('V2', temp >> 8)

            if self.service.read_buffer[key].isValid():
                self.handle_reading(key)


        if self.UUID == "FEC7": # data2
            value = self.instance._.value
            ret = struct.unpack("16B", value)
            """
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
            self.service.datasets[0].append(((self.service.LeadI*2.86)/10000)/6)
            self.service.datasets[1].append(((self.service.LeadII*2.86)/10000)/6)
            self.service.datasets[2].append((self.service.LeadIII*2.86/10000)/6)
            self.service.datasets[3].append((self.service.aVR*2.86/10000)/6)
            self.service.datasets[4].append((self.service.aVL*2.86/10000)/6)
            self.service.datasets[5].append((self.service.aVF*2.86/10000)/6)
            self.service.datasets[6].append((self.service.V1*2.86/10000)/6)
            self.service.datasets[7].append((self.service.V2*2.86/10000)/6)
            self.service.datasets[8].append((self.service.V3*2.86/10000)/6)
            self.service.datasets[9].append((self.service.V4*2.86/10000)/6)
            self.service.datasets[10].append((self.service.V5*2.86/10000)/6)
            self.service.datasets[11].append((self.service.V6*2.86/10000)/6)
            """
            key = int(ret[0])
            (temp,) = struct.unpack(">i", chr(ret[1]) + chr(ret[2]) + chr(ret[3]) + chr(0))
            self.service.read_buffer[key].set('V3', temp >> 8)
            (temp,) = struct.unpack(">i", chr(ret[4]) + chr(ret[5]) + chr(ret[6]) + chr(0))
            self.service.read_buffer[key].set('V4', temp >> 8)
            (temp,) = struct.unpack(">i", chr(ret[7]) + chr(ret[8]) + chr(ret[9]) + chr(0))
            self.service.read_buffer[key].set('V5', temp >> 8)
            (temp,) = struct.unpack(">i", chr(ret[10]) + chr(ret[11]) + chr(ret[12]) + chr(0))
            self.service.read_buffer[key].set('V1', temp >> 8)

            if self.service.read_buffer[key].isValid():
                self.handle_reading(key)


    def handle_reading(self, key):
#            if not hasattr(self.service, "fd"):
#                import os
#                path = os.path.join(os.path.dirname(__file__), "log.txt")
#                self.service.fd = open(path, 'w')
        for i in range(12):
            self.service.datasets[i].append(self.service.read_buffer[key].get_by_idx(i))
            self.service.read_buffer[key].set_by_idx(i, None)
            # should the self.service.read_buffer[key] be reset after append???

        if self.service.record_cnt % 10 == 1:
            print self.service.record_cnt
            print self.service.read_buffer[key]
#            self.service.fd.write(output)
        self.service.record_cnt = self.service.record_cnt + 1
        if self.service.record_cnt % (NUM_OF_SAMPLES/100) == 1 and self.service.record_cnt <= (NUM_OF_SAMPLES+1):
            progress = {
                        'type': 'ECG',
                        'value': {
                                'type': 'progress',
                                'value': self.service.record_cnt/(NUM_OF_SAMPLES/100)
                                }
                        }
            self.peripheralWorker.delegateWorker.getQueue().put(progress)
        if self.service.record_cnt > NUM_OF_SAMPLES: # time to stop reading from sd card after reading the first 10-second samples
            # send data to peripheral delegate worker
            if self.service.sampleRecorded == False: # make sure it only send once!!!!!!
                self.service.sampleRecorded = True # set sampleRecorded flag to True to prevent recording a sample again;
                NSLog("10 SAMPLES READING COMPLETE, STOPPING FROM READING SD CARD")
                self.service.state = 3
                self.peripheralWorker.writeValueForCharacteristic(self.service.setter.createStopFlag(), self.service.setter)
                tmpDatasets = []
                for i in range(len(self.service.datasets)):
                    data = [self.service.datasets[i][j] for j in range(len(self.service.datasets[i]))]
                    label = ECG_CHANNELLABELS[i]
                    #label = "channel " + str(i)
                    tmpDatasets.append(dict())
                    tmpDatasets[i]['data'] = data
                    tmpDatasets[i]['label'] = label
                    tmpDatasets[i]['min'] = min(data)
                    tmpDatasets[i]['max'] = max(data)

                val = {
                        'type': 'ecg',
                        'data': tmpDatasets
                    }
                #self.service.queue.put(val)
                #print val
                self.peripheralWorker.delegateWorker.getQueue().put(val)
                #self.service.send = True
            else: # not sending samples to clients
                pass

        # TBD
        '''
        data = {
                'type': 'ECG',
                'value': ''
                }
        self.peripheralWorker.delegateWorker.getQueue().put(data)
        '''
