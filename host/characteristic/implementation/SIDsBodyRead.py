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

import random

'''
structure:

raw data: 2 bytes
'''

class SIDsBodyRead(Characteristic):
    CONV_MAP = {
        0:  1367.760,
        1:  1379.465,
        2:  1391.305,
        3:  1403.239,
        4:  1415.250,
        5:  1427.331,
        6:  1439.460,
        7:  1451.626,
        8:  1463.813,
        9:  1476.009,
        10: 1488.198,
        11: 1500.365,
        12: 1512.499,
        13: 1524.584,
        14: 1536.607,
        15: 1548.558,
        16: 1560.420,
        17: 1572.187,
        18: 1583.845,
        19: 1595.382,
        20: 1606.790,
        21: 1618.059,
        22: 1629.181,
        23: 1640.148,
        24: 1650.950,
        25: 1661.585,
        26: 1672.044,
        27: 1682.321,
        28: 1692.413,
        29: 1702.318,
        30: 1712.023,
        31: 1721.535,
        32: 1730.848,
        33: 1739.980,
        34: 1748.890,
        35: 1757.610,
        36: 1766.168,
        37: 1774.384,
        38: 1782.482,
        39: 1790.379,
        40: 1798.075,
        41: 1805.572,
        42: 1812.871,
        43: 1819.976,
        44: 1826.893,
        45: 1833.609,
        46: 1840.199,
        47: 1846.558,
        48: 1852.661,
        49: 1858.652,
        50: 1864.467
    }

    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0

    def process(self):
        #hex_str = binascii.hexlify(self.instance._.value)
        #print "SIDsBodyRead", hex_str
        value, = struct.unpack("<H", self.instance._.value)
        print "SIDsBodyRead: ", value

        # Convert to temperature in Celsius
        # TBD!!!!!!!
        tempC = 0
        print SIDsBodyRead.CONV_MAP[0]
        if value < SIDsBodyRead.CONV_MAP[0]:
            tempC = -1
        elif value > SIDsBodyRead.CONV_MAP[50]:
            tempC = 51
        else:
            idx = 0
            for i in range(1, 50):
                if SIDsBodyRead.CONV_MAP[i] < value:
                    continue
                idx = i
                break
            lo = SIDsBodyRead.CONV_MAP[idx-1]
            hi = SIDsBodyRead.CONV_MAP[idx]
            temp_lo = idx - 1
            temp_hi = idx
            tempC = (value - lo) * (temp_hi - temp_lo) / (hi - lo) + temp_lo
            tempC = round(tempC, 2)

        print  "Body Temp: ", tempC


#        tempC = random.uniform(31, 40)



        # send to frontend
        data = {
                'type': 'BodyTemp',
                'value': tempC
                }

        self.peripheralWorker.delegateWorker.getQueue().put(data)


