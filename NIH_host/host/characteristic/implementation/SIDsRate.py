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

class SIDsRate(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 1
        
    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)
        self.rate = int(hex_str, base=16) # 1: enabled; 0: disabled
        print "SIDS SHT25 RATE?(%s) %d sec" % (self.instance._.UUID, self.rate)
        data = {'type': 'SIDsRate', 
                'value': self.rate
                }
        return data
    
    def createRateBySec(self, sec):
        byte_array = array.array('b', chr(sec))
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        return val_data