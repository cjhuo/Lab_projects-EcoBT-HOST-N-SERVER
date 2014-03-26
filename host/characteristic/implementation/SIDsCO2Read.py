'''
Created on Feb 9, 2013

@author: cjhuo
'''

from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *

import binascii
import struct
import csv
import os.path
from datetime import datetime
import math

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
        self.conv_params = {
#            'C': 1,
#            'Ref0': 700.0,
            'Tc': 12,
#            'b': 5.8,
            'S0A': 400,
            'o': -5.443,
            'p': -0.07764,
            'q': 4.472,
            'r': 0.07798,
            'm': 0,
            'n': 1,
        }
        self.didLoadByFile = False

    def conversion(self, PD1, PD2, AMB1, AMB2, T, RH):
        # Constants
#        C = self.conv_params['C']
#        Ref0 = self.conv_params['Ref0']
        Tc = self.conv_params['Tc']
#        b = self.conv_params['b']
        S0A = self.conv_params['S0A']
        o = self.conv_params['o']
        p = self.conv_params['p']
        q = self.conv_params['q']
        r = self.conv_params['r']
        m = self.conv_params['m']
        n = self.conv_params['n']
        PD1 = PD1 + 0.0
        PD2 = PD2 + 0.0
        AMB1 = AMB1 + 0.0
        AMB2 = AMB2 + 0.0
        print "PD1 ", PD1
        print "PD2 ", PD2
        print "AMB1 ", AMB1
        print "AMB2 ", AMB2
        # Conversion
#        S = PD1 - AMB1
#        print "S ", S
#        Ref = PD2 - AMB2
#        if Ref == 0:
#            Ref = 1
#        print "Ref ", Ref
#        d = (Ref0 - Ref) / Ref
#        print "d ", d
#        SC = S * (1 + d * C)
#        print "SC ", SC
#        SCT = SC + (T - 30) * Tc
#        print "SCT ", SCT
#        S0 = m + n * S0A
#        print "S0 ", S0
#        SCTN = S0 / SCT
#        print "SCTN ", SCTN
#        a = o + p * RH
#        print "a ", a
#        CO2 = a * math.exp(b * SCTN) # uint: percentage
#        print "CO2: ",  CO2
        SC = PD1 - AMB1
        print "SC ", SC
        SCT = SC + (T - 30) * Tc
        print "SCT ", SCT
        S0 = m + n * S0A
        print "S0 ", S0
        SCTN = SCT / S0
        print "SCTN ", SCTN
        a = o + p * (RH - 45)
        print "a ", a
        b = q + r * (RH - 45)
        print "b ", b
        CO2 = 1 + a * SCTN + b * SCTN * SCTN
        print "CO2: ", CO2
        return CO2

    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)
        print "CO2 READING: ", hex_str
        value = self.instance._.value
        hour, minute, sec, LED00, LED01, LED10, LED11, amb0, amb1, rh, temp = struct.unpack("<BBBhhhhhhHH", value)
        rh = rh & 0xFFFC
        rh = -6.0 + (125.0 * rh) / 65536
        temp = temp & 0xFFFC
        temp = -46.85 + (175.72 * temp) / 65536
        print "HUMIDITY and AMBIENT TEMP: ", rh, temp
        print "CO2 READINGS: ", LED00, LED01, LED10, LED11
        co2 = self.conversion(LED00, LED11, amb0, amb1, temp, rh)

        print hour, minute, sec, LED00, LED01, LED10, LED11, amb0, amb1, rh, temp
        self.logToFile(hour, minute, sec, LED00, LED01, LED10, LED11, amb0, amb1, rh, temp)

        data = {
                'type': 'SIDsRead',
                'value': [hour, minute, sec, LED00, LED01, LED10, LED11, amb0, amb1, rh, temp, co2]
                }

        self.peripheralWorker.delegateWorker.getQueue().put(data)
        data = {
            'type': 'CO2',
            'value': "%.2f" % co2
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

    def loadFile(self, address):
        if self.didLoadByFile:
            return
        print "try to load params from file"
        path = os.path.join(os.path.dirname(__file__),
            os.pardir,
            os.pardir,
            os.pardir,
            "webEngine/static/Uploads/")
        path = os.path.abspath(path)
        fname = "config_" + address + ".csv"
        fullpath = path + "/" + fname
        if os.path.isfile(fullpath):
            self.updateParamsByFile(fullpath)
            self.didLoadByFile = True

    def sendParamsToFrontend(self):
        data = {
            'type': 'CO2FormulaParams',
            'value': self.conv_params
        }
        self.peripheralWorker.delegateWorker.getQueue().put(data)

    def updateParamsByDict(self, params):
        print params
        for key in params:
            try:
                self.conv_params[key] = float(params[key])
            except:
                pass
        self.sendParamsToFrontend()

    def updateParamsByFile(self, fname):
        print "update params"
        with open(fname, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                sName = str(row[0])
                if sName in self.conv_params:
                    sValue = float(row[1])
                    self.conv_params[sName] = sValue
        self.sendParamsToFrontend()

    def logToFile(self, hour, minute, sec, LED00, LED01, LED10, LED11, amb0, amb1, rh, temp):
        if not (hasattr(self.service, 'enable_log') and self.service.enable_log):
            return
        if not hasattr(self.service, 'log_file') or self.service.log_file == False: # try to open a file
            prefix = os.path.join(os.path.dirname(__file__), os.path.pardir, os.pardir, os.pardir, "data/log_")
            name = datetime.now().strftime("%Y%m%d%H%M%S")
            postfix = '.csv'
            fd = None
            if not os.path.exists(prefix + name + postfix):
                for i in range(100):
                    print "create new log file"
                fd = open(prefix + name + postfix, 'w')
                self.service.log_file = fd
                self.service.csvWriter = csv.writer(fd, delimiter=',')
                self.service.csvWriter.writerow(["Time", "LED1PD1", "LED1PD2", "LED2PD1", "LED2PD2", "AMBIENT1", "AMBIENT2", "RH", "TEMP"])
            else:
                raise Exception
        if self.service.log_file != False:
            self.service.csvWriter.writerow([str(hour)+":"+str(minute)+":"+str(sec), LED00, LED01, LED10, LED11, amb0, amb1, rh, temp])










