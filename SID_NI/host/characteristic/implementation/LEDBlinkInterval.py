'''
Created on Feb 10, 2013

@author: cjhuo
'''


from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *

import array
import binascii

from Characteristic import *

class LEDBlinkInterval(Characteristic): # unit 0.1 sec
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 2
        
    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)
        self.interval = int(hex_str, base=16) # 1: enabled; 0: disabled
        print "LED Blink Interval?(%s) %d sec" % (self.instance._.UUID, self.interval/10)
        if self.UUID == "FF13":
            t = 'LED0 Interval'
        elif self.UUID == "FF14":
            t = 'LED1 Interval'             
        data = {
                'type': t, 
                'value': self.interval,
                'uuid': self.UUID
                }
        return data
    
    def createInterval(self, interval): # unit: 0.1 sec
        byte_array = array.array('b', chr(interval))
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        return val_data