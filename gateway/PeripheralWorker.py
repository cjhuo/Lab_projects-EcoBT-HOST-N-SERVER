'''
Created on Feb 5, 2013

@author: cjhuo

@summary: 
maintains a profile hierarchy. The follows is an example:

{'1800': {'2A00': {'descriptors': {}, 'properties': ['Read']},
          '2A01': {'descriptors': {}, 'properties': ['Read']}},
 '1801': {'2A05': {'descriptors': {}, 'properties': ['Read']}},
 '180A': {'2A23': {'descriptors': {'2901': 'DeviceInformation'},
                   'properties': ['Read']}},
 '7760': {'7761': {'descriptors': {'2901': 'Authentication'},
                   'properties': ['Write']}},
 '7770': {'7771': {'descriptors': {'2901': 'AES_CFB: uint8, parameters: 1. secret key: unicode16, 2. IV: unicode16'},
                   'properties': ['Read']},
          '7772': {'descriptors': {'2901': 'secret key: unicode16'},
                   'properties': ['Read', 'Write Without Response']},
          '7773': {'descriptors': {'2901': 'IV : unicode16'},
                   'properties': ['Read', 'Write Without Response']}},
 '7780': {'7781': {'descriptors': {'2901': 'TestDescriptor',
                                   '2902': '\x00\x00'},
                   'properties': ['Read', 'Notify']}}}
'''
from Foundation import *
#from PyObjCTools import AppHelper
from config_gateway import *
from objc import *

import array, binascii, struct, pprint


class PeripheralWorker(NSObject):
    def init(self):
        self.instance = None
        self.identifier = None
        self.profileHierarchyDict = {}
        NSLog("Initialize Peripheral Worker")
        return self
    
    def setInstance(self, instance):
        self.instance = instance   
    
    def stop(self):
        pass
    
    def discoverServices(self):
        self.instance.discoverServices_(None)

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
        self.instance.discoverCharacteristics_forService_(nil, service)
        
    def readValueForCharacteristic(self, characteristic):
        NSLog("READING CHARACTERISTIC VALUE FROM %@", characteristic._.UUID)
        self.instance.readValueForCharacteristic_(characteristic)
        
    def setNotifyValueForCharacteristic(self, flag, characteristic):
        self.instance.setNotifyValue_forCharacteristic_(flag, characteristic)
            
    def writeValueForCharacteristic(self, value, characteristic, withResponse):
        NSLog("WRITING CHARACTERISTIC %@ TO VALUE %@", characteristic._.UUID, value)
        if withResponse:
            self.instance.writeValue_forCharacteristic_type_(value, characteristic,
                                                        CBCharacteristicWriteWithResponse)
        else:
            self.instance.writeValue_forCharacteristic_type_(value, characteristic,
                                                        CBCharacteristicWriteWithoutResponse)
            

        
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
            
            if chrUUIDStr == SYSTEM_ID_CHAR and srvUUIDStr == DEVICE_INFO_SERVICE:
                self.readValueForCharacteristic(char)
            
            #discover descriptors for the characteristic
            self.profileHierarchyDict[srvUUIDStr][chrUUIDStr]['descriptors'] = {}
            peripheral.discoverDescriptorsForCharacteristic_(char)
                    
                                         
    def peripheral_didDiscoverDescriptorsForCharacteristic_error_(self,
                                                                      peripheral,
                                                                      characteristic,
                                                                      error):
        
        NSLog("didDiscoverDescriptorsForCharacteristic %@, %@", self.UUID2Str(characteristic._.UUID), error)
        for descriptor in characteristic._.descriptors:
            #NSLog("Reading value of descriptor %@ for characteristic %@", self.UUID2Str(descriptor._.UUID), self.UUID2Str(characteristic._.UUID))   
            peripheral.readValueForDescriptor_(descriptor)
        
    def peripheral_didUpdateValueForDescriptor_error_(self, 
                                                     peripheral,
                                                     descriptor,
                                                     error):
        NSLog("didUpdateValueForDescriptor %@, %@", descriptor._.characteristic._.UUID, error)
        
        srvUUIDStr = self.UUID2Str(descriptor._.characteristic._.service._.UUID)   
        chrUUIDStr = self.UUID2Str(descriptor._.characteristic._.UUID)   
        descyptUUIDStr = self.UUID2Str(descriptor._.UUID)        
        descryptStr, = struct.unpack("@"+str(len(descriptor._.value))+"s", descriptor._.value)
        self.profileHierarchyDict[srvUUIDStr][chrUUIDStr]['descriptors'][descyptUUIDStr] = descryptStr  
        #NSLog("descriptor's value is %@", NSString.alloc().initWithData_encoding_(descriptor._.value, NSUTF8StringEncoding))
        pprint.pprint(self.profileHierarchyDict)

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
        srvUUIDStr = self.UUID2Str(characteristic._.service._.UUID)   
        chrUUIDStr = self.UUID2Str(characteristic._.UUID)
        if chrUUIDStr == SYSTEM_ID_CHAR and srvUUIDStr == DEVICE_INFO_SERVICE:
            idntfr, = struct.unpack('@Q', characteristic._.value)
            self.identifier = idntfr
            hex_str = binascii.hexlify(characteristic._.value)
            a1, a2, a3, a4, a5, a6 = struct.unpack('cccxxccc', characteristic._.value)
            address = str(binascii.hexlify(a6) + '-' + binascii.hexlify(a5) + '-' + binascii.hexlify(a4) + '-' + \
             binascii.hexlify(a3) + '-' + binascii.hexlify(a2) + '-' + binascii.hexlify(a1))
            print 'MAC Address: ', address, 'identifier is ', self.identifier
                      


    def peripheral_didWriteValueForCharacteristic_error_(self,
                                                         peripheral,
                                                         characteristic,
                                                         error):
        NSLog("CHAR(%@) is updated", characteristic._.UUID)
            

    def peripheral_didUpdateNotificationStateForCharacteristic_error_(self,
                                                                      peripheral,
                                                                      characteristic,
                                                                      error):
        
        NSLog("char(%@) is auto-notify? %@", characteristic._.UUID, characteristic.isNotifying())
             
 
        

  