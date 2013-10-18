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

class SIDsAudioSet(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 2
        self.isSet = False
        
    def process(self):
        value = self.instance._.value
        para1, para2, para3 = struct.unpack("@BBB", value)
        print "SIDsAudioSet", para1, para2, para3
        if(self.isSet != True):     
            self.peripheralWorker.writeValueForCharacteristic(self.createEnableAudioRead(para2, para3), self)
            self.isSet = True

    def createEnableAudioRead(self, p2, p3):
        settings = struct.pack("@BBB", 0x01, p2, p3)
        val_data = NSData.dataWithBytes_length_(settings, len(settings))
        return val_data