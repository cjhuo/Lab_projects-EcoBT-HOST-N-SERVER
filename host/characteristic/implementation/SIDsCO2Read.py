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
import csv
import os.path
from datetime import datetime

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
        print "Peripheral No.", self.peripheralWorker.peripheral.number, "-" , "CO2 READING: ", hex_str
        value = self.instance._.value
        hour, minute, sec, LED00, LED01, LED10, LED11, amb0, amb1, rh, temp = struct.unpack("<BBBhhhhhhHH", value)
        print "Peripheral No.", self.peripheralWorker.peripheral.number, "-" , rh, temp
        rh = rh & 0xFFFC
        rh = -6.0 + (125.0 * rh) / 65536
        temp = temp & 0xFFFC
        temp = -46.85 + (175.72 * temp) / 65536

        print "Peripheral No.", self.peripheralWorker.peripheral.number, "-" , hour, minute, sec, LED00, LED01, LED10, LED11, amb0, amb1, rh, temp
        self.logToFile(hour, minute, sec, LED00, LED01, LED10, LED11, amb0, amb1, rh, temp)
        
        data = {
                'type': 'SIDsRead',
                'value': [hour, minute, sec, LED00, LED01, LED10, LED11, amb0, amb1, rh, temp]
                }
        
        self.peripheralWorker.delegateWorker.getQueue().put(data)
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
    def logToFile(self, hour, minute, sec, LED00, LED01, LED10, LED11, amb0, amb1, rh, temp):
        if not hasattr(self.service, 'log_file') or self.service.log_file == False: # try to open a file
            prefix = os.path.join(os.path.dirname(__file__), os.path.pardir, os.pardir, os.pardir, "data/log_")
            name = datetime.now().strftime("%Y%m%d%H%M%S_") + self.peripheralWorker.peripheral.side
            postfix = '.csv'
            fd = None
            if not os.path.exists(prefix + name + postfix):
                    fd = open(prefix + name + postfix, 'w')
                    self.service.log_file = fd
                    self.service.csvWriter = csv.writer(fd, delimiter=',')
                    self.service.csvWriter.writerow(["Time", "LED1PD1", "LED1PD2", "LED2PD1", "LED2PD2", "AMBIENT1", "AMBIENT2", "RH", "TEMP"])
            else:
                raise Exception
        if self.service.log_file != False:
            self.service.csvWriter.writerow([str(hour)+":"+str(minute)+":"+str(sec), LED00, LED01, LED10, LED11, amb0, amb1, rh, temp])
                
                
                
                
                
                
                
                
        
        