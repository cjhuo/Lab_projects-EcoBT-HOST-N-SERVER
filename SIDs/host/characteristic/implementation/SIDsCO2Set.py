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
  unsigned char data[CO2_PARAM_LEN];
  struct{
  unsigned short interval;
  unsigned char sample_calculation; // 0: average, 1: remove max/min then avg 2: median //input disabled
  unsigned char LED0_power;
  unsigned char LED0_PD0_power;
  unsigned char LED0_PD1_power;
  unsigned short LED0_delay;
  unsigned char LED0_sample_cnt;
  unsigned char LED1_power;
  unsigned char LED1_PD0_power;
  unsigned char LED1_PD1_power;
  unsigned short LED1_delay;
  unsigned char LED1_sample_cnt;
  unsigned char AMBI_PD0_power;
  unsigned char AMBI_PD1_power;
  unsigned short AMBI_delay;
  unsigned char AMBI_sample_cnt;
  };
} co2_param_t;
'''

SETTING_NAMES = ['TIME BETWEEN DATA', 'SAMPLE CACULATION', 'LED1 POWER', 'LED1 PD1 POWER', 'LED1 PD2 POWER', 'LED1 DELAY', 'LED1 SAMPLE COUNT', \
                 'LED2 POWER', 'LED2 PD1 POWER', 'LED2 PD2 POWER', 'LED2 DELAY', 'LED2 SAMPLE COUNT', 'AMBIENT PD1 POWER', 'AMBIENT PD2 POWER',\
                 'AMBIENT DELAY', 'AMBIENT SAMPLE COUNT' ]

class SIDsCO2Set(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 2
        self.settings = dict()
        
    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)
        print "CO2 PARAMETERS: ", hex_str
        
        value = self.instance._.value
        temp = struct.unpack("<HBBBBHBBBBHBBBHB", value)
        counter = 0
        for item in temp:
            self.settings[SETTING_NAMES[counter]] = int(item)
            counter += 1
        
        #self.rate = int(hex_str, base=16) # 1: enabled; 0: disabled
        #print "SIDS SHT25 RATE?(%s) %d sec" % (self.UUID, self.rate)
        '''
        data = {
                'type': 'SIDsRate', 
                'value': self.rate,
                'uuid': self.UUID
                }
        return data
        '''
    
    def updateSettings(self, settings):
        counter = 0;
        for val in settings:
            self.settings[SETTING_NAMES[counter]] = val
            counter += 0
            
    def createRateBySec(self, sec):
        byte_array = array.array('b', chr(sec))
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        return val_data