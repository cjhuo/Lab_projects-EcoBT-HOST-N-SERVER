'''
Created on Feb 5, 2013

@author: cjhuo

@summary:
monitor the input queue where command sent from UI is stored, and send to where the worker belongs to
A EcoBTPeripheralWorker delegate has members as below:
instance of peripheral,
instance of peripheral delegate,
'''
from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *

import array
import binascii
import struct

from EcoBTWorker import EcoBTWorker
from EcoBTPeripheralDelegateWorker import EcoBTPeripheralDelegateWorker

from datetime import datetime
import time

class EcoBTPeripheralWorker(NSObject, EcoBTWorker):
    def init(self):
        EcoBTWorker.__init__(self)
        self.peripheral = None
        self.delegateWorker = EcoBTPeripheralDelegateWorker()
        print "Initialize Peripheral Worker"
        self.record_cnt = 1
        self.fd = None
        self.status = None
        self.data_prefix = None
        return self

    def setSockets(self, sockets):
        self.sockets = sockets
        self.delegateWorker.setGlobalSockets(sockets)

    def stop(self):
        self.delegateWorker.getQueue().put('stop')
        self.delegateWorker.join()

    def discoverServices(self):
        self.peripheral.discoverServices_(None)


    # CBPeripheral delegate methods
    def peripheral_didDiscoverServices_(self, peripheral, error):
        for service in peripheral._.services:
            print "Service found with UUID: ", service._.UUID
            if service._.UUID == CBUUID.UUIDWithString_("180D"):
                print "UUID Matched!!"
                peripheral.discoverCharacteristics_forService_(nil, service)
            elif service._.UUID == CBUUID.UUIDWithString_("180A"):
                print "%s Found!!" % service._.UUID
                peripheral.discoverCharacteristics_forService_(nil, service)
            elif service._.UUID == CBUUID.UUIDWithString_("FF10"):#LED lights
                print "%s Found!!" % service._.UUID
                peripheral.discoverCharacteristics_forService_(nil, service)
            elif service._.UUID == CBUUID.UUIDWithString_("FF20"):#Real Time Clock
                print "%s Found!!" % service._.UUID
                peripheral.discoverCharacteristics_forService_(nil, service)
            elif service._.UUID == CBUUID.UUIDWithString_("FFA0"):#ACC
                print "%s Found!!" % service._.UUID
                peripheral.discoverCharacteristics_forService_(nil, service)
            elif service._.UUID == CBUUID.UUIDWithString_("FE10"):#humidity&temperature
                print "%s Found!!" % service._.UUID
                peripheral.discoverCharacteristics_forService_(nil, service)
            elif service._.UUID == CBUUID.UUIDWithString_("FEC0"):#ECG
                print "%s Found!!" % service._.UUID
                peripheral.discoverCharacteristics_forService_(nil, service)
            else:
                pass

    def peripheral_didDiscoverCharacteristicsForService_error_(self,
                                                               peripheral,
                                                               service,
                                                               error):
        print "didDiscoverCharacteristicsForService"
        # ECO BT DEFAULT PROFILE
        if service._.UUID == CBUUID.UUIDWithString_("180D"):
            for char in service._.characteristics:
                NSLog("%@", char._.UUID)
                peripheral.readValueForCharacteristic_(char)
        # DEVINO PROFILE
        if service._.UUID == CBUUID.UUIDWithString_("180A"):
            for char in service._.characteristics:
                NSLog("%@", char._.UUID)
                peripheral.readValueForCharacteristic_(char)
        # EPL LED PROFILE
        if service._.UUID == CBUUID.UUIDWithString_("FF10"):
            for char in service._.characteristics:
                NSLog("%@", char._.UUID)
                peripheral.readValueForCharacteristic_(char)
        # EPL RTC ROFILE
        if service._.UUID == CBUUID.UUIDWithString_("FF20"):
            for char in service._.characteristics:
                NSLog("%@", char._.UUID)
                peripheral.readValueForCharacteristic_(char)
        # EPL ECG ROFILE
        if service._.UUID == CBUUID.UUIDWithString_("FEC0"):
            notify_list = []
            notify_list.append(CBUUID.UUIDWithString_("FEC2"))
            notify_list.append(CBUUID.UUIDWithString_("FEC6"))
            notify_list.append(CBUUID.UUIDWithString_("FEC7"))
