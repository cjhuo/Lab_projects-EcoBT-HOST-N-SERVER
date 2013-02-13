'''
Created on Feb 9, 2013

@author: cjhuo
'''
import binascii
import struct
import array

from Characteristic import *

firstHalf = 'FEC6' # V6, I, II, V2
secondHalf = 'FEC7' # V3, V4, V5, V1

class ECGRead(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0
        
    def process(self):
        value = self.instance._.value
        hex_str = binascii.hexlify(value)
        
        # TBD
        data = {
                'type': 'ECG',
                'value': ''
                }
        self.peripheralWorker.delegateWorker.getQueue().put(data)
