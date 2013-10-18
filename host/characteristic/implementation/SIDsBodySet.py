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

from Characteristic import *

'''
structure:
frequency: 2 bytes in sec
avgCnt: 1 byte
run/stop: 1 byte
'''

class SIDsBodySet(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 2
        
    def process(self):
        value = self.instance._.value
        freq, avgCnt, enable = struct.unpack("<HBB", value)
        print "SIDsBodySet %d%d%d" % (freq, avgCnt, enable)
        
        if(enable != 0x01): # if not enabled, enable it
            self.peripheralWorker.writeValueForCharacteristic(self.createEnableFlag(freq, avgCnt), self)

    def createEnableFlag(self, freq, avgCnt):
        settings = struct.pack("<HBB", freq, avgCnt, 0x01)
        val_data = NSData.dataWithBytes_length_(settings, len(settings))
        return val_data