#            notify_list.append(CBUUID.UUIDWithString_("FEC8"))
            for char in service._.characteristics:
                NSLog("%@", char._.UUID)
                if char._.UUID in notify_list:
                    print "Set Notify for ", char._.UUID
                    peripheral.setNotifyValue_forCharacteristic_(True, char)
                else:
                    peripheral.readValueForCharacteristic_(char)
        # SIDS SHT25 PROFILE
        if service._.UUID == CBUUID.UUIDWithString_("FE10"):
            for char in service._.characteristics:
                NSLog("%@", char._.UUID)
                notify_list = []
                notify_list.append(CBUUID.UUIDWithString_("FE11"))
                notify_list.append(CBUUID.UUIDWithString_("FE13"))
                if char._.UUID in notify_list:
                    print "Set Notify for ", char._.UUID
                    peripheral.setNotifyValue_forCharacteristic_(True, char)
                if char._.UUID == CBUUID.UUIDWithString_("FE11") or\
                   char._.UUID == CBUUID.UUIDWithString_("FE12") or\
                   char._.UUID == CBUUID.UUIDWithString_("FE13"):
                    peripheral.readValueForCharacteristic_(char)
        # EPL ACC. PROFILE
        if service._.UUID == CBUUID.UUIDWithString_("FFA0"):
            print "discovering chars"
            for char in service._.characteristics:
                NSLog("%@", char._.UUID)
                notify_list = []
                notify_list.append(CBUUID.UUIDWithString_("FFA3"))
                notify_list.append(CBUUID.UUIDWithString_("FFA4"))
                notify_list.append(CBUUID.UUIDWithString_("FFA5"))
                notify_list.append(CBUUID.UUIDWithString_("FFA6"))
                if char._.UUID in notify_list:
                    print "Set Notify for ", char._.UUID
                    peripheral.setNotifyValue_forCharacteristic_(True, char)
                if char._.UUID == CBUUID.UUIDWithString_("FFA1"):
                    peripheral.readValueForCharacteristic_(char)

    def peripheral_didUpdateValueForCharacteristic_error_(self,
                                                          peripheral,
                                                          characteristic,
                                                          error):
#        print "Read Characteristic(%s) value" % characteristic._.UUID
        if characteristic._.UUID == CBUUID.UUIDWithString_("2a23"):
            hex_str = binascii.hexlify(characteristic._.value)
            print "180A Profile?(%s) %s" % (characteristic._.UUID, hex_str)

        # ECO ECG PROFILE
        data_prefix = 0
        data = None
        if characteristic._.UUID == CBUUID.UUIDWithString_("FEC1"): # info
            hex_str = binascii.hexlify(characteristic._.value)
            print "CHAR(%s) %s" % (characteristic._.UUID, hex_str)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FEC2"): # status
            hex_str = binascii.hexlify(characteristic._.value)
            print "CHAR(%s) %s" % (characteristic._.UUID, hex_str)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FEC3"): # config1
            hex_str = binascii.hexlify(characteristic._.value)
            print "CHAR(%s) %s" % (characteristic._.UUID, hex_str)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FEC4"): # config2
            value = characteristic._.value
            config2 = struct.unpack("13B", value)
            t = []
            for e in config2:
                t.append(e)
            t[2] = 0x00 # turn off lead off detection
            data = struct.pack("13B", t[0], t[1], t[2],t[3], t[4], t[5],t[6],t[7],
                                      t[8], t[9], t[10],t[11], t[12])
            val_data = NSData.dataWithBytes_length_(data, len(data))
