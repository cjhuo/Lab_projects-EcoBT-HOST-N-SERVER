'''
Created on Jan 20, 2014

@author: cjhuo
'''

from Foundation import *
#from PyObjCTools import AppHelper
from config_peripheral import *
from objc import *
from PyObjCTools import AppHelper

import ProfileHierarchyBuilder
from SecurityHandler import SecurityHandler


class PeripheralManagerWorker(NSObject):
    
    def init(self):
        '''
        state: 
            0: if down, 
            1: if up but not startAdvertise, 
            2: up and startAdvertise, 
            3: has host connected(advertise stopped automatically)
        '''
        self._state = 0
        self.services = []
        self.authenticaionToken = None
        self.securityHandler = SecurityHandler("AES_CFB")
        # initializing CBPeripheralManager
        NSLog("Initializing CBPeripheralManager")
        self.manager = CBPeripheralManager.alloc().initWithDelegate_queue_(self, nil)
        return self
        
    def updateState(self, state):
        self._state = state
        if self._state == 0:
            NSLog("PERIPHERAL MANAGER IS DOWN")
        elif self._state == 1:
            NSLog("PERIPHERAL MANAGER IS UP")
        elif self._state == 2:
            NSLog("PERIPHERAL MANAGER IS ADVERTISING")
        elif self._state == 3:
            NSLog("PERIPHERAL MANAGER IS CONNECTED WITH A HOST, ADVERTISE STOPPED")
        
    def getState(self):
        return self._state
    
    def stop(self):
        pass
    
    def UUID2Str(self, UUID):
        for service, chars in ProfileDict.iteritems():
            if CBUUID.UUIDWithString_(service) == UUID:
                return service
            for char in chars.keys():
                if CBUUID.UUIDWithString_(char) == UUID:
                    return char
        return None
    
    ''' CBPeripheralManagerDelegate Methods From Below '''
    
    ''' check Bluetooth state '''
    def peripheralManagerDidUpdateState_(self, peripheral):
        state = peripheral._.state
        if(state == CBPeripheralManagerStateUnknown):
            NSLog("BLUETOOTH STATE UNKNOWN")
        elif(state == CBPeripheralManagerStateResetting):
            NSLog("BLUETOOTH RESETING")
        elif(state == CBPeripheralManagerStateUnsupported):
            NSLog("BLUETOOTH UNSUPPORTED")
        elif(state == CBPeripheralManagerStateUnauthorized):
            NSLog("BLUETOOTH UNAUTHORIZED")
        elif(state == CBPeripheralManagerStatePoweredOff):
            NSLog("BLUETOOTH POWER OFF")
        if(state == CBPeripheralManagerStatePoweredOn):
            self.updateState(1)
        else:
            self.updateState(0)
            
        if self.getState() == 1: # bluetooth ready
            # start initialize services and characteristics
            '''
            # for test now, not scalable
            # !!!FOUND, THERE HAS TO BE A CHARACTERISTIC EXISTING IN THE PERIPHERAL 
            # WITH NOTIFICATION PROPETIY TO KEEP THE CONNECTION WITH
            # OUT TIMEOUT. OTHERWISE, THE CONNECTION WILL TIMEOUT IN 3 SECONDS
            self.testCharacteristic = CBMutableCharacteristic.alloc().initWithType_properties_value_permissions_(CBUUID.UUIDWithString_(u'7788'),
                                                       CBCharacteristicPropertyNotify | CBCharacteristicPropertyRead,
                                                       nil, # ensures the value is treated dynamically
                                                       CBAttributePermissionsReadable)
            self.testCharacteristic._.descriptors = [CBMutableDescriptor.alloc().
                                                     initWithType_value_(CBUUID.UUIDWithString_(CBUUIDCharacteristicUserDescriptionString),
                                                                         u'TestDescriptor')]
            self.testService = CBMutableService.alloc().initWithType_primary_(CBUUID.UUIDWithString_(u'7780'),
                                                      YES)
            self.testService._.characteristics = [self.testCharacteristic]
                        
            self.manager.addService_(self.testService)
            self.manager.startAdvertising_({CBAdvertisementDataServiceUUIDsKey: [CBUUID.UUIDWithString_(u'7780')],
                                            CBAdvertisementDataLocalNameKey: u'TestPeripheral'})

            '''
            ProfileHierarchyBuilder.createHierarchy(self)
            
            # start advertise, using the first service UUID as advertisement data
            self.manager.startAdvertising_({CBAdvertisementDataServiceUUIDsKey: [self.manager._.services[0]._.UUID],
                                            CBAdvertisementDataLocalNameKey: u'TestPeripheral'})
            
            '''
            !!!Native conversion between NSDictionary and dict, and NSArray and list from Objective-c to Python
            self.manager.startAdvertising_(NSDictionary.dictionaryWithObjects_forKeys_(
                                                [[CBUUID.UUIDWithString_(u'1801')], # advertising using GATT
                                                    NSString.stringWithString_(u'TestPeripheral')],
                                                [CBAdvertisementDataServiceUUIDsKey, CBAdvertisementDataLocalNameKey]))
            '''
            self.updateState(2)

            
            
    def peripheralManager_central_didSubscribeToCharacteristic_(self, peripheral, central, characteristic):
        NSLog("Central subscribed to characteristic")
        
    def peripheralManager_central_didUnsubscribeFromCharacteristic_(self, peripheral, central, characteristic):
        NSLog("Central unsubscribed from characteristic")
        
    def peripheralManagerDidStartAdvertising_error_(self, peripheral, error):
        NSLog("Peripheral did start advertising")
        
    def peripheralManager_didAddService_error_(self, peripheral, service, error):
        NSLog("Peripheral did add service")
                        
    def peripheralManager_willRestoreState_(self, peripheral, dictionary):
        NSLog("Peripheral will be stored by system")
            
    def peripheralManagerIsReadyToUpdateSubscribers_(self, peripheral):
        NSLog("Peripheral is ready to update to subscriber")
    
    def peripheralManager_didReceiveReadRequest_(self, peripheral, request):
        NSLog("Peripheral received read request from central")
        #print "Still advertising?", "Yes" if self.manager._.isAdvertising == 1 else "No"
        #self.manager.stopAdvertising()
        char = self.UUID2Str(request._.characteristic._.UUID)
        service = self.UUID2Str(request._.characteristic._.service._.UUID)
        error = None
        for srv in self.services:
            if srv.UUID == service:
                for chr in srv.characteristics:
                    if chr.UUID == char:
                        if srv.UUID == SECURITY_SERVICE: ## initializing or reinitializing security channel
                            request, error = chr.handleReadRequest(request, self.securityHandler)
                            self.manager.respondToRequest_withResult_(request, error)
                            return
                        if srv.UUID == DEVICE_INFO:
                            message = chr.handleReadRequest()
                            request._.value = NSData.alloc().initWithBytes_length_(message, len(message))
                            error = CBATTErrorSuccess[0] # CBATTErrorSuccess is a tuple, only first one useful
                            self.manager.respondToRequest_withResult_(request, error)
                            return                     
                        else:                    
                            # check if the security channel has already been established
                            if self.securityHandler.isInitialized() == False:
                                error = CBATTErrorReadNotPermitted
                                self.manager.respondToRequest_withResult_(request, error)
                                return   
                            else:                                 
                                # security channel has already been established                                 
                                message = chr.handleReadRequest()
                                encrypt_data = self.securityHandler.encrypt(message)
                                request._.value = NSData.alloc().initWithBytes_length_(encrypt_data, len(encrypt_data))
                                error = CBATTErrorSuccess[0] # CBATTErrorSuccess is a tuple, only first one useful
                                self.manager.respondToRequest_withResult_(request, error)
                                return                            
            '''
        if request._.characteristic._.UUID  == self.testCharacteristic._.UUID:
            testNSData = NSString.alloc().initWithString_(u'1234').dataUsingEncoding_(NSUTF8StringEncoding) # default value
            request._.value = NSData.alloc().initWithBytes_length_('bytes', 5)
            self.manager.respondToRequest_withResult_(request, CBATTErrorSuccess[0]) # CBATTErrorSuccess is a tuple, only first one useful
        '''
        ''' treat static characteristic value
            if request._.offset > self.testCharacteristic._.value._.length:
                self.manager.respondToRequest_withResult_(request, CBATTErrorInvalidOffset)
            else:
                request._.value = self.testCharacteristic._.value.subdataWithRange_(
                                    NSMakeRange(request._.offset, 
                                    self.testCharacteristic._.value._.length - request._.offset))
                self.manager.respondToRequest_withResult_(request, CBATTErrorSuccess)
        '''
            
        
    def peripheralManager_didReceiveWriteRequests_(self, peripheral, requests):
        NSLog("Peripheral received write requests from central")
            
            
            
            
            