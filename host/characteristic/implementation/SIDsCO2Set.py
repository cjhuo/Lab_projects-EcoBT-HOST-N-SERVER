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

import json
import os
import csv

from Characteristic import *

'''
typedef union{
  unsigned char data[CO2_PARAM_LEN];
  struct{
  unsigned short interval;
  unsigned char sample_cnt;
  unsigned char sample_calculation; // 0: average, 1: remove max/min then avg 2: median
  unsigned char LED0_power;
  unsigned char LED0_PD0_power;
  unsigned char LED0_PD1_power;
  unsigned short LED0_delay;
  unsigned char LED1_power;
  unsigned char LED1_PD0_power;
  unsigned char LED1_PD1_power;
  unsigned short LED1_delay;
  unsigned char AMBI_PD0_power;
  unsigned char AMBI_PD1_power;
  unsigned short AMBI_delay;
  };
} co2_param_t;
'''

SETTING_NAMES = ['TIME BETWEEN DATA (s) (1~65535)', 'SAMPLE COUNT (1~255)', 'SAMPLE CACULATION', \
                 'LED1 GAIN (0~255)', 'LED1 PD1 GAIN (0~255)', 'LED1 PD2 GAIN (0~255)', 'LED1 DELAY (ms) (10~65535)', \
                 'LED2 GAIN (0~255)', 'LED2 PD1 GAIN (0~255)', 'LED2 PD2 GAIN (0~255)', 'LED2 DELAY (ms) (10~65535)', \
                 'AMBIENT PD1 GAIN (0~255)', 'AMBIENT PD2 GAIN (0~255)','AMBIENT DELAY (ms) (10~65535)']

FORMULA_PARAM_NAMES = []

class SIDsCO2Set(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 2
        self.settings = dict()
        
    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)
        print "CO2 PARAMETERS: ", hex_str
        value = self.instance._.value
        temp = struct.unpack("<HBBBBBHBBBHBBH", value)
        counter = 0
        for item in temp:
            self.settings[SETTING_NAMES[counter]] = int(item)
            counter += 1
        
        self.sendSettingsToFrontend()
        
    
    def updateSettingsByDict(self, settings):
        counter = 0;
        for key, val in settings.items():
            self.settings[str(key)] = int(val)
            counter += 0
        print self.settings
        self.sendSettingsToPeripheral()
            
    def updateSettingsByFile(self, fname):
        with open(fname, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                sName = str(row[0])
                sValue = int(row[1])
                if sName in SETTING_NAMES:
                    self.settings[sName] = sValue
        self.sendSettingsToPeripheral()
                    
    def sendSettingsToPeripheral(self):
        self.peripheralWorker.writeValueForCharacteristic(self.createSettings(), self)

    def sendSettingsToFrontend(self):
        data = {
                'type': 'SIDsSettings',
                'value': self.settings
                }
        self.peripheralWorker.delegateWorker.getQueue().put(data)
 
    def createSettings(self):
        settings = list()
        for name in SETTING_NAMES:
            settings.append(self.settings[name])
        byte_array = struct.pack("<HBBBBBHBBBHBBH", *settings)
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        return val_data