#            peripheral.writeValue_forCharacteristic_type_(
#                val_data, characteristic,
#                CBCharacteristicWriteWithResponse)
            hex_str = binascii.hexlify(characteristic._.value)
            print "CHAR(%s) %s" % (characteristic._.UUID, hex_str)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FEC5"): # start ECG to record/read data
            value = characteristic._.value
            (start,) = struct.unpack("@B", value)
            if start == 0x00:
                #time.sleep(3)
                print "START ECG RECORD"
                data = struct.pack("@B", 0x01)
                val_data = NSData.dataWithBytes_length_(data, len(data))
                peripheral.writeValue_forCharacteristic_type_(
                    val_data, characteristic,
                    CBCharacteristicWriteWithResponse)
            if start == 0x01:
                print "STOP ECG, READ ECG DATA"
                # stop ecg
                data = struct.pack("@B", 0x00)
                val_data = NSData.dataWithBytes_length_(data, len(data))
                peripheral.writeValue_forCharacteristic_type_(
                    val_data, characteristic,
                    CBCharacteristicWriteWithResponse)
                # read ecg from sd card
                data = struct.pack("@B", 0x11)
                val_data = NSData.dataWithBytes_length_(data, len(data))
                peripheral.writeValue_forCharacteristic_type_(
                    val_data, characteristic,
                    CBCharacteristicWriteWithResponse)
                self.fd = open("log.txt", 'w')
                self.record_cnt = 1
            if start == 0x11:
                print "READING ECG DATA"
                self.record_cnt = 1
        if characteristic._.UUID == CBUUID.UUIDWithString_("FEC6"): # data1
            hex_str = binascii.hexlify(characteristic._.value)
            print "%s" % hex_str
            value = characteristic._.value
            ret = struct.unpack("16B", value)
            self.data_prefix = ret[0]
            (temp,) = struct.unpack(">I", chr(ret[1]) + chr(ret[2]) + chr(ret[3]) + chr(0))
            self.status = temp >> 8
            (temp,) = struct.unpack(">i", chr(ret[4]) + chr(ret[5]) + chr(ret[6]) + chr(0))
            self.V6 = temp >> 8
            (temp,) = struct.unpack(">i", chr(ret[7]) + chr(ret[8]) + chr(ret[9]) + chr(0))
            self.LeadI = temp >> 8
            (temp,) = struct.unpack(">i", chr(ret[10]) + chr(ret[11]) + chr(ret[12]) + chr(0))
            self.LeadII = temp >> 8
            (temp,) = struct.unpack(">i", chr(ret[13]) + chr(ret[14]) + chr(ret[15]) + chr(0))
            self.V2 = temp >> 8
            self.LeadIII = self.LeadII - self.LeadI
            self.aVR = 0 - ((self.LeadI + self.LeadII) / 2)
            self.aVL = self.LeadI - (self.LeadII / 2)
            self.aVF = self.LeadII - (self.LeadI / 2)

        if characteristic._.UUID == CBUUID.UUIDWithString_("FEC7"): # data2
            value = characteristic._.value
            ret = struct.unpack("16B", value)
            if self.data_prefix != None and self.data_prefix == ret[0]:
                data_prefix = ret[0]
            else:
                print "miss match"
                return
            (temp,) = struct.unpack(">i", chr(ret[1]) + chr(ret[2]) + chr(ret[3]) + chr(0))
            self.V3 = temp >> 8
            (temp,) = struct.unpack(">i", chr(ret[4]) + chr(ret[5]) + chr(ret[6]) + chr(0))
            self.V4 = temp >> 8
            (temp,) = struct.unpack(">i", chr(ret[7]) + chr(ret[8]) + chr(ret[9]) + chr(0))
            self.V5 = temp >> 8
            (temp,) = struct.unpack(">i", chr(ret[10]) + chr(ret[11]) + chr(ret[12]) + chr(0))
            self.V1 = temp >> 8
            output = ""
            if self.status != None:
                output += "Record  number       : %8d            status: %06X\n" % (self.record_cnt ,self.status)
            output += " V1: %8d  V2: %8d  V3: %8d    V4: %8d     V5: %8d      V6: %8d\n" % (self.V1, self.V2, self.V3, self.V4, self.V5, self.V6)
            output += "aVR: %8d aVL: %8d aVF: %8d LeadI: %8d LeadII: %8d LeadIII: %8d\n" % (self.aVR, self.aVL, self.aVF, self.LeadI, self.LeadII, self.LeadIII)
            if self.fd == None:
                self.fd = open("log.txt", 'w')
            if self.record_cnt % 100 == 1:
                print output
            self.fd.write(output)
            self.record_cnt = self.record_cnt + 1
            self.data_prefix = None

        if characteristic._.UUID == CBUUID.UUIDWithString_("FEC8"): # data info
            value = characteristic._.value
            start_time = value[:8]
            end_time   = value[8:]
            year, month, day, wday, hour, minute, second = struct.unpack("<HBBBBBB", start_time)
            try:
                rtc_time = datetime(year = year, month = month, day = day, hour = hour, minute = minute, second = second)
                print "ECG Record Start Time", rtc_time
            except:
                # if the RTC is not set, then the values are 0s
                pass
            year, month, day, wday, hour, minute, second = struct.unpack("<HBBBBBB", end_time)
            try:
                rtc_time = datetime(year = year, month = month, day = day, hour = hour, minute = minute, second = second)
                print "ECG Record End Time", rtc_time
            except:
                # if the RTC is not set, then the values are 0s
                pass
        # SIDS SHT25 PROFILE
        sht25_enable = False
        if characteristic._.UUID == CBUUID.UUIDWithString_("FE11"):
            hex_str = binascii.hexlify(characteristic._.value)
            print "CO2 STATUS\t", hex_str
            status = struct.pack("<BBBBBB", 1, 0, 0, 0, 0, 1)
            val_data = NSData.dataWithBytes_length_(status, len(status))
            peripheral.writeValue_forCharacteristic_type_(
                val_data, characteristic,
                CBCharacteristicWriteWithResponse)
