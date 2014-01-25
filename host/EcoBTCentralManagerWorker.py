'''
@summary: 
monitor the input queue where command sent from UI is stored, and send to where the worker belongs to\
A manager worker has members as below:
instance of central manager,
instance of central manager delegate,
list of discovered peripheral workers
'''  

from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *
from PyObjCTools import AppHelper

from Queue import Queue 
import time

from EcoBTWorker import EcoBTWorker
from EcoBTCentralManagerDelegateWorker import EcoBTCentralManagerDelegateWorker
from EcoBTPeripheralWorker import EcoBTPeripheralWorker

from Peripheral import Peripheral


class EcoBTCentralManagerWorker(NSObject, EcoBTWorker):
    def init(self):
        EcoBTWorker.__init__(self)
        self.peripheralWorkers = []
        # initialize CMdelegate worker
        self.delegateWorker =  EcoBTCentralManagerDelegateWorker()
        self.delegateWorker.setEcoBTWorker(self)
        self.delegateWorker.start()
        self.pNum = 0 # this number is for each peripheral to identify themselves
        '''
        0: if down, 
        1: if up but not startScan, 
        2: up and startScan, 
        3: has node connected, still scanning
        4: stopScan, but has peripheral connected
        '''
        self.state = 0
        # initialize manager with delegate
        NSLog("Initialize CBCentralManager Worker")
        self.manager = CBCentralManager.alloc().initWithDelegate_queue_(self, nil)
        return self
    
    def setSockets(self, sockets):
        self.sockets = sockets
        self.delegateWorker.setGlobalSockets(sockets)
        
    def stop(self): # clean up
        NSLog("Cleaning Up")
        for w in self.peripheralWorkers:
            w.delegateWorker.getQueue().put('stop')
            w.delegateWorker.join()
            
        self.delegateWorker.getQueue().put('stop')
        self.delegateWorker.join()

    def connectPeripheral(self, peripheral):
        #NSLog("Trying to connnect peripheral %@", peripheral._.UUID)
        options = NSDictionary.dictionaryWithObject_forKey_(
            NSNumber.numberWithBool_(YES),
            CBConnectPeripheralOptionNotifyOnDisconnectionKey
        )
        self.manager.connectPeripheral_options_(peripheral, options)     
            
    def cancelPeripheralConnection(self, peripheral):
        if type(peripheral) == Peripheral:
            self.manager.cancelPeripheralConnection_(peripheral.instance)
            NSLog("DISCONNECTING FROM PERIPHERAL %@", peripheral.address)
        else:
            self.manager.cancelPeripheralConnection_(peripheral)
            
    def cancelAllConnectionExcept(self, peripheral):
        for worker in self.peripheralWorkers:
            if worker.peripheral.address != peripheral.address:
                self.cancelPeripheralConnection(worker.peripheral)
                
    def cancelAllConnection(self):
        for worker in self.peripheralWorkers:
            self.cancelPeripheralConnection(worker.peripheral)
            
        
    def findPeripheralWorkerByAddress(self, address):
        for worker in self.peripheralWorkers:
            if worker.peripheral.address == address:
                return worker
        return None

    def startScan(self):
        NSLog("STARTING SCAN")
        options = NSDictionary.dictionaryWithObject_forKey_(
            NSNumber.numberWithBool_(NO),
            CBCentralManagerScanOptionAllowDuplicatesKey
        )
        self.manager.scanForPeripheralsWithServices_options_(
            [CBUUID.UUIDWithString_(u"180D"), CBUUID.UUIDWithString_(u"7780"), CBUUID.UUIDWithString_(u"1801")],
            options
        )
        
    def stopScan(self):
        NSLog("stop scan")
        self.manager.stopScan()
        
    def sendState(self):
        data = {'type': 'state',
                'value': self.state}
        self.delegateWorker.getQueue().put(data)     
        
    def sendPeripheralList(self):
        data = {'type': 'peripheralList',
                'value': []
                }
        for worker in self.peripheralWorkers:
            p = {'name': worker.peripheral.name,
                 'rssi': worker.peripheral.rssi,
                 'number': worker.peripheral.number,
                 'address': worker.peripheral.address,
                 'type': worker.peripheral.type
                 }
            data['value'].append(p)
        self.delegateWorker.getQueue().put(data)
        
    def sendFailMessage(self, message):
        msg = {
               'type': 'message',
               'value': message
               }
        self.delegateWorker.getQueue().put(msg)

    # CBCentralManager delegate methods
    def centralManagerDidUpdateState_(self, central):
        ble_state = central._.state
        if ble_state == CBCentralManagerStateUnkown:
            NSLog("state unkown")
            self.state = 0
            self.sendFailMessage("state unkown")
        elif ble_state == CBCentralManagerStateResetting:
            NSLog("resetting")
            self.state = 0
            self.sendFailMessage("resetting")
        elif ble_state == CBCentralManagerStateUnsupported:
            NSLog("BLE is not supported")
            self.state = 0
            self.sendFailMessage("BLE is not supported")
            self.sendState()
            #AppHelper.stopEventLoop()
        elif ble_state == CBCentralManagerStateUnauthorized:
            NSLog("unauthorized")
            self.state = 0
            self.sendFailMessage("unauthorized")
        elif ble_state == CBCentralManagerStatePoweredOff:
            NSLog("power off")
            self.state = 0
            self.sendFailMessage("power off")
        elif ble_state == CBCentralManagerStatePoweredOn:
            NSLog("ble is ready!!")
            
            
            
            self.state = 1
            self.sendState()
            '''
            # for test purpose
            self.startScan()
            self.state = 2
            self.sendState()
            '''
            
            #self.startScan()
        else:
            NSLog("Can't get Central Manager's state!")
            raise Exception

    '''
    Invoked when the central discovers a EcoBT node while scanning.
    add peripheral list and send to UI
    '''
    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self,
                                                                     central,
                                                                     peripheral,
                                                                     advtisement_data,
                                                                     rssi):
        NSLog("Found Peripheral %@ %@", peripheral._.name, rssi)
        NSLog("%@", advtisement_data)
        
        # update self's state and send to UI
        self.state = 3
        self.sendState()
        # check if the peripheral has already been added to the list
        found = self.findWorkerForPeripheralInstance(peripheral)       
        if found == False:
            # initializae peripheral worker when peripheral is added to the list
            worker = EcoBTPeripheralWorker.alloc().init()
            worker.setSockets(self.sockets)
            #print 'Peripheral socket: ', worker.sockets
            
            worker.setPeripheral(Peripheral(peripheral, peripheral._.name, rssi, self.pNum))
            self.pNum += 1
            self.peripheralWorkers.append(worker)
            
            # for test
            self.connectPeripheral(peripheral)
            self.startScan()
        
        #send peripherals list to UI !!!!!!!
        
        
        #print "Connect, stopScan"
        #self.stopScan()

    def centralManager_didRetrivePeripherals_(self, central, peripherals):
        NSLog("Retrive peripherals")

    def centralManager_didConnectPeripheral_(self, central, peripheral):
        # Update UI
        
        NSLog("Connected to peripheral %@", peripheral._.name)
            
        #delegate.sockets = self.sockets     
        NSLog("number of peripherals: %@", len(self.peripheralWorkers))
        w = self.findWorkerForPeripheralInstance(peripheral)
        if w != False:
            # start peripheral's delegate worker only when it's connected
            w.peripheral.instance.setDelegate_(w)
            w.delegateWorker.start()
            
            # for test
            NSLog("DISCOVERING SERVICES FOR NODE %@", w.peripheral.address)
            w.discoverServices()
        else: 
            NSLog("error, peripheral hasn't been added to watch list")
            raise Exception
        #peripheral.discoverServices_(None)


    '''
    lost connection from EcoBT node
    '''
    def centralManager_didDisconnectPeripheral_error_(self,
                                                      central,
                                                      peripheral,
                                                      error):
        worker = self.findWorkerForPeripheralInstance(peripheral)
        # dispose worker and remove peripheral
        if worker != False:
            worker.stop()
            self.peripheralWorkers.remove(worker)
            NSLog("Disconnect from Peripheral No %@", worker.peripheral.number)
            self.sendFailMessage("Disconnect from Peripheral %s" % worker.peripheral.name)
        else:
            NSLog("Didn't find the peripheral to remove from peripherhal list!")
        
        # update UI
        self.sendPeripheralList()
        #AppHelper.stopEventLoop()
        #sys.exit()

    def centralManager_didFailToConnectPeripheral_error_(self,
                                                         central,
                                                         peripheral,
                                                         error):
        NSLog("Fail to Connect")

    
    def findWorkerForPeripheralInstance(self, peripheralInstance):
        for w in self.peripheralWorkers:
            if w.peripheral.instance == peripheralInstance:
                return w           
        return False # not found



