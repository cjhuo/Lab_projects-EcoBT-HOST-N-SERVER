'''
Created on Feb 15, 2013

@author: cjhuo
'''
from Characteristic import *
from Foundation import *
import binascii

class ECGStatus(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0
        
    def process(self):
        #print self.instance._.value
        value = self.instance._.value
        hex_str = binascii.hexlify(value)
        NSLog("ECG STATUS %@ %@", self.service.UUID, hex_str)
        #val = binascii.hexlify(start)