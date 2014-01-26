'''
Created on Feb 5, 2013

@author: cjhuo

@summary: 

'''
from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *

import array
import binascii
import struct

from Service import *
from characteristic import characteristicFactory
from characteristic.implementation import Characteristic

class PeripheralWorker(NSObject):
    def init(self):
        self.instance = None
        self.profileHierarchyDict = {}
        NSLog("Initialize Peripheral Worker")
        return self
    
    def setInstance(self, instance):
        self.instance = instance
        
    def stop(self):
        pass
    
    def discoverServices(self):
        self.instance.discoverServices_(None)

    def setWorker(self, worker):
        self.worker = worker
        
    def UUID2Str(self, UUID):
        tempStr = ""
        for index in range(len(UUID._.data)):
            tempStr = tempStr + (binascii.hexlify(UUID._.data[index])).upper()
        return tempStr
    
    def checkProperties(self, properties):
        propertiesStrList = []
        if properties & CBCharacteristicPropertyBroadcast == CBCharacteristicPropertyBroadcast:
            propertiesStrList.append("Broadcast")
        if properties & CBCharacteristicPropertyRead == CBCharacteristicPropertyRead:
            propertiesStrList.append("Read")
        if properties & CBCharacteristicPropertyWriteWithoutResponse == CBCharacteristicPropertyWriteWithoutResponse:
            propertiesStrList.append("Write Without Response")
        if properties & CBCharacteristicPropertyWrite == CBCharacteristicPropertyWrite:
            propertiesStrList.append("Write")
        if properties & CBCharacteristicPropertyNotify == CBCharacteristicPropertyNotify:
            propertiesStrList.append("Notify")
        if properties & CBCharacteristicPropertyIndicate == CBCharacteristicPropertyIndicate:
            propertiesStrList.append("Indicate")
        if properties & CBCharacteristicPropertyAuthenticatedSignedWrites == CBCharacteristicPropertyAuthenticatedSignedWrites:
            propertiesStrList.append("Authenticated Signed Writes")
            
        return propertiesStrList
        
    def discoverCharacteristics_forService(self, service):
        if type(service) == Service:
            self.instance.discoverCharacteristics_forService_(nil, service.instance)
        else:
            self.instance.discoverCharacteristics_forService_(nil, service)
        
    def readValueForCharacteristic(self, characteristic):
        if isinstance(characteristic, Characteristic.Characteristic):
            NSLog("READING CHARACTERISTIC VALUE FROM %@", characteristic.UUID)
            self.instance.readValueForCharacteristic_(characteristic.instance)
        else:
            NSLog("READING CHARACTERISTIC VALUE FROM %@", characteristic._.UUID)
            self.instance.readValueForCharacteristic_(characteristic)
        
    def setNotifyValueForCharacteristic(self, flag, characteristic):
        if isinstance(characteristic, Characteristic.Characteristic):
            self.instance.setNotifyValue_forCharacteristic_(flag, characteristic.instance)
        else:
            self.instance.setNotifyValue_forCharacteristic_(flag, characteristic)
            
    def writeValueForCharacteristic(self, value, characteristic):
        if isinstance(characteristic, Characteristic.Characteristic):
            NSLog("WRITING CHARACTERISTIC %@ TO VALUE %@", characteristic.UUID, value)
            self.instance.writeValue_forCharacteristic_type_(
                                                               value, characteristic.instance,
                                                               CBCharacteristicWriteWithResponse)
        else:
            NSLog("WRITING CHARACTERISTIC %@ TO VALUE %@", characteristic._.UUID, value)
            self.instance.writeValue_forCharacteristic_type_(
                                                               value, characteristic,
                                                               CBCharacteristicWriteWithResponse)

        
    # CBPeripheral delegate methods
    def peripheral_didDiscoverServices_(self, peripheral, error):
        print "Number of services:", len(peripheral._.services)
        for service in peripheral._.services:
            NSLog("Service found with UUID: %@", self.UUID2Str(service._.UUID))
            self.profileHierarchyDict[self.UUID2Str(service._.UUID)] = {}    
            self.discoverCharacteristics_forService(service)
        

    def peripheral_didDiscoverCharacteristicsForService_error_(self,
                                                               peripheral,
                                                               service,
                                                               error):
        for char in service._.characteristics:            
            srvUUIDStr = self.UUID2Str(service._.UUID)   
            chrUUIDStr = self.UUID2Str(char._.UUID)                  
            self.profileHierarchyDict[srvUUIDStr][chrUUIDStr] = {}
            self.profileHierarchyDict[srvUUIDStr][chrUUIDStr]['properties'] = self.checkProperties(char._.properties)
            #discover descriptors for the characteristic
            peripheral.discoverDescriptorsForCharacteristic_(char)
                    
                                         
    def peripheral_didDiscoverDescriptorsForCharacteristic_error_(self,
                                                                      peripheral,
                                                                      characteristic,
                                                                      error):
        
        NSLog("didDiscoverDescriptorsForCharacteristic %@, %@", characteristic._.UUID, error)
        for descriptor in characteristic._.descriptors:
            NSLog("Reading value of descriptor %@ for characteristic %@", descriptor._.UUID, str(characteristic._.UUID))
            peripheral.readValueForDescriptor_(descriptor)
            NSLog("value %@", descriptor._.value)
        
    def peripheral_didUpdateValueForDescriptor_error_(self, 
                                                     peripheral,
                                                     descriptor,
                                                     error):
        NSLog("didUpdateValueForDescriptor %@ for characteristic %@, error %@", descriptor._.UUID, descriptor._.characteristic._.UUID, error)
        NSLog("descriptor's value is %@", NSString.alloc().initWithData_encoding_(descriptor._.value, NSUTF8StringEncoding))
        print str(NSString.alloc().initWithData_encoding_(descriptor._.value, NSUTF8StringEncoding))

    def peripheral_didWriteValueForDescriptor_error_(self,
                                                     peripheral,
                                                     descriptor,
                                                     error):
        NSLog("didWriteValueForDescriptor %@, %@", descriptor._.UUID, error._.code)
        #peripheral.readValueForDescriptor_(descriptor)
        NSLog("value %@", descriptor._.value)
        
            
    def peripheral_didUpdateValueForCharacteristic_error_(self,
                                                          peripheral,
                                                          characteristic,
                                                          error):
