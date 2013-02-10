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
from Service import *
from characteristic import characteristicFactory
from characteristic.implementation import Characteristic

class EcoBTPeripheralWorker(NSObject, EcoBTWorker):
    def init(self):
        EcoBTWorker.__init__(self)
        self.peripheral = None
        self.services = []
        self.delegateWorker = EcoBTPeripheralDelegateWorker()
        print "Initialize Peripheral Worker"
        return self        

    def setSockets(self, sockets):
        self.sockets = sockets
        self.delegateWorker.setGlobalSockets(sockets)
        
    def stop(self):
        self.delegateWorker.getQueue().put('stop')
        self.delegateWorker.join()

    def discoverServices(self):
        self.peripheral.discoverServices_(None)

    def setWorker(self, worker):
        self.worker = worker
        print worker
        #self.worker.getQueue().put('This is a test')
        
    def discoverCharacteristics_forService(self, service):
        if type(service) == Service:
            self.peripheral.discoverCharacteristics_forService_(nil, service.instance)
        else:
            self.peripheral.discoverCharacteristics_forService_(nil, service)
        
    def readValueForCharacteristic(self, characteristic):
        if isinstance(characteristic, Characteristic.Characteristic):
            self.peripheral.readValueForCharacteristic_(characteristic.instance)
        else:
            self.peripheral.readValueForCharacteristic_(characteristic)
        
    def setNotifyValueForCharacteristic(self, flag, characteristic):
        if isinstance(characteristic, Characteristic.Characteristic):
            self.peripheral.setNotifyValue_forCharacteristic_(flag, characteristic.instance)
        else:
            self.peripheral.setNotifyValue_forCharacteristic_(flag, characteristic)
            
    def writeValueForCharacteristic(self, value, characteristic):
        if isinstance(characteristic, Characteristic.Characteristic):
            self.peripheral.writeValue_forCharacteristic_type_(
                                                               value, characteristic.instance,
                                                               CBCharacteristicWriteWithResponse)
        else:
            self.peripheral.writeValue_forCharacteristic_type_(
                                                               value, characteristic,
                                                               CBCharacteristicWriteWithResponse)
            
    def findServiceByUUID(self, UUID):
        for s in self.services:
            if s.UUID == UUID:
                return s
        raise Exception # didn't find any service
        
    def findCharacteristicByUUID(self, UUID):
        for s in self.services:
            for c in s.characteristics:
                if UUID == c.UUID:
                    return c
        raise Exception
    
    def appendService(self, service):
        uuid = self.checkUUID(service._.UUID)
        if uuid != None:
            s = Service()
            s.setUUID(uuid)
            s.instance = service
            self.services.append(s) # append to service list for tracking from UI   
        else:
            pass # found a service profile not listed in IOBluetooth.py
        
    def appendCharacteristicForService(self, characteristic, service, peripheral):
        c = characteristicFactory.createCharacteristic(self.checkUUID(characteristic._.UUID), characteristic, peripheral)
        # Characteristic that has read&write and system infor needs to be read at the beginning         
        if c.privilege == 1 or c.privilege == 2: 
            self.readValueForCharacteristic(c)
        service.characteristics.append(c)
    
    def checkUUID(self, UUID):
        for p in ProfileList:
            if UUID == CBUUID.UUIDWithString_(p):
                #peripheral.discoverCharacteristics_forService_(nil, service)
                return p  
        # does not raise exception now to ignore discovery of profiles 'Generic Access Profile' and 'Generic Attribute Profile'
        # raise Exception # didn't find any UUID
        return None
    
    # for the purpose of test, enable some certain characteristic(s) at the starting point
    def initCharacteristicWhenDiscovered(self, uuid):
        if uuid == "FFA0": # enable ACC
            c = self.findCharacteristicByUUID("FFA1")
            byte_array = array.array('b', chr(1))
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            self.writeValueForCharacteristic(val_data, c)
        if uuid == "FE10":
            c = self.findCharacteristicByUUID("FE12") # set SIDs update frequency at 0.5Hz
            byte_array = array.array('b', chr(2)) 
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            self.writeValueForCharacteristic(val_data, c)
            c = self.findCharacteristicByUUID("FE13")
            byte_array = array.array('b', chr(1))
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            self.writeValueForCharacteristic(val_data, c)
        
    # CBPeripheral delegate methods
    def peripheral_didDiscoverServices_(self, peripheral, error):
        for service in peripheral._.services:
            print "Service found with UUID: ", service._.UUID
            self.appendService(service)
            
            # for test
            self.discoverCharacteristics_forService(service)
        
        # inform UI!

    def peripheral_didDiscoverCharacteristicsForService_error_(self,
                                                               peripheral,
                                                               service,
                                                               error):
        print "didDiscoverCharacteristicsForService"
        uuid = self.checkUUID(service._.UUID)
        if uuid != None:
            s = self.findServiceByUUID(uuid)
            for char in service._.characteristics:
                #print char._.UUID
                if (self.checkUUID(char._.UUID)) != None:
                    #NSLog("%@", char._.UUID)
                    self.appendCharacteristicForService(char, s, self.peripheral)        
                        
                    # for test
                    #self.readValueForCharacteristic(char)
                    self.setNotifyValueForCharacteristic(True, char)               
                    #peripheral.readValueForCharacteristic_(char)
                else:
                    pass # found a characteristic profile not listed in IOBluetooth.py
            
            # for the purpose of test, enable ACC and SIDs at the starting point
            self.initCharacteristicWhenDiscovered(uuid)
                
        else: 
            pass # found a service profile not listed in IOBluetooth.py
        '''    
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
        '''          
            
    def peripheral_didUpdateValueForCharacteristic_error_(self,
                                                          peripheral,
                                                          characteristic,
                                                          error):
#        print "Read Characteristic(%s) value" % characteristic._.UUID
        
        char = self.findCharacteristicByUUID(self.checkUUID(characteristic._.UUID))

        # process the received data and put into queue
        self.delegateWorker.getQueue().put(char.process())

        ''' hasn't resolve
        # EPL LED PROFILE
        if characteristic._.UUID == CBUUID.UUIDWithString_("FF14"):
            hex_str = binascii.hexlify(characteristic._.value)
            value = int(hex_str, base=16)
            print "CHAR(%s) %d %s" % (characteristic._.UUID, value, hex_str)
            byte_array = array.array('b', chr(2))
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            peripheral.writeValue_forCharacteristic_type_(
                val_data, characteristic,
                CBCharacteristicWriteWithResponse)
        '''


    def peripheral_didWriteValueForCharacteristic_error_(self,
                                                         peripheral,
                                                         characteristic,
                                                         error):
        print "CHAR(%s) is updated" % (characteristic._.UUID)
        char = self.findCharacteristicByUUID(self.checkUUID(characteristic._.UUID))
        # process the received data and put into queue

        self.delegateWorker.getQueue().put(char.process())
        
        '''
        hex_str = binascii.hexlify(characteristic._.value)
        value = int(hex_str, base=16)
        print "CHAR(%s) is updated" % (characteristic._.UUID)
        '''

    def peripheral_didUpdateNotificationStateForCharacteristic_error_(self,
                                                                      peripheral,
                                                                      characteristic,
                                                                      error):
        
        print "char(" + str(characteristic._.UUID) + ") is auto-notify? " + str(characteristic.isNotifying())
              

        

  