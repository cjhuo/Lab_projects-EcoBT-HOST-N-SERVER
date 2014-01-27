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

from PeripheralWorker import PeripheralWorker

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
            print 'sending snapshot to central'
            gatewayOverview = {}
            gatewayOverview['gateway_id'] = self.gatewayManager.getUUID()
            gatewayOverview['connected_peripherals'] = []
            for peripheralWorker in self.gatewayManager.getPeripheralWorkers():
                temp = {}
                temp['id'] = peripheralWorker.getIdentifier()
                temp['profileHierarchy'] = peripheralWorker.getProfileHierarchy()
                gatewayOverview['connected_peripherals'].append(temp)
            message = {
                       'type': 'snapshot',
                       'value': gatewayOverview
                       }
            try:
                self.gatewayManager.writeReport2Gateway(message)
            except:
                print 'error happened when sending update to central'
                 

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
        # initialize manager with delegate
        NSLog("Initialize CBCentralManager Worker")
        self.manager = CBCentralManager.alloc().initWithDelegate_queue_(self, nil)
   
        return self
    
    def getUUID(self):
        return self.uuid

    def getPeripheralWorkers(self):
        return self.peripheralWorkers

    def setConnection2Gateway(self, connection2Gateway):
        self.connection2Gateway = connection2Gateway
        
    def writeReport2Gateway(self, report):
        self.connection2Gateway.send(json.dumps(report))
        
    def handleRequestFromGateway(self, request):        
        if request['type'] == 'gatewayAuthentication':
            message = {
                       'type': 'gatewayAuthenticationFeedback',
                       'value': {
                                 'authorizationToken': GATEWAY_AUTHENTICATION_TOKEN,
                                 'gatewayUUID': self.uuid
                                 }
                       
                       }
            self.writeReport2Gateway(message)
            #self.connection2Gateway.send(message)
            
        if request['type'] == 'gatewayUUID':
            self.uuid = request['value']
            print self.uuid
        
     
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
            
        
    def findPeripheralWorkerByAddress(self, address):
        for worker in self.peripheralWorkers:
            if worker.address == address:
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

    




