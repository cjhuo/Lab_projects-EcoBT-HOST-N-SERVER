'''
Created on Feb 9, 2013

@author: cjhuo
'''
import binascii
import struct
import array

from Characteristic import *

class ECG(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0
        
    def process(self):
        value = self.instance._.value
        hex_str = binascii.hexlify(value)
        
        # TBD
        return {'type': 'test',
                'uuid': self.UUID
                }
 
    def createEnableFlag(self):
        return self.createFlag(1)
        
    def createDisableFlag(self):
        return self.createFlag(0)
        
    def createFlag(self, flag):
        byte_array = array.array('b', chr(flag))
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        return val_data