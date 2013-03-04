'''
Created on Feb 9, 2013

@author: cjhuo
'''

from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *

import array
import binascii
import struct

from Characteristic import *

'''
typedef union{
  unsigned char data[CO2_READING_LEN];
  struct{
  unsigned char timestamp[3]; //hour, minute, second
  short LED0_PD0;
  short LED0_PD1;
  short LED1_PD0;
  short LED1_PD1;
  short AMBI_PD0;
  short AMBI_PD1;
  short RH;
  short T;
  };
} co2_reading_t;
'''

class SIDsCO2Read(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0

    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)
        print "CO2 READING: ", hex_str
        value = self.instance._.value
        hour, min, sec, LED00, LED01, LED10, LED11, amb0, amb1, rh, temp = struct.unpack("<BBBhhhhhhHH", value)
        print rh, temp
        rh = rh & 0xFFFC
        rh = -6.0 + (125.0 * rh) / 65536
        temp = temp & 0xFFFC
        temp = -46.85 + (175.72 * temp) / 65536

        print hour, min, sec, LED00, LED01, LED10, LED11, amb0, amb1, rh, temp
        '''
        self.start = int(hex_str, base=16) # 1: enabled; 0: disabled
        print "SIDS SHT25 Start?(%s) %d" % (self.instance._.UUID, self.start)
        data = {
                'type': 'SIDsStart',
                'value': self.start,
                'uuid': self.UUID
                }
        return data
        '''

    def createStartFlag(self):
        return self.createFlag(1)

    def createStopFlag(self):
        return self.createFlag(0)

    def createFlag(self, flag):
        byte_array = array.array('b', chr(flag))
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        return val_data
