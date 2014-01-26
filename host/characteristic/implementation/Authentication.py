'''
Created on Jan 26, 2014

@author: cjhuo
'''

from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *

import array
import binascii

from Characteristic import *

class Authentication(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 3
        self.acc_enable = 0
        
    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)
        acc_enable = int(hex_str, base=16) # 1: enabled; 0: disabled                
        print "ACC ENABLE?(%s) %s" % (self.instance._.UUID, acc_enable)
        if self.acc_enable != acc_enable:
            log = "DISABLING ACC" if self.acc_enable == 0 else "ENABLING ACC"
            NSLog(log)
            self.peripheralWorker.writeValueForCharacteristic(self.createFlag(self.acc_enable), self)
        '''
        data = {'type': 'ACCEnable', 
                'value': self.acc_enable,
                'uuid': self.UUID
                }
        return data
        '''
    
    def createEnableFlag(self):
        return self.createFlag(1)
        
    def createDisableFlag(self):
        return self.createFlag(0)
        
    def createFlag(self, flag):
        byte_array = array.array('b', chr(flag))
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        return val_data
    