#            value = int(hex_str, base=16)
#            if value == 1:
#                sht25_enable = True
#            print "SIDS SHT25 ENABLE?(%s) %s" % (characteristic._.UUID, sht25_enable)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FE12"):
            hex_str = binascii.hexlify(characteristic._.value)
            print "CO2 PARAM\t", hex_str
#            value = int(hex_str, base=16)
#            print "SIDS SHT25 RATE?(%s) %d sec" % (characteristic._.UUID, value)
#            byte_array = array.array('b', chr(2))
#            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
#            peripheral.writeValue_forCharacteristic_type_(
#                val_data, characteristic,
#                CBCharacteristicWriteWithResponse)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FE13"):
            hex_str = binascii.hexlify(characteristic._.value)
            print "CO2 READING\t", hex_str
#            value = int(hex_str, base=16)
#            print "SIDS SHT25 START?(%s) %d" % (characteristic._.UUID, value)
#            if value == 0:
#                print "START SIDS SHT25 Sensor"
#                byte_array = array.array('b', chr(1))
#                val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
#                peripheral.writeValue_forCharacteristic_type_(
#                    val_data, characteristic,
#                    CBCharacteristicWriteWithResponse)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FE14"):
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str[:-2], base=16)
            value = value & 0xFFFC
            temp = -46.85 + (175.72 * value) / 65536
            print "SIDS SHT25 TEMP READING?(%s) %.2f" % (characteristic._.UUID, temp)
            data = {'type': 'temperature', 'value': round(temp, 2)}
            self.delegateWorker.getQueue().put(data)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FE15"):
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str[:-2], base=16)
            value = value & 0xFFFC
            humid = -6.0 +  (125.0 * value) / 65536
            print "SIDS SHT25 HUMID READING?(%s) %.2f" % (characteristic._.UUID, humid)
            data = {'type': 'humidity', 'value': round(humid,2)}
            self.delegateWorker.getQueue().put(data)
        # EPL LED PROFILE
        if characteristic._.UUID == CBUUID.UUIDWithString_("FF11"): #LED 0(RED) state 0: off 1: on 2: blink
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str, base=16)
            print "CHAR(%s) %d" % (characteristic._.UUID, value)
            byte_array = array.array('b', chr(0))
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            peripheral.writeValue_forCharacteristic_type_(
                val_data, characteristic,
                CBCharacteristicWriteWithResponse)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FF12"): # LED 1(GREEN) state 0: off 1: on 2: blink
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str, base=16)
            print "CHAR(%s) %d" % (characteristic._.UUID, value)
            byte_array = array.array('b', chr(0))
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            peripheral.writeValue_forCharacteristic_type_(
                val_data, characteristic,
                CBCharacteristicWriteWithResponse)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FF13"): # LED 0(RED) blink toggle interval (0.1 sec)
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str, base=16)
            print "CHAR(%s) %d %s" % (characteristic._.UUID, value, hex_str)
            byte_array = array.array('b', chr(1))
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            peripheral.writeValue_forCharacteristic_type_(
                val_data, characteristic,
                CBCharacteristicWriteWithResponse)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FF14"): # LED 1(Green) blink toggle intrval (0.1 sec)
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str, base=16)
            print "CHAR(%s) %d %s" % (characteristic._.UUID, value, hex_str)
            byte_array = array.array('b', chr(2))
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            peripheral.writeValue_forCharacteristic_type_(
                val_data, characteristic,
                CBCharacteristicWriteWithResponse)
        # EPL RTC PROFILE
        if characteristic._.UUID == CBUUID.UUIDWithString_("FF21"): # RTC Set Time
            value = characteristic._.value
            year, month, day, wday, hour, minute, second = struct.unpack("<HBBBBBB", value)
            print "EPL RTC Set Time ", year, month, day, wday, hour, minute, second
            now = datetime.now()
            print now
            timestamp = struct.pack("<HBBBBBB", now.year, now.month, now.day, now.isoweekday(), now.hour, now.minute, now.second)
            val_data = NSData.dataWithBytes_length_(timestamp, len(timestamp))
            peripheral.writeValue_forCharacteristic_type_(
                val_data, characteristic,
                CBCharacteristicWriteWithResponse)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FF22"): # RTC Get Time, not auto-notify
            value = characteristic._.value
            year, month, day, wday, hour, minute, second = struct.unpack("<HBBBBBB", value)
            try:
                rtc_time = datetime(year = year, month = month, day = day, hour = hour, minute = minute, second = second)
                print "EPL RTC Get Time", rtc_time
            except:
                # if the RTC is not set, then the values are 0s
                pass
        # EPL ACC PROFILE
        if characteristic._.UUID == CBUUID.UUIDWithString_("FFA1"):
            hex_str = binascii.hexlify(characteristic._.value)
            acc_enable = int(hex_str, base=16)
            if acc_enable == 0:
                print "Enable ACC"
                byte_array = array.array('b', chr(1))
            else:
                print "Disable ACC"
                byte_array = array.array('b', chr(0))
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            peripheral.writeValue_forCharacteristic_type_(
                val_data, characteristic,
                CBCharacteristicWriteWithResponse)
        """
        if characteristic._.UUID == CBUUID.UUIDWithString_("FFA3"):
            hex_str = binascii.hexlify(characteristic._.value)
            print "ACC X: %3d\t" % int(hex_str, base=16),
        if characteristic._.UUID == CBUUID.UUIDWithString_("FFA4"):
            hex_str = binascii.hexlify(characteristic._.value)
            print "ACC Y: %3d\t" % int(hex_str, base=16),
        if characteristic._.UUID == CBUUID.UUIDWithString_("FFA5"):
            hex_str = binascii.hexlify(characteristic._.value)
            print "ACC Z: %3d" % int(hex_str, base=16)
        """
        import math
        if characteristic._.UUID == CBUUID.UUIDWithString_("FFA6"):
            value = characteristic._.value
            hex_str = binascii.hexlify(value)
            x, y, z = struct.unpack("<hhh", value) #only first 12bit is valid according to data sheet
            x = (0.0 + (x >> 4))  / 1000
            y = (0.0 + (y >> 4)) / 1000
            z = (0.0 + (z >> 4)) / 1000
            x = 1.0 if x>1.0 else x
            x = -1.0 if x<-1.0 else x
            y = 1.0 if y>1.0 else y
            y = -1.0 if y<-1.0 else y
            z = 1.0 if z>1.0 else z
            z = -1.0 if z<-1.0 else z

            print "X: % .3fg Y: % .3fg Z: % .3fg" % (x, y, z)
            '''
            x = math.atan2(x, math.sqrt(y*y+z*z))
            data = ('x', x)
            self.worker.getQueue().put(data)

            z = math.atan2(y, math.sqrt(x*x+z*z))
            data = ('z', z)
            self.worker.getQueue().put(data)
            '''
            '''
            if x<0 and z<0:
                x = -math.asin(x)-3.141592
            elif x>0 and z<0:
                x = 3.141592 - math.asin(x)
            else:
                x = math.asin(x)
            data = {'type': 'orientation', 'axis': 'x', 'value': x}
            self.delegateWorker.getQueue().put(data)
            '''

            #x = math.asin(x)
            data = {'type': 'orientation',
                    'value': { 'x': x,
                               'y': y,
                               'z': z
                              }
                    }
            #data = {'type': 'orientation', 'axis': 'x', 'value': x}
            self.delegateWorker.getQueue().put(data)
            #y = math.asin(y)
            #data = {'type': 'orientation', 'axis': 'y', 'value': y}
            #self.delegateWorker.getQueue().put(data)
            #z = math.acos(z)
            #data = {'type': 'orientation', 'axis': 'z', 'value': z}
            #self.delegateWorker.getQueue().put(data)

    '''
    def peripheral_didUpdateValueForCharacteristic_error_(self,
                                                          peripheral,
                                                          characteristic,
                                                          error):
#        print "Read Characteristic(%s) value" % characteristic._.UUID
        if characteristic._.UUID == CBUUID.UUIDWithString_("FFA1"):
            hex_str = binascii.hexlify(characteristic._.value)
            acc_enable = int(hex_str, base=16)
            if acc_enable == 0:
                print "Enable ACC"
                byte_array = array.array('b', chr(1))
            else:
                print "Disable ACC"
                byte_array = array.array('b', chr(0))
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            peripheral.writeValue_forCharacteristic_type_(
                val_data, characteristic,
                CBCharacteristicWriteWithResponse)
        # FFA3: x, FFA4: y, FFA5: z
        if characteristic._.UUID == CBUUID.UUIDWithString_("FFA3") or\
           characteristic._.UUID == CBUUID.UUIDWithString_("FFA4") or\
           characteristic._.UUID == CBUUID.UUIDWithString_("FFA5"):
            hex_str = binascii.hexlify(characteristic._.value)
            print characteristic._.UUID, hex_str, int(hex_str, base=16)

            # put data into queue
            if characteristic._.UUID == CBUUID.UUIDWithString_("FFA3"):
                data = ('x', int(hex_str, base=16))
                self.worker.getQueue().put(data)
            elif characteristic._.UUID == CBUUID.UUIDWithString_("FFA4"):
                data = ('y', int(hex_str, base=16))
                self.worker.getQueue().put(data)
            elif characteristic._.UUID == CBUUID.UUIDWithString_("FFA5"):
                data = ('z', int(hex_str, base=16))
                self.worker.getQueue().put(data)
    #def setData(self, data):
    '''

    def setWorker(self, worker):
        self.worker = worker
        print worker
        #self.worker.getQueue().put('This is a test')

    def peripheral_didWriteValueForCharacteristic_error_(self,
                                                         peripheral,
                                                         characteristic,
                                                         error):
        hex_str = binascii.hexlify(characteristic._.value)
        value = int(hex_str, base=16)
        print "CHAR(%s) is updated" % (characteristic._.UUID)

    def peripheral_didUpdateNotificationStateForCharacteristic_error_(self,
                                                                      peripheral,
                                                                      characteristic,
                                                                      error):
        print "char(" + str(characteristic._.UUID) + ") is auto-notify? " + str(characteristic.isNotifying())

