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
        NSLog("Initialize Peripheral Worker")
        return self
    
    def setPeripheral(self, peripheral):
        self.peripheral = peripheral
        self.delegateWorker.number = peripheral.number     

    def setSockets(self, sockets):
        self.sockets = sockets
        self.delegateWorker.setGlobalSockets(sockets)
        
    def stop(self):
        self.delegateWorker.getQueue().put('stop')
        self.delegateWorker.join()

    def discoverServices(self):
        self.peripheral.instance.discoverServices_(None)

    def setWorker(self, worker):
        self.worker = worker
        #print worker
        #self.worker.getQueue().put('This is a test')
        
    def discoverCharacteristics_forService(self, service):
        if type(service) == Service:
            self.peripheral.instance.discoverCharacteristics_forService_(nil, service.instance)
        else:
            self.peripheral.instance.discoverCharacteristics_forService_(nil, service)
        
    def readValueForCharacteristic(self, characteristic):
        if isinstance(characteristic, Characteristic.Characteristic):
            NSLog("READING CHARACTERISTIC VALUE FROM %@", characteristic.UUID)
            self.peripheral.instance.readValueForCharacteristic_(characteristic.instance)
        else:
            NSLog("READING CHARACTERISTIC VALUE FROM %@", characteristic._.UUID)
            self.peripheral.instance.readValueForCharacteristic_(characteristic)
        
    def setNotifyValueForCharacteristic(self, flag, characteristic):
        if isinstance(characteristic, Characteristic.Characteristic):
            self.peripheral.instance.setNotifyValue_forCharacteristic_(flag, characteristic.instance)
        else:
            self.peripheral.instance.setNotifyValue_forCharacteristic_(flag, characteristic)
            
    def writeValueForCharacteristic(self, value, characteristic):
        if isinstance(characteristic, Characteristic.Characteristic):
            NSLog("WRITING CHARACTERISTIC %@ TO VALUE %@", characteristic.UUID, value)
            self.peripheral.instance.writeValue_forCharacteristic_type_(
                                                               value, characteristic.instance,
                                                               CBCharacteristicWriteWithResponse)
        else:
            NSLog("WRITING CHARACTERISTIC %@ TO VALUE %@", characteristic._.UUID, value)
            self.peripheral.instance.writeValue_forCharacteristic_type_(
                                                               value, characteristic,
                                                               CBCharacteristicWriteWithResponse)
            
    def findServiceByUUID(self, UUID):
        for s in self.services:
            if s.UUID == UUID:
                return s
        #raise Exception # didn't find any service
        return None
        
    def findCharacteristicByUUID(self, UUID):
        for s in self.services:
            for c in s.characteristics:
                if UUID == c.UUID:
                    return c
        #raise Exception
        return None
    
    def appendService(self, serviceInstance):
        uuid = self.checkUUID(serviceInstance._.UUID)
        if uuid != None:
            s = Service(uuid, serviceInstance)
            self.services.append(s) # append to service list for tracking from UI   
        else:
            # found a service profile not listed in IOBluetooth.py
            NSLog("FOUND AN UNKNOWN SERVICE %@", serviceInstance._.UUID)
        
    def appendCharacteristicForService(self, characteristic, service, peripheral):
        c = characteristicFactory.createCharacteristic(self.checkUUID(characteristic._.UUID), characteristic, service, self)
        # Characteristic that has read&write and system infor needs to be read at the beginning         
        if c.privilege == 1 or c.privilege == 2: 
            self.readValueForCharacteristic(c)
        elif c.privilege == 0:
            self.setNotifyValueForCharacteristic(True, c)   
        service.characteristics.append(c)
    
    def checkUUID(self, UUID):
        for p in ProfileDict.keys():
            if UUID == CBUUID.UUIDWithString_(p):
                #peripheral.discoverCharacteristics_forService_(nil, service)
                return p  
        # does not raise exception now to ignore discovery of profiles 'Generic Access Profile' and 'Generic Attribute Profile'
        # raise Exception # didn't find any UUID
        return None
    
    def findECGService(self):
        return self.findCharacteristicByUUID("FEC5")
  
    '''  
    # for the purpose of test, enable some certain characteristic(s) at the starting point
    def initCharacteristicWhenDiscovered(self, uuid):
        if uuid == "FFA0": # disable ACC
            c = self.findCharacteristicByUUID("FFA1")
            if c != None:
                val = c.createDisableFlag()
                self.writeValueForCharacteristic(val, c)
        if uuid == "FF10":
            c = self.findCharacteristicByUUID("FF11") # set Green LED to disable
            if c != None: 
                val = c.createDisableFlag()
                self.writeValueForCharacteristic(val, c)
            c = self.findCharacteristicByUUID("FF12")
            if c != None: # set Green LED blink interval to 0.1sec
                val = c.createDisableFlag()
                self.writeValueForCharacteristic(val, c)
    '''
        
    # CBPeripheral delegate methods
    def peripheral_didDiscoverServices_(self, peripheral, error):
        print "Number of services:", len(peripheral._.services)
        for service in peripheral._.services:
            #NSLog("Service UUID %@", service._.UUID)
            if self.checkUUID(service._.UUID) != None and self.findServiceByUUID(self.checkUUID(service._.UUID)) == None: # already added service, no need to add again
                NSLog("Service found with UUID: %@", service._.UUID)
                self.appendService(service)
            
                # for test
                self.discoverCharacteristics_forService(service)
        
        # inform UI!

    def peripheral_didDiscoverCharacteristicsForService_error_(self,
                                                               peripheral,
                                                               service,
                                                               error):
        #print "didDiscoverCharacteristicsForService", service._.UUID
        uuid = self.checkUUID(service._.UUID)
        if uuid != None:
            s = self.findServiceByUUID(uuid)
            if s != None:               
                for char in service._.characteristics:
                    #discover descriptors for the characteristic
                    peripheral.discoverDescriptorsForCharacteristic_(char)
                                 
                    if (self.checkUUID(char._.UUID)) != None:
                        NSLog("didDiscoverCharacteristicsForService %@ %@", service._.UUID, char._.UUID)
                        self.appendCharacteristicForService(char, s, self.peripheral.instance)        
                        # for test
                        #self.readValueForCharacteristic(char)            
                        #peripheral.readValueForCharacteristic_(char)
                        
                        # for the purpose of test, enable ACC and SIDs at the starting point
                        #self.initCharacteristicWhenDiscovered(uuid)
                    else:
                        # found a characteristic profile not listed in IOBluetooth.py
                        NSLog("FOUND AN UNKNOWN CHARACTERISTIC %@", char._.UUID)
            else: # found a unkown service
                NSLog("FOUND AN UNKNOWN SERVICE %@", service._.UUID)
                
        else: 
            pass # found a service profile not listed in IOBluetooth.py
        
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
        
        char = self.findCharacteristicByUUID(self.checkUUID(characteristic._.UUID))
        if char != None:
            # process the received data
            char.process()


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
             
 
        

  