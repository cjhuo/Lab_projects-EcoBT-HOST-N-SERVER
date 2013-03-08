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