'''
Created on Jan 26, 2014

@author: cjhuo
'''


'''
@summary: 
This gateway serves as bridge between rimware and sensors.
It serves to get the BLE profile hierarchy from the sensor
and extract information of characteristics including
properties, description in descriptors, special services
(security, authentication).
Due to the current Apple's BLE implementation, peripheral
cannot detect disconnection event, peripheral reset 
security and authentication after a certain idle time 
(e.g. 1 seconds) determined by peripheral. So to keep
an active session without re-initializing security
and authentication checking gateway should send periodic
request to peripheral with an interval which is less
than the interval set on peripheral
'''  

from Foundation import *
#from PyObjCTools import AppHelper
from objc import *
from PyObjCTools import AppHelper
from config_gateway import *
from Queue import Queue 
import time, json, threading
from threading import Event
from collections import deque
import pickle

from PeripheralWorker import PeripheralWorker

# Importing a dynamically generated module

def importCode(code,name,add_to_sys_modules=0):
    """
    Import dynamically generated code as a module. code is the
    object containing the code (a string, a file handle or an
    actual compiled code object, same types as accepted by an
    exec statement). The name is the name to give to the module,
    and the final argument says wheter to add it to sys.modules
    or not. If it is added, a subsequent import statement using
    name will return this module. If it is not added to sys.modules
    import will try to load it in the normal fashion.

    import foo

    is equivalent to

    foofile = open("/path/to/foo.py")
    foo = importCode(foofile,"foo",1)

    Returns a newly generated module.
    """
    import sys,imp

    module = imp.new_module(name)

    exec code in module.__dict__
    if add_to_sys_modules:
        sys.modules[name] = module

    return module
'''
# Example
code = \
"""
def testFunc():
    print "spam!"

class testClass:
    def testMethod(self):
        print "eggs!"
"""

m = importCode(code,"test")
m.testFunc()
o = m.testClass()
o.testMethod()
'''

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Serves for periodically send gateway snapshot to central.
The snapshot includes:
    all profile hierarchy of connected peripherals
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class PeriodicUpdater(threading.Thread):
    def __init__(self, gatewayManager):
        threading.Thread.__init__(self,name = "GatewayPeriodicUpdater")
        self.gatewayManager = gatewayManager
        self.flag = Event()
        
    def stop(self):
        self.flag.set()
        
    def run(self):
        while not self.flag.isSet():
            
            time.sleep(GATEWAY_UPDATE2CENTRAL_INTERVAL)
            #print 'sending snapshot to central'
            gatewayOverview = {}
            gatewayOverview['gateway_id'] = self.gatewayManager.getUUID()
            gatewayOverview['connected_peripherals'] = []
            for peripheralWorker in self.gatewayManager.getPeripheralWorkers():
                temp = {}
                temp['isSecured'] = (peripheralWorker.securityHandler != None and peripheralWorker.securityHandler.isSecured())
                temp['isAuthorized'] = (peripheralWorker.authenticationHandler != None and peripheralWorker.authenticationHandler.isAuthorized())
                temp['id'] = peripheralWorker.getIdentifier()
                temp['profileHierarchy'] = peripheralWorker.getProfileHierarchy()
                gatewayOverview['connected_peripherals'].append(temp)
            message = {
                       'type': 'snapshot',
                       'value': gatewayOverview
                       }
            try:    
                self.gatewayManager.writeReport2Central(message)
            except:
                print 'error happened when sending update to central'
        print 'PeriodicUpdater exiting..'
