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
        self.power = 0
        self.enable = 0
        self.record = 0

    def process(self):
        value = self.instance._.value
        self.power, self.enable, self.record = struct.unpack("<BBB", value)
        print "SIDsAudioSet %d%d%d" % (power, enable, record)

#        if (power != 0x01):
#            self.peripheralWorker.writeValueForCharacteristic(self.createAudioReadConf(0x01, 0x01, 0x00), self)

#        if(enable != 0x01): # if not enabled, enable it
#            self.peripheralWorker.writeValueForCharacteristic(self.createEnableAudioRead(window), self)

    def startAudioRead(self):
        self.peripheralWorker.writeValueForCharacteristic(self.createAudioReadConf(0x01, 0x01, 0x00), self)

    def stopAudioRead(self):
        self.peripheralWorker.writeValueForCharacteristic(self.createAudioReadConf(0x00, 0x00, 0x00), self)        

    def createEnableAudioRead(self, window):
        settings = struct.pack("<HB", window, 0x01)
        val_data = NSData.dataWithBytes_length_(settings, len(settings))
        return val_data

    def createAudioReadConf(self, power, enable, record):
        settings = struct.pack("BBB", power, enable, record)
        val_data = NSData.dataWithBytes_length_(settings, len(settings))
        return val_data
