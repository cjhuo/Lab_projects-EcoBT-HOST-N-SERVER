'''
Created on Feb 9, 2013

@author: cjhuo
'''
import binascii

from Characteristic import *

class SIDsHumidRead(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0
        
    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)
        value = int(hex_str[:-2], base=16)
        value = value & 0xFFFC
        humid = -6.0 +  (125.0 * value) / 65536
        print "SIDS SHT25 HUMID READING?(%s) %.2f" % (self.instance._.UUID, humid)
        data = {
                'type': 'humidity', 
                'value': round(humid,2),
                'uuid': self.UUID
                } # read to 2nd digit after decimal point
        self.peripheralWorker.delegateWorker.getQueue().put(data)