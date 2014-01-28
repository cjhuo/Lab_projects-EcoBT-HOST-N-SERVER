'''
Created on Feb 5, 2013

@author: cjhuo

@summary: 
maintains a profile hierarchy. The follows is an example:
Format:
{Services: {Characteristics: {'descriptors':{'uuid': }, 'properties':[]}}
Example:
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
        self.securityHandler = None
        self.authenticationHandler = None
        NSLog("Initialize Peripheral Worker")
        return self
    
    
    def getsecurityHandler(self):
        return self.authenticationHandler
    
    def getAuthenticationHandler(self):
        return self.authenticationHandler
    
    def getProfileHierarchy(self):
        return self.profileHierarchyDict
    
    def getIdentifier(self):
        return self.identifier
    
    def setInstance(self, instance):
        self.instance = instance   
    
    def setGateway(self, gateway):
        self.gateway = gateway
    
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
        
    def readValueFromPeripheral(self, serviceUUIDStr, characteristicUUIDStr):
        for service in self.instance._.services:
            if service._.UUID == CBUUID.UUIDWithString_(serviceUUIDStr):
                for char in service._.characteristics:
                    if char._.UUID == CBUUID.UUIDWithString_(characteristicUUIDStr):
                        self.readValueForCharacteristic(char)
                        return
        # raise error if can't find a relevant characteristic            
        
    
    def writeValueForPeripheral(self, serviceUUIDStr, characteristicUUIDStr, message, requireRespone):
        for service in self.instance._.services:
            if service._.UUID == CBUUID.UUIDWithString_(serviceUUIDStr):
                for char in service._.characteristics:
                    if char._.UUID == CBUUID.UUIDWithString_(characteristicUUIDStr):
                        if requireRespone:
                            self.writeValueForCharacteristic(char, NSData.alloc().initWithBytes_length_(message, len(message)), 
                                                             CBCharacteristicWriteWithResponse)
                        else:
                            self.writeValueForCharacteristic(char, NSData.alloc().initWithBytes_length_(message, len(message)), 
                                                             CBCharacteristicWriteWithoutResponse)
                        return
        # raise error if can't find a relevant characteristic            
    def findCharacteristicByUUIDStr(self, UUIDStr):
        for service in self.instance._.services:
            for char in service._.characteristics:
                if char._.UUID == CBUUID.UUIDWithString_(UUIDStr):
                    return char
        return None
                            
    def readValueForCharacteristic(self, characteristic):
        if type(characteristic) == str:
            characteristic = self.findCharacteristicByUUIDStr(characteristic)
        if characteristic == None:
            return
        NSLog("READING CHARACTERISTIC VALUE FROM %@", characteristic._.UUID)
        self.instance.readValueForCharacteristic_(characteristic)
        
    def setNotifyValueForCharacteristic(self, flag, characteristic):
        self.instance.setNotifyValue_forCharacteristic_(flag, characteristic)
            
    def writeValueForCharacteristic(self, value, characteristic, withResponse):
        if type(characteristic) == str:
            characteristic = self.findCharacteristicByUUIDStr(characteristic)     
        if characteristic == None:
            return   
        NSLog("WRITING CHARACTERISTIC %@ TO VALUE %@", characteristic._.UUID, value)
        data = NSData.alloc().initWithBytes_length_(value, len(value))
        if withResponse:
            self.instance.writeValue_forCharacteristic_type_(data, characteristic,
                                                        CBCharacteristicWriteWithResponse)
        else:
            self.instance.writeValue_forCharacteristic_type_(data, characteristic,
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
#        print 'error equals to None? ', error == None
        NSLog("didUpdateValueForCharacteristic error %@", error)
        srvUUIDStr = self.UUID2Str(characteristic._.service._.UUID)   
        chrUUIDStr = self.UUID2Str(characteristic._.UUID)
        if len(characteristic._.value) != 0:
            if chrUUIDStr == SYSTEM_ID_CHAR and srvUUIDStr == DEVICE_INFO_SERVICE:
                idntfr, = struct.unpack('@Q', bytes(characteristic._.value))
                self.identifier = idntfr
                hex_str = binascii.hexlify(characteristic._.value)
                a1, a2, a3, a4, a5, a6 = struct.unpack('cccxxccc', characteristic._.value)
                address = str(binascii.hexlify(a6) + '-' + binascii.hexlify(a5) + '-' + binascii.hexlify(a4) + '-' + \
                 binascii.hexlify(a3) + '-' + binascii.hexlify(a2) + '-' + binascii.hexlify(a1))
                print 'MAC Address: ', address, 'identifier is ', self.identifier
                # initialize authentication if any
                if self.authenticationHandler != None:
                    self.authenticationHandler.initialize(peripheral)
                return
            if srvUUIDStr == SECURITY_SERVICE:
                if chrUUIDStr != SECURITY_TYPE_CHARACTERISTIC:
                    self.securityHandler.setParameter(characteristic)
                    if self.securityHandler.isSecured() and self.authenticationHandler != None and self.authenticationHandler.isAuthorized() == False:
                        self.authenticationHandler.checkAuthentication(self.securityHandler)
                else:
                    data = binascii.hexlify(characteristic._.value)
                    print data
                    if error == None:
                        self.gateway.receiveFeedbackFromPeripheral(self.identifier, 'Read', srvUUIDStr, chrUUIDStr, data, None)
                    else:
                        self.gateway.receiveFeedbackFromPeripheral(self.identifier, 'Read', srvUUIDStr, chrUUIDStr, data, int(error._.code)) 
                return                    
            if self.securityHandler != None and self.securityHandler.isSecured():
                if self.authenticationHandler != None and self.authenticationHandler.isAuthorized() == False:
                    self.authenticationHandler.checkAuthentication(self.securityHandler)          
                    return
                print 'decryption required'
                data, = struct.unpack("@"+str(len(self.instance._.value))+"s", self.instance._.value)
                message = binascii.unhexlify(self.securityHandler.decrypt(data))
            print bytes(characteristic._.value)
            print message
            if error == None:
                self.gateway.receiveFeedbackFromPeripheral(self.identifier, 'Read', srvUUIDStr, chrUUIDStr, message, None)
            else:
                self.gateway.receiveFeedbackFromPeripheral(self.identifier, 'Read', srvUUIDStr, chrUUIDStr, message, int(error._.code))                                  
        else: # security or authentication expired
            self.securityHandler.reset()
            self.authenticationHandler.reset()


    def peripheral_didWriteValueForCharacteristic_error_(self,
                                                         peripheral,
                                                         characteristic,
                                                         error):
        NSLog("CHAR(%@) is updated", characteristic._.UUID)
        srvUUIDStr = self.UUID2Str(characteristic._.service._.UUID)   
        chrUUIDStr = self.UUID2Str(characteristic._.UUID)
        
        if srvUUIDStr != SECURITY_SERVICE and chrUUIDStr != SECURITY_TYPE_CHARACTERISTIC:
            self.securityHandler.setParameter(characteristic)
        elif srvUUIDStr == AUTHENTICATION_SERVICE and chrUUIDStr == AUTHENTICATION_CHAR:
            pass # ignore authentication service write feedback
        elif error == None:
            print 'write success'
            self.gateway.receiveFeedbackFromPeripheral(self.identifier, 'Write', srvUUIDStr, chrUUIDStr, 0, None)
        else:
            print 'write failed'
            self.gateway.receiveFeedbackFromPeripheral(self.identifier, 'Write', srvUUIDStr, chrUUIDStr, -1, int(error._.code))

    def peripheral_didUpdateNotificationStateForCharacteristic_error_(self,
                                                                      peripheral,
                                                                      characteristic,
                                                                      error):
        
        NSLog("char(%@) is auto-notify? %@", characteristic._.UUID, characteristic.isNotifying())
             
 
        

  