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

class EcoBTPeripheralWorker(NSObject, EcoBTWorker):
    def init(self):
        EcoBTWorker.__init__(self)
        self.delegateWorker = EcoBTPeripheralDelegateWorker()
        #self.delegateWorker.start()
        self.sockets = None
        self.peripheral = None
        self.delegate = None
        print "Initialize Peripheral Worker"
        return self        
        
    def stop(self):
        self.delegateWorker.running.value = 0

    def discoverServices(self):
        self.peripheral.discoverServices_(None)
        
        
    # CBPeripheral delegate methods
    def peripheral_didDiscoverServices_(self, peripheral, error):
        for service in peripheral._.services:
            print "Service found with UUID: ", service._.UUID
            if service._.UUID == CBUUID.UUIDWithString_("180D"):
                print "UUID Matched!!"
                peripheral.discoverCharacteristics_forService_(nil, service)
            elif service._.UUID == CBUUID.UUIDWithString_("FF10"):#LED lights
                print "%s Found!!" % service._.UUID
                peripheral.discoverCharacteristics_forService_(nil, service)
            elif service._.UUID == CBUUID.UUIDWithString_("FFA0"):#ACC
                print "%s Found!!" % service._.UUID
                peripheral.discoverCharacteristics_forService_(nil, service)
            elif service._.UUID == CBUUID.UUIDWithString_("FE10"):#humidity&temperature
                print "%s Found!!" % service._.UUID
                peripheral.discoverCharacteristics_forService_(nil, service)
            else:
                pass

    def peripheral_didDiscoverCharacteristicsForService_error_(self,
                                                               peripheral,
                                                               service,
                                                               error):
        print "didDiscoverCharacteristicsForService"
        if service._.UUID == CBUUID.UUIDWithString_("180D"):
            for char in service._.characteristics:
                NSLog("%@", char._.UUID)
                peripheral.readValueForCharacteristic_(char)
        if service._.UUID == CBUUID.UUIDWithString_("FF10"):
            for char in service._.characteristics:
                NSLog("%@", char._.UUID)
                peripheral.readValueForCharacteristic_(char)
        # SIDS SHT25 PROFILE
        if service._.UUID == CBUUID.UUIDWithString_("FE10"):
            for char in service._.characteristics:
                NSLog("%@", char._.UUID)
                notify_list = []
                notify_list.append(CBUUID.UUIDWithString_("FE14"))
                notify_list.append(CBUUID.UUIDWithString_("FE15"))
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
        # SIDS SHT25 PROFILE
        sht25_enable = False
        if characteristic._.UUID == CBUUID.UUIDWithString_("FE11"):
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str, base=16)
            if value == 1:
                sht25_enable = True
            print "SIDS SHT25 ENABLE?(%s) %s" % (characteristic._.UUID, sht25_enable)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FE12"):
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str, base=16)
            print "SIDS SHT25 RATE?(%s) %d sec" % (characteristic._.UUID, value)
            byte_array = array.array('b', chr(2))
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            peripheral.writeValue_forCharacteristic_type_(
                val_data, characteristic,
                CBCharacteristicWriteWithResponse)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FE13"):
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str, base=16)
            print "SIDS SHT25 START?(%s) %d" % (characteristic._.UUID, value)
            if value == 0:
                print "START SIDS SHT25 Sensor"
                byte_array = array.array('b', chr(1))
                val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
                peripheral.writeValue_forCharacteristic_type_(
                    val_data, characteristic,
                    CBCharacteristicWriteWithResponse)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FE14"):
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str[:-2], base=16)
            value = value & 0xFFFC
            temp = -46.85 + (175.72 * value) / 65536
            print "SIDS SHT25 TEMP READING?(%s) %.2f" % (characteristic._.UUID, temp)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FE15"):
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str[:-2], base=16)
            value = value & 0xFFFC
            humid = -6.0 +  (125.0 * value) / 65536
            print "SIDS SHT25 HUMID READING?(%s) %.2f" % (characteristic._.UUID, humid)
        # EPL LED PROFILE
        if characteristic._.UUID == CBUUID.UUIDWithString_("FF11"):
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str, base=16)
            print "CHAR(%s) %d" % (characteristic._.UUID, value)
            byte_array = array.array('b', chr(0))
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            peripheral.writeValue_forCharacteristic_type_(
                val_data, characteristic,
                CBCharacteristicWriteWithResponse)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FF12"):
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str, base=16)
            print "CHAR(%s) %d" % (characteristic._.UUID, value)
            byte_array = array.array('b', chr(0))
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            peripheral.writeValue_forCharacteristic_type_(
                val_data, characteristic,
                CBCharacteristicWriteWithResponse)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FF13"):
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str, base=16)
            print "CHAR(%s) %d %s" % (characteristic._.UUID, value, hex_str)
            byte_array = array.array('b', chr(1))
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            peripheral.writeValue_forCharacteristic_type_(
                val_data, characteristic,
                CBCharacteristicWriteWithResponse)
        if characteristic._.UUID == CBUUID.UUIDWithString_("FF14"):
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str, base=16)
            print "CHAR(%s) %d %s" % (characteristic._.UUID, value, hex_str)
            byte_array = array.array('b', chr(2))
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            peripheral.writeValue_forCharacteristic_type_(
                val_data, characteristic,
                CBCharacteristicWriteWithResponse)
        # EPL ACC PROFILE
        if characteristic._.UUID == CBUUID.UUIDWithString_("FFA1"):
            hex_str = binascii.hexlify(characteristic._.value)
            acc_enable = int(hex_str, base=16)
            if acc_enable == 0:
                print "Enable ACC"
                byte_array = array.array('b', chr(1))
            else:
                print "Disable ACC"
                byte_array = array.array('b', chr(1))
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
            
            if x<0 and z<0:
                x = -math.asin(x)-3.141592
            elif x>0 and z<0:
                x = 3.141592 - math.asin(x)
            else:   
                x = math.asin(x)
            data = ('x', x)
            self.delegateWorker.getQueue().put(data)
            
            '''
            x = math.asin(x)
            data = ('x', x)
            self.worker.getQueue().put(data)
            y = math.asin(y)
            data = ('y', y)
            self.worker.getQueue().put(data)
            z = math.acos(z)
            data = ('z', z)
            self.worker.getQueue().put(data)
            '''
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

