'''
Created on Feb 9, 2013

@author: cjhuo
'''

import binascii

from Characteristic import *

class SIDsTempRead(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0
        
    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)
        value = int(hex_str[:-2], base=16)
        value = value & 0xFFFC
        temp = -46.85 + (175.72 * value) / 65536
        print "SIDS SHT25 TEMP READING?(%s) %.2f" % (self.instance._.UUID, temp)
        data = {
                'type': 'temperature', 
                'value': round(temp, 2),
                'uuid': self.UUID
                } # read to 2nd digit after decimal point
        self.peripheralWorker.delegateWorker.getQueue().put(data)