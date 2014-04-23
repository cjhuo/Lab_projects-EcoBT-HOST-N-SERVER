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
import os
import csv

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
        value = self.instance._.value
        self.start, self.LED_ready, self.PD0, self.PD1, self.RH_T_ready, self.RH_T_enable = struct.unpack("<BBBBBB", value)
        print "CO2 STATUS: LED(%d) PD0(%d) PD1(%d) RHT(%d)" % (self.LED_ready, self.PD0, self.PD1, self.RH_T_ready)
        #print self.start, self.LED_ready, self.PD0, self.PD1, self.RH_T_ready, self.RH_T_enable
        if int(self.start) == 0 and int(self.LED_ready) == 1 and int(self.PD0) == 1 and \
                                    int(self.PD1) == 1 and int(self.RH_T_ready) == 1 and int(self.RH_T_enable) == 1: # correct initial state
            self.state = STOP_FLAG
            #self.startSIDs()
        elif int(self.start) == 1:
            self.state = START_FLAG

        if self.peripheralWorker.peripheral.type != 'SIDs':
            self.peripheralWorker.peripheral.type = 'SIDs'
        # send a message to UI
        self.sendState()
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

    def sendState(self):
        data = {'type': 'SIDs',
        'value': {'type': 'state',
                  'value': self.state # stopped == ready signal
                  }
        }
        self.peripheralWorker.delegateWorker.getQueue().put(data)

    def startSIDs(self):
        byte_array = struct.pack("<BBBBBB", 1, 1, 1, 1, 1, 1)
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        self.peripheralWorker.writeValueForCharacteristic(val_data, self)
        if hasattr(self.service, 'log_file'):
            self.service.log_file = False
        self.service.enable_log = True
        self.sendState()

    def stopSIDs(self):
        byte_array = struct.pack("<BBBBBB", 0, 1, 1, 1, 1, 1)
        val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
        self.peripheralWorker.writeValueForCharacteristic(val_data, self)
        self.sendState()

        # open the data folder
        # dataPath = os.path.join(os.path.dirname(__file__), os.path.pardir, os.pardir, os.pardir, "data")
        # os.system('open "%s"' % dataPath)

    def createLogFile(self, timestamp):
        self.service.enable_log = True
        if not hasattr(self.service, 'log_co2') or self.service.log_co2 == False:
            prefix = os.path.join(os.path.dirname(__file__), os.path.pardir, os.pardir, os.pardir, "data/log_co2_")
            name = timestamp.strftime("%Y%m%d%H%M%S")
            postfix = ".csv"
            fd = None
            fname = prefix + name + postfix
            if not os.path.exists(fname):
                fd = open(fname, 'w')
                self.service.log_co2 = fd
                self.service.csvWriter_co2 = csv.writer(fd, delimiter=',')
                self.service.csvWriter_co2.writerow(
                    ["Time", "LED1PD1", "LED1PD2", "LED2PD1", "LED2PD2", "AMBIENT1", "AMBIENT2", "RH", "TEMP", "CO2"])
            else:
                raise Exception

    def closeLogFile(self):
        self.service.enable_log = False
        if hasattr(self.service, 'log_co2'):
            self.service.log_co2.flush()
            self.service.log_co2.close()
            self.service.log_co2 = False
            self.service.csvWriter_co2 = None

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
