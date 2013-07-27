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
        if self.acc_enable == DISABLE_FALG:
            #log = "DISABLING ACC" if self.acc_enable == 0 else "ENABLING ACC"
            log = "ENABLING ACC"
            NSLog(log)
            self.peripheralWorker.writeValueForCharacteristic(self.createEnableFlag(), self)
        
        '''
        data = {'type': 'ACCEnable', 
                'value': self.acc_enable,
                'uuid': self.UUID
                }
        return data
        '''
    
    def createEnableFlag(self):
        return self.createFlag(ENABLE_FALG)
        
    def createDisableFlag(self):
        return self.createFlag(DISABLE_FALG)
        
    def createFlag(self, flag):
        byte_array = array.array('b', chr(flag))
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        return val_data
    