"""                
class InQueueHandler(threading.Thread):
    def __init__(self, gwManager):
        threading.Thread.__init__(self,name = "InQueueHandler")
        self.gwManager = gwManager
        self.flag = Event()
        
    def stop(self):
        self.flag.set()
        
    def run(self):
        while not self.flag.isSet():
            request = self.gwManager.inQueue.get()
            if request['type'] == 'gatewayAuthentication':
                report = {
                           'type': 'gatewayAuthenticationFeedback',
                           'value': {
                                     'authorizationToken': GATEWAY_AUTHENTICATION_TOKEN,
                                     'gatewayUUID': self.gwManager.uuid
                                     }
                           
                           }
                self.gwManager.writeReport2Central(report)
                #self.connection2Gateway.send(report)
                
            if request['type'] == 'gatewayUUID':
                self.gwManager.uuid = request['value']
                print self.gwManager.uuid
            
            if request['type'] == 'peripheralQuery':
                print 'got query ', request['value']['queryID']
                self.gwManager.taskQueue.append(request)
                self.gwManager.processTaskQueue()
                
            if request['type'] == 'peripheralSecurityTypeCheck':
                peripheralID = request['value']['peripheralID']
                peripheral = self.gwManager.findPeripheralWorkerByIdentifier(peripheralID)
                peripheral.readValueFromPeripheral(SECURITY_SERVICE, SECURITY_TYPE_CHARACTERISTIC)
                
            if request['type'] == 'peripheralAuthenticationHandlerCls':
                peripheralID = request['value']['peripheralID']
                peripheral = self.gwManager.findPeripheralWorkerByIdentifier(peripheralID)
                authenticationHandlerCls = request['value']['authenticationHandlerCls']
                m = importCode(authenticationHandlerCls, 'authentication')
                peripheral.authenticationHandler = m.Authentication()
                if peripheral.identifier != None:
                    peripheral.authenticationHandler.initialize(peripheral)
                report = {
                          'type': 'peripheralAuthenticationTokenQuery',
                          'value': {
                                    'peripheralID': peripheralID,
                                    }
                          }            
                if report != None:
                    self.gwManager.writeReport2Central(report)                 
                
            if request['type'] == 'peripheralSecurityHandlerCls':
                peripheralID = request['value']['peripheralID']
                peripheral = self.gwManager.findPeripheralWorkerByIdentifier(peripheralID)
                securityHandlerCls = request['value']['securityHandlerCls']
                m = importCode(securityHandlerCls, 'security')
                peripheral.securityHandler = m.SecurityHandlerFactory(request['value']['securityType'])
                peripheral.securityHandler.initialize(peripheral)
                
            if request['type'] == 'peripheralAuthenticationTokenResponse':
                peripheralID = request['value']['peripheralID']
                peripheral = self.gwManager.findPeripheralWorkerByIdentifier(peripheralID)
                peripheral.authenticationHandler.setToken(request['value']['authenticationToken'])
                if peripheral.securityHandler != None:
                    peripheral.authenticationHandler.checkAuthentication(peripheral.securityHandler)
            self.gwManager.inQueue.task_done()
        print 'InQueueHandler exiting..'
"""                
                                 

