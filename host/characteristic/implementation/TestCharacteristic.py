'''
Created on Jan 25, 2014

@author: cjhuo
'''
from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *

import array, binascii, struct


from Characteristic import *

class TestCharacteristic(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 3
        self.acc_enable = 0
        
    def process(self):
        print "length of data ", len(self.instance._.value)
        
        data, = struct.unpack("@"+str(len(self.instance._.value))+"s", self.instance._.value)
                
        print "Data is ", self.peripheralWorker.securityObj.decrypt(data)
        
        #self.peripheralWorker.readValueForCharacteristic(self.peripheralWorker.findCharacteristicByUUID(u'7788'))