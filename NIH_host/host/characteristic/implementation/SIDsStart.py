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

class SIDsStart(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 1
        
    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)
        self.start = int(hex_str, base=16) # 1: enabled; 0: disabled
        print "SIDS SHT25 Start?(%s) %d" % (self.instance._.UUID, self.start)
        data = {'type': 'SIDsStart', 
                'value': self.start
                }
        return data

    def createStartFlag(self):
        return self.createFlag(1)
        
    def createStopFlag(self):
        return self.createFlag(0)
        
    def createFlag(self, flag):
        byte_array = array.array('b', chr(flag))
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        return val_data