class GWManager(NSObject):
    def init(self):
        self.peripheralWorkers = []
        '''
        0: if down, 
        1: if up but not startScan, 
        2: up and startScan, 
        3: has node connected, still scanning
        4: stopScan, but has peripheral connected
        '''
        self._state = 0
        self.uuid = None
        self.taskQueue = deque()
        self.processingQueue = deque()
        self.connection2Gateway = None
        #self.inQueueHandler = InQueueHandler(self)
        # initialize manager with delegate
        NSLog("Initialize CBCentralManager Worker")
        self.manager = CBCentralManager.alloc().initWithDelegate_queue_(self, nil)
   
        return self
    
    def getUUID(self):
        return self.uuid

    def getPeripheralWorkers(self):
        return self.peripheralWorkers

    def setConnection2Central(self, connection2Gateway):
        self.connection2Gateway = connection2Gateway
        #self.inQueue = self.connection2Gateway.inQueue
        #self.inQueueHandler.start()
        
    def writeReport2Central(self, report):
        self.connection2Gateway.send(json.dumps(report))
        
    def handleRequestFromCentral(self, request):                
        if request['type'] == 'gatewayAuthentication':
            report = {
                       'type': 'gatewayAuthenticationFeedback',
                       'value': {
                                 'authorizationToken': GATEWAY_AUTHENTICATION_TOKEN,
                                 'gatewayUUID': self.uuid
                                 }
                       
                       }
            self.writeReport2Central(report)
            #self.connection2Gateway.send(report)
            
        if request['type'] == 'gatewayUUID':
            self.uuid = request['value']
            print self.uuid
        
        if request['type'] == 'peripheralQuery':
            print 'got query ', request['value']['queryID']
            self.taskQueue.append(request)
            self.processTaskQueue()
            
        if request['type'] == 'peripheralSecurityTypeCheck':
            peripheralID = request['value']['peripheralID']
            peripheral = self.findPeripheralWorkerByIdentifier(peripheralID)
            peripheral.readValueFromPeripheral(SECURITY_SERVICE, SECURITY_TYPE_CHARACTERISTIC)
            
        if request['type'] == 'peripheralAuthenticationHandlerCls':
            peripheralID = request['value']['peripheralID']
            peripheral = self.findPeripheralWorkerByIdentifier(peripheralID)
            authenticationHandlerCls = request['value']['authenticationHandlerCls']
            m = importCode(authenticationHandlerCls, 'authentication')
            peripheral.authenticationHandler = m.Authentication()
            if peripheral.identifier != None:
                peripheral.authenticationHandler.initialize(peripheral)
            report = {
                      'type': 'peripheralAuthenticationTokenQuery',
                      'value': {
                                'peripheralID': peripheralID,
                                }
                      }            
            if report != None:
                self.writeReport2Central(report)                 
            
        if request['type'] == 'peripheralSecurityHandlerCls':
            peripheralID = request['value']['peripheralID']
            peripheral = self.findPeripheralWorkerByIdentifier(peripheralID)
            securityHandlerCls = request['value']['securityHandlerCls']
            m = importCode(securityHandlerCls, 'security')
            peripheral.securityHandler = m.SecurityHandlerFactory(request['value']['securityType'])
            peripheral.securityHandler.initialize(peripheral)
            
        if request['type'] == 'peripheralAuthenticationTokenResponse':
            peripheralID = request['value']['peripheralID']
            peripheral = self.findPeripheralWorkerByIdentifier(peripheralID)
            peripheral.authenticationHandler.setToken(request['value']['authenticationToken'])
            if peripheral.securityHandler != None:
                peripheral.authenticationHandler.checkAuthentication(peripheral.securityHandler)
            
            
    def processTaskQueue(self):
        print 'taskQueue', self.taskQueue
        print 'processing Queue', self.processingQueue
        request = None
        if len(self.taskQueue) != 0:
            request = self.taskQueue.popleft()
            self.processingQueue.append(request)
            
            #queryID = request['value']['queryID']
            peripheralID = request['value']['peripheralID']
            peripheral = self.findPeripheralWorkerByIdentifier(peripheralID)
            if peripheral == None: # not found 
                print 'peripheral for this request not found'
                self.processingQueue.remove(request)
                return
            serviceUUIDStr = request['value']['serviceUUID']
            characteristicUUIDStr = request['value']['characteristicUUID']
        
            if request['value']['action'] == 'Read':
                peripheral.readValueFromPeripheral(serviceUUIDStr, characteristicUUIDStr)
            if request['value']['action'] == 'Write':
                message = request['value']['message']
                peripheral.writeValueForPeripheral(serviceUUIDStr, characteristicUUIDStr, message, True)
            if request['value']['action'] == 'Write Without Response':
                message = request['value']['message']
                peripheral.writeValueForPeripheral(serviceUUIDStr, characteristicUUIDStr, message, False)
                
    def processProcessingQueue(self):
        for request in self.processingQueue:
            peripheralID = request['value']['peripheralID']
            peripheral = self.findPeripheralWorkerByIdentifier(peripheralID)
            if peripheral == None: # not found 
                print 'peripheral for this request not found'
                self.processingQueue.remove(request)
                return
            serviceUUIDStr = request['value']['serviceUUID']
            characteristicUUIDStr = request['value']['characteristicUUID']
        
            if request['value']['action'] == 'Read':
                peripheral.readValueFromPeripheral(serviceUUIDStr, characteristicUUIDStr)
            if request['value']['action'] == 'Write':
                message = request['value']['message']
                peripheral.writeValueForPeripheral(serviceUUIDStr, characteristicUUIDStr, message, True)
            if request['value']['action'] == 'Write Without Response':
                message = request['value']['message']
                peripheral.writeValueForPeripheral(serviceUUIDStr, characteristicUUIDStr, message, False)            
               
    def receiveFeedbackFromPeripheral(self, peripheralID, actionType, serviceUUIDStr, characteristicUUIDStr, value=None, error=None): 
        request2del = None
        report = None
        
        if serviceUUIDStr == SECURITY_SERVICE and characteristicUUIDStr == SECURITY_TYPE_CHARACTERISTIC:              
                report = {
                          'type': 'peripheralSecurityTypeCheck',
                          'value': {
                                    'peripheralID': peripheralID,
                                    'securityType': int(value),
                                    'error': error
                                    }
                          }
        else:                                      
            for request in self.processingQueue:
                if request['value']['action'] == actionType and \
                    request['value']['serviceUUID'] == serviceUUIDStr and \
                    request['value']['characteristicUUID'] == characteristicUUIDStr:
                    # consider the first the met as the corresponding request
                    report = {
                              'type': 'peripheralQueryFeedback',
                              'value': {
                                        'queryID': request['value']['queryID'],
                                        'peripheralID': peripheralID,
                                        'serviceUUID': serviceUUIDStr,
                                        'characteristicUUID': characteristicUUIDStr,
                                        'rtValue': value,
                                        'error': error
                                        }
                              }
                    request2del = request
                    break
            if request2del != None:
                self.processingQueue.remove(request)
        if report != None:
            self.writeReport2Central(report)
     
    def updateState(self, state):
        self._state = state
        if self._state == 0:
            NSLog("CENTRAL MANAGER IS DOWN")
        elif self._state == 1:
            NSLog("CENTRAL MANAGER IS UP")
        elif self._state == 2:
            NSLog("CENTRAL MANAGER IS SCANNING")
        elif self._state == 3:
            NSLog("CENTRAL MANAGER HAS PERIPHERAL(S) CONNECTED, STILL SCANNING")
        elif self._state == 4:
            NSLog("CENTRAL MANAGER HAS PERIPHERAL(S) CONNECTED, SCANNING STOPPED")
        
    def stop(self): # clean up
        NSLog("CLEANING UP..")
        if self.periodicUpdater != None:
            self.periodicUpdater.stop()
            self.periodicUpdater.join()
        #self.inQueueHandler.stop()
        #self.inQueueHandler.join()

    def connectPeripheral(self, peripheralInstance):
        #NSLog("Trying to connnect peripheral %@", peripheral._.UUID)
        options = {
                   CBConnectPeripheralOptionNotifyOnDisconnectionKey:
                   NSNumber.numberWithBool_(YES)
                   }
        self.manager.connectPeripheral_options_(peripheralInstance, options)     
            
    def cancelPeripheralConnection(self, peripheralInstance):
        NSLog("DISCONNECTING FROM PERIPHERAL %@", peripheralInstance._.identifier.UUIDString())        
        self.manager.cancelPeripheralConnection_(peripheralInstance)
            
    def cancelAllConnectionExcept(self, peripheralInstance):
        for worker in self.peripheralWorkers:
            if worker.instance != peripheralInstance:
                self.cancelPeripheralConnection(worker.instance)
                
    def cancelAllConnection(self):
        for worker in self.peripheralWorkers:
            self.cancelPeripheralConnection(worker.instance)
                    
    def findPeripheralWorkerByIdentifier(self, identifier):
        for worker in self.peripheralWorkers:
            if worker.identifier == identifier:
                return worker
        return None
    
    def findWorkerForPeripheralInstance(self, peripheralInstance):
        for w in self.peripheralWorkers:
            if w.instance == peripheralInstance:
                return w           
        return None # not found
    
    def startScan(self):
        NSLog("STARTING SCAN")
        options = NSDictionary.dictionaryWithObject_forKey_(
            NSNumber.numberWithBool_(NO),
            CBCentralManagerScanOptionAllowDuplicatesKey
        )
        self.manager.scanForPeripheralsWithServices_options_(
            nil, # scan everything with any advertisement data
            options
        )
        
    def stopScan(self):
        NSLog("stop scan")
        self.manager.stopScan()
        

    # CBCentralManager delegate methods
    def centralManagerDidUpdateState_(self, central):
        ble_state = central._.state
        if ble_state == CBCentralManagerStateUnkown:
            NSLog("state unkown")
        if ble_state == CBCentralManagerStateResetting:
            NSLog("resetting")
        if ble_state == CBCentralManagerStateUnsupported:
            NSLog("BLE is not supported")
        if ble_state == CBCentralManagerStateUnauthorized:
            NSLog("unauthorized")
        if ble_state == CBCentralManagerStatePoweredOff:
            NSLog("power off")
        self.updateState(0)
        
        if ble_state == CBCentralManagerStatePoweredOn:
            NSLog("ble is ready!!")
            self.updateState(1)
            
            self.startScan()
            
            self.periodicUpdater = PeriodicUpdater(self)
            self.periodicUpdater.start()                 

    '''
    Invoked when the central discovers a EcoBT node while scanning.
    add peripheral list
    '''
    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self,
                                                                     central,
                                                                     peripheral,
                                                                     advtisement_data,
                                                                     rssi):
        NSLog("Found Peripheral %@ %@ %@", peripheral._.name, peripheral._.identifier.UUIDString(), rssi)
        NSLog("%@", advtisement_data)
        
        # check if the peripheral has already been added to the list
        found = self.findWorkerForPeripheralInstance(peripheral)       
        if found == None:            
            worker = PeripheralWorker.alloc().init()        
            worker.setInstance(peripheral)
            worker.setGateway(self)
            self.peripheralWorkers.append(worker)            
            self.connectPeripheral(peripheral)
        
        self.startScan()
            

    def centralManager_didRetrivePeripherals_(self, central, peripherals):
        NSLog("Retrive peripherals")

    def centralManager_didConnectPeripheral_(self, central, peripheral):        
        NSLog("Connected to peripheral %@", peripheral._.name)
            
        NSLog("number of peripherals: %@", len(self.peripheralWorkers))
        
        worker = self.findWorkerForPeripheralInstance(peripheral)       
        if worker != None:         
            # initialize peripheral worker when peripheral is added to the list   
            peripheral.setDelegate_(worker)      
            NSLog("DISCOVERING SERVICES FOR NODE %@", peripheral._.name)
            worker.discoverServices()

    '''
    lost connection from EcoBT node
    '''
    def centralManager_didDisconnectPeripheral_error_(self,
                                                      central,
                                                      peripheral,
                                                      error):
        worker = self.findWorkerForPeripheralInstance(peripheral)
        # dispose worker and remove peripheral
        if worker != None:
            worker.stop()
            self.peripheralWorkers.remove(worker)
            NSLog("Disconnect from Peripheral No %@", peripheral._.identifier.UUIDString())
        else:
            NSLog("Didn't find the peripheral to remove from peripheral list!")

    def centralManager_didFailToConnectPeripheral_error_(self,
                                                         central,
                                                         peripheral,
                                                         error):
        NSLog("Fail to Connect")

    