#        print "Read Characteristic(%s) value" % characteristic._.UUID
        NSLog("didUpdateValueForCharacteristic error %@", error)
        
        char = self.findCharacteristicByUUID(self.checkUUID(characteristic._.UUID))
        if char != None:
            # process the received data
            char.process()
        
        if self.securityIV != None and self.securityKey != None:
            from Crypto.Cipher import AES
            self.securityObj = AES.new(self.securityKey, AES.MODE_CFB, self.securityIV)
            self.securityIV = None
            self.securityKey = None
            self.readValueForCharacteristic(self.findCharacteristicByUUID(u'7781'))

    def peripheral_didWriteValueForCharacteristic_error_(self,
                                                         peripheral,
                                                         characteristic,
                                                         error):
        NSLog("CHAR(%@) is updated", characteristic._.UUID)
        char = self.findCharacteristicByUUID(self.checkUUID(characteristic._.UUID))
        
        # value sent out, start to read in new value
        self.readValueForCharacteristic(char)
        '''
        if char != None:
            # process the received data and put into queue
            char.process()
            pass
        '''
            

    def peripheral_didUpdateNotificationStateForCharacteristic_error_(self,
                                                                      peripheral,
                                                                      characteristic,
                                                                      error):
        
        NSLog("char(%@) is auto-notify? %@", str(characteristic._.UUID), str(characteristic.isNotifying()))
             
 
        

  