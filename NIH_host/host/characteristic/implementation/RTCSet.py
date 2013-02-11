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
        
    def process(self):
        value = self.instance._.value
        year, month, day, wday, hour, minute, second = struct.unpack("<HBBBBBB", value)
        print "EPL RTC Last Set Time ", year, month, day, wday, hour, minute, second
        self.time = datetime(year, month, day, wday, hour, minute, second)
        data = {'type': "RTCSet", 'value': self.time} # read to 2nd digit after decimal point
        return data
    
    def createHostCurrentTime(self):
        now = datetime.now()
        print "Creating host current time"
        timestamp = struct.pack("<HBBBBBB", now.year, now.month, now.day, now.isoweekday(), now.hour, now.minute, now.second)
        val_data = NSData.dataWithBytes_length_(timestamp, len(timestamp))
        return val_data