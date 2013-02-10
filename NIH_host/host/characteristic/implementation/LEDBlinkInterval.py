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
        self.privilege = 1
        
    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)
        self.interval = int(hex_str, base=16) # 1: enabled; 0: disabled
        print "LED Blink Interval?(%s) %d sec" % (self.instance._.UUID, self.interval/10)
        data = {'type': 'LEDBlinkInterval', 
                'value': self.interval
                }
        return data
    
    def createIntervalBySec(self, sec):
        byte_array = array.array('b', chr(sec*10))
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        return val_data