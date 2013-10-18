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

class SIDsBodySet(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 2
        self.isSet = False
        
    def process(self):
        value = self.instance._.value
        para1, para2, para3, para4 = struct.unpack("@BBBB", value)
        print "SIDsBodySet", para1, para2, para3, para4
        if(self.isSet != True):     
            self.peripheralWorker.writeValueForCharacteristic(self.createEnableBodyTemp(para2, para3, para4), self)
            self.isSet = True

    def createEnableBodyTemp(self, p2, p3, p4):
        settings = struct.pack("@BBBB", 0x01, p2, p3, p4)
        val_data = NSData.dataWithBytes_length_(settings, len(settings))
        return val_data
