'''
Created on Feb 10, 2013

@author: cjhuo
'''

from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *


import array
import struct
from datetime import datetime

from Characteristic import *

'''
set time would be 0 if not set before
otherwise the last set time timestamp
'''
class RTCSet(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 2
        self.isSet = False
        
    def process(self):
        value = self.instance._.value
        year, month, day, wday, hour, minute, second = struct.unpack("<HBBBBBB", value)
        print "EPL RTC Last Set Time ", year, month, day, wday, hour, minute, second
        if(self.isSet != True):
            now = datetime.now()
            self.time = datetime(now.year, now.month, now.day, now.isoweekday(), now.hour, now.minute, now.second)
            
            NSLog("SENDING TIME OF HOST TO NODE")
            self.peripheralWorker.writeValueForCharacteristic(self.createHostCurrentTime(), self)
            self.isSet = True
        '''
        data = {
                'type': "RTCSet", 
                'value': self.time, 
                'uuid': self.UUID
                } # read to 2nd digit after decimal point
        return data
        #return {'type': 'test'}
        '''
    
    def createHostCurrentTime(self):
        now = datetime.now()
        timestamp = struct.pack("<HBBBBBB", now.year, now.month, now.day, now.isoweekday(), now.hour, now.minute, now.second)
        val_data = NSData.dataWithBytes_length_(timestamp, len(timestamp))
        return val_data