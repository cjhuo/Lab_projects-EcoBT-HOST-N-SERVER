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

from EcoBTWorker import EcoBTWorker
from EcoBTCentralManagerDelegateWorker import EcoBTCentralManagerDelegateWorker
from EcoBTPeripheralWorker import EcoBTPeripheralWorker


class EcoBTCentralManagerWorker(NSObject, EcoBTWorker):
    def init(self):
        EcoBTWorker.__init__(self)
        self.peripheralWorkers = []
        self.sockets = None
        # initialize CMdelegate worker
        self.delegateWorker =  EcoBTCentralManagerDelegateWorker()
        self.delegateWorker.start()
        # initialize manager with delegate
        print "Initialize CBCentralManager Worker"
        self.manager = CBCentralManager.alloc().initWithDelegate_queue_(self, nil)
        return self
        
    def stop(self): # clean up
        print "Cleaning Up"
        for w in self.peripheralWorkers:
            w.delegateWorker.getQueue().put('stop')
            w.delegateWorker.join()
            
        self.delegateWorker.getQueue().put('stop')
        self.delegateWorker.join()

    def connectPeripheral(self, peripheral):
        print "Trying to connnect peripheral"
        options = NSDictionary.dictionaryWithObject_forKey_(
            NSNumber.numberWithBool_(YES),
            CBConnectPeripheralOptionNotifyOnDisconnectionKey
        )
        self.manager.connectPeripheral_options_(peripheral, options)
        

    def startScan(self):
        self.manager.scanForPeripheralsWithServices_options_(
            NSArray.arrayWithObject_(CBUUID.UUIDWithString_(u"180D")),
            nil
        )
        
    def stopScan(self):
        print "stop scan"
        self.manager.stopScan()
    

    # CBCentralManager delegate methods
    def centralManagerDidUpdateState_(self, central):
        ble_state = central._.state
        if ble_state == CBCentralManagerStateUnkown:
            print "state unkown"
        elif ble_state == CBCentralManagerStateResetting:
            print "resetting"
        elif ble_state == CBCentralManagerStateUnsupported:
            print "BLE is not supported"
            #AppHelper.stopEventLoop()
        elif ble_state == CBCentralManagerStateUnauthorized:
            print "unauthorized"
        elif ble_state == CBCentralManagerStatePoweredOff:
            print "power off"
        elif ble_state == CBCentralManagerStatePoweredOn:
            print "ble is ready!!"
            
            # for test
            self.startScan()
            #self.startScan()
        else:
            print "test"

    '''
    Invoked when the central discovers a EcoBT node while scanning.
    add peripheral list and send to UI
    '''
    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self,
                                                                     central,
                                                                     peripheral,
                                                                     advtisement_data,
                                                                     rssi):
        print "Found Peripheral ", peripheral._.name, rssi
        NSLog("%@", advtisement_data)
        
        found = self.findWorkerForPeripheral(peripheral) # check if the peripheral has already been added to the list      
        if found == False:
            # initializae peripheral worker when peripheral is added to the list
            worker = EcoBTPeripheralWorker.alloc().init()
            worker.peripheral = peripheral
            self.peripheralWorkers.append(worker)
            
            # for test
            self.connectPeripheral(peripheral)
        
        #send peripherals list to UI !!!!!!!
        
        
        #print "Connect, stopScan"
        #self.stopScan()

    def centralManager_didRetrivePeripherals_(self, central, peripherals):
        print "Retrive peripherals"

    def centralManager_didConnectPeripheral_(self, central, peripheral):
        # Update UI
        
        print "Connected to peripheral ", peripheral._.name
            
        #delegate.sockets = self.sockets     
        
        self.worker = self.findWorkerForPeripheral(peripheral)
        if self.worker != False:
            self.worker.peripheral.setDelegate_(self.worker)
            # start peripheral's delegate worker only when it's connected
            self.worker.delegateWorker.start()
            
            # for test
            self.worker.discoverServices()
        else: 
            print "error, peripheral hasn't been added to watch list"
        #peripheral.discoverServices_(None)


    '''
    lost connection from EcoBT node
    '''
    def centralManager_didDisconnectPeripheral_error_(self,
                                                      central,
                                                      peripheral,
                                                      error):
        worker = self.findWorkerForPeripheral(peripheral)
        # dispose worker and remove peripheral
        if worker != False:
            worker.stop()
            self.peripheralWorkers.remove(worker)
            print "Disconnect"
        else:
            print "Didn't find the peripheral from list"
        #AppHelper.stopEventLoop()
        #sys.exit()

    def centralManager_didFailToConnectPeripheral_error_(self,
                                                         central,
                                                         peripheral,
                                                         error):
        print "Fail to Connect"

    
    def findWorkerForPeripheral(self, peripheral):
        for w in self.peripheralWorkers:
            if w.peripheral == peripheral:
                return w           
        return False # not found



