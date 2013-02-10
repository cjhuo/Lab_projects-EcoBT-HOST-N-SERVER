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

class SIDsEnable(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 1
        
    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)
        self.enable = int(hex_str, base=16) # 1: enabled; 0: disabled
        print "SIDS SHT25 ENABLE?(%s) %s" % (self.instance._.UUID, self.enable)
        data = {'type': 'SIDsEnable', 
                'value': self.enable
                }
        return data
    
    def createEnableFlag(self):
        return self.createFlag(1)
        
    def createDisableFlag(self):
        return self.createFlag(0)
        
    def createFlag(self, flag):
        byte_array = array.array('b', chr(flag))
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        return val_data