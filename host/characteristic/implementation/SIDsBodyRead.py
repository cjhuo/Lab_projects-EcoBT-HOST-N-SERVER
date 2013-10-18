'''
Created on Oct 17, 2013

@author: cjhuo
'''
from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *

import array
import struct
import binascii

from Characteristic import *

'''
structure:

raw data: 2 bytes
'''

class SIDsBodyRead(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0
        
    def process(self):
        #hex_str = binascii.hexlify(self.instance._.value)
        #print "SIDsBodyRead", hex_str
        value = struct.unpack("<H", self.instance._.value)
        print "SIDsBodyRead: ", value
        
        # Convert to temperature in Celsius
        # TBD!!!!!!!
        tempC = None
        
        
        
        # send to frontend
        data = {
                'type': 'BodyTemp',
                'value': tempC
                }
        
        self.peripheralWorker.delegateWorker.getQueue().put(data)
 
  