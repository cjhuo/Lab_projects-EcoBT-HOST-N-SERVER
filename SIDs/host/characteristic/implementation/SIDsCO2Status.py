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

from host.characteristic.implementation.Characteristic import *

'''
typedef union{
  unsigned char data[CO2_STATUS_LEN];
  struct{
  unsigned char start;
  unsigned char LED_ready;
  unsigned char PD0_ready;
  unsigned char PD1_ready;
  unsigned char RH_T_ready;
  unsigned char RH_T_enable;
  };
} co2_status_t;
'''

START_FLAG = 1
STOP_FLAG = 0

class SIDsCO2Status(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 1
        self.state = None # 0: stopped; 1: started
        
    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)
        print "CO2 STATUS: ", hex_str
        value = self.instance._.value
        self.start, self.LED_ready, self.PD0, self.PD1, self.RH_T_ready, self.RH_T_enable = struct.unpack("<BBBBBB", value)
        print self.start, self.LED_ready, self.PD0, self.PD1, self.RH_T_ready, self.RH_T_enable
        if int(self.start) == 0 and int(self.LED_ready) == 1 and int(self.PD0) == 1 and \
                                    int(self.PD1) == 1 and int(self.RH_T_ready) == 1 and int(self.RH_T_enable) == 1: # correct initial state
            self.state = STOP_FLAG
        elif int(self.start) == 1:
            self.state = START_FLAG
        
        if self.peripheralWorker.peripheral.type != 'SIDs':
            self.peripheralWorker.peripheral.type = 'SIDs'
        # send a message to UI
        data = {'type': 'SIDs',
        'value': {'type': 'state',
                  'value': self.state # stopped == ready signal
                  }
        }
        self.peripheralWorker.delegateWorker.getQueue().put(data)
    '''
        enable = int(hex_str, base=16) # 1: enabled; 0: disabled
        print "SIDS SHT25 ENABLE?(%s) %s" % (self.instance._.UUID, enable)
        if self.enable != enable:
            log = "DISABLE" if self.enable == 0 else "ENABLE"
            NSLog("SETTING SIDS MONITORING TO %@", log)
            self.peripheralWorker.writeValueForCharacteristic(self.createFlag(self.enable), self)
        
        data = {'type': 'SIDsEnable', 
                'value': self.enable,
                'uuid': self.UUID
                }
        return data
        '''
    def startSIDs(self):
        byte_array = struct.pack("<BBBBBB", 1, 1, 1, 1, 1, 1)
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        self.peripheralWorker.writeValueForCharacteristic(val_data, self)
        
    def stopSIDs(self):
        byte_array = struct.pack("<BBBBBB", 0, 1, 1, 1, 1, 1)
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        self.peripheralWorker.writeValueForCharacteristic(val_data, self)
    '''
    def createStartFlag(self):
        return self.createFlag(START_FLAG)
        
    def createStopFlag(self):
        return self.createFlag(STOP_FLAG)
        
    def createFlag(self, flag):
        byte_array = array.array('b', chr(flag))
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        return val_data
    '''