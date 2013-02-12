'''
Created on Feb 10, 2013

@author: cjhuo
'''

import array
import struct
from datetime import datetime

from Characteristic import *

'''
get time is updated every sec.
get time is not auto notify
'''
class RTCGet(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0
        
    def process(self):
        value = self.instance._.value
        year, month, day, wday, hour, minute, second = struct.unpack("<HBBBBBB", value)
        try:
            rtc_time = datetime(year = year, month = month, day = day, hour = hour, minute = minute, second = second)
            print "EPL RTC Get Time", rtc_time
        except:
            # if the RTC is not set, then the values are 0s
            print "EPL RTC Get Time not set yet!"
            rtc_time = 0
        data = {'type': "RTCGet", 'value': rtc_time, 'uuid': self.UUID} # read to 2nd digit after decimal point
        return data
