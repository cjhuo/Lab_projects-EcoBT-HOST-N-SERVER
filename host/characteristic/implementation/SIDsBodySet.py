'''
Created on Oct 17, 2013

@author: cjhuo
'''

from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *

import array
import struct
import csv
import os

from Characteristic import *

'''
structure:
frequency: 2 bytes in sec
avgCnt: 1 byte
run/stop: 1 byte
'''


class SIDsBodySet(Characteristic):

    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 2
        self.freq = 0
        self.ready = 0
        self.enable = 0

    def process(self):
        value = self.instance._.value
        self.freq, self.ready, self.enable = struct.unpack("<HBB", value)
        print "SIDsBodySet %d%d%d" % (self.freq, self.ready, self.enable)

# if(enable != 0x01): # if not enabled, enable it
#            self.peripheralWorker.writeValueForCharacteristic(self.createEnableFlag(freq, ready), self)

    def startBodyTemp(self):
        print "Start BodyTemp"
        self.peripheralWorker.writeValueForCharacteristic(self.createEnableFlag(self.freq, self.ready), self)

    def stopBodyTemp(self):
        self.peripheralWorker.writeValueForCharacteristic(self.createDisableFlag(self.freq, self.ready), self)

    def createLogFile(self, timestamp):
        self.service.enable_log = True
        if not hasattr(self.service, 'log_bodytemp') or self.service.log_bodytemp == False:
            prefix = os.path.join(os.path.dirname(__file__), os.path.pardir, os.pardir, os.pardir, "data/log_bodytemp_")
            name = timestamp.strftime("%Y%m%d%H%M%S")
            postfix = ".csv"
            fd = None
            fname = prefix + name + postfix
            if not os.path.exists(fname):
                fd = open(fname, 'w')
                self.service.log_bodytemp = fd
                self.service.csvWriter_bodytemp = csv.writer(fd, delimiter=',')
                self.service.csvWriter_bodytemp.writerow(
                    ["Time", "Body Temperature"])
            else:
                raise Exception

    def closeLogFile(self):
        self.service.enable_log = False
        if hasattr(self.service, 'log_bodytemp'):
            self.service.log_bodytemp.flush()
            self.service.log_bodytemp.close()
            self.service.log_bodytemp = False
            self.service.csvWriter_bodytemp = None

    def createEnableFlag(self, freq, ready):
        settings = struct.pack("<HBB", freq, ready, 0x01)
        val_data = NSData.dataWithBytes_length_(settings, len(settings))
        return val_data

    def createDisableFlag(self, freq, ready):
        settings = struct.pack("<HBB", freq, ready, 0x00)
        val_data = NSData.dataWithBytes_length_(settings, len(settings))
        return val_data
