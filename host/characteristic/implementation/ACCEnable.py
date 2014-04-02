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
import csv
import os

from Characteristic import *

ENABLE_FALG = 1
DISABLE_FALG = 0

class ACCEnable(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 2
        self.acc_enable = 0
        
    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)
        self.acc_enable = int(hex_str, base=16) # 1: enabled; 0: disabled                
        print "ACC ENABLE?(%s) %s" % (self.instance._.UUID, self.acc_enable)
        '''
        if self.acc_enable == ENABLE_FALG:
            #log = "DISABLING ACC" if self.acc_enable == 0 else "ENABLING ACC"
            log = "DISABLING ACC"
            NSLog(log)
            self.peripheralWorker.writeValueForCharacteristic(self.createDisableFlag(), self)
        '''
#        if self.acc_enable == DISABLE_FALG:
#           self.startAcc()
        
        '''
        data = {'type': 'ACCEnable', 
                'value': self.acc_enable,
                'uuid': self.UUID
                }
        return data
        '''
    def startACC(self):
        log = "ENABLING ACC"
        NSLog(log)
        self.peripheralWorker.writeValueForCharacteristic(self.createEnableFlag(), self)

    def stopACC(self):
        log = "Stopping ACC"
        NSLog(log)
        self.peripheralWorker.writeValueForCharacteristic(self.createDisableFlag(), self)

    def createLogFile(self, timestamp):
        self.service.enable_log = True
        if not hasattr(self.service, 'log_acc') or self.service.log_acc == False:
            prefix = os.path.join(os.path.dirname(__file__), os.path.pardir, os.pardir, os.pardir, "data/log_acc_")
            name = timestamp.strftime("%Y%m%d%H%M%S")
            postfix = ".csv"
            fd = None
            fname = prefix + name + postfix
            if not os.path.exists(fname):
                fd = open(fname, 'w')
                self.service.log_acc = fd
                self.service.csvWriter_acc = csv.writer(fd, delimiter=',')
                self.service.csvWriter_acc.writerow(
                    ["Time", "X", "Y", "Z"])
            else:
                raise Exception

    def closeLogFile(self):
        self.service.enable_log = False
        if hasattr(self.service, 'log_acc'):
            self.service.log_acc.flush()
            self.service.log_acc.close()
            self.service.log_acc = False
            self.service.csvWriter_acc = None

    def createEnableFlag(self):
        return self.createFlag(ENABLE_FALG)
        
    def createDisableFlag(self):
        return self.createFlag(DISABLE_FALG)
        
    def createFlag(self, flag):
        byte_array = array.array('b', chr(flag))
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        return val_data
    