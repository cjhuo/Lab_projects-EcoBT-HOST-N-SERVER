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
window: 2 bytes in ms
run/stop: 1 byte  
'''
class SIDsAudioSet(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 2
        
    def process(self):
        value = self.instance._.value
        window, enable = struct.unpack("<HB", value)
        print "SIDsAudioSet %d%d" % (window, enable)
        
        if(enable != 0x01): # if not enabled, enable it
            self.peripheralWorker.writeValueForCharacteristic(self.createEnableAudioRead(window), self)

    def createEnableAudioRead(self, window):
        settings = struct.pack("<HB", window, 0x01)
        val_data = NSData.dataWithBytes_length_(settings, len(settings))
        return val_data