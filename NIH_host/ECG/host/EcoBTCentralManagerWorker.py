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
        

    def startScan(self):
        options = NSDictionary.dictionaryWithObject_forKey_(
            NSNumber.numberWithBool_(YES),
            CBCentralManagerScanOptionAllowDuplicatesKey
        )
        self.manager.scanForPeripheralsWithServices_options_(
            NSArray.arrayWithObject_(CBUUID.UUIDWithString_(u"180D")),
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
        
    def startTestECG(self, address): #address could be the pNum or address
        for worker in self.peripheralWorkers:
            if worker.peripheral.address == address: # found the ecg peripheral
                NSLog("SENDING START TEST RECORDING SIGNAL FROM CMANAGER")
                char = worker.findCharacteristicByUUID("FEC5")
                char.service.sampleRecorded = False # create a flag to indicate the samples hasn't been recorded   
                worker.writeValueForCharacteristic(char.createStopFlag(), char)
                time.sleep(3)
                worker.writeValueForCharacteristic(char.createStartFlag(), char)
                
    def startECG(self, address):
        for worker in self.peripheralWorkers:
            if worker.peripheral.address == address: # found the ecg peripheral
                NSLog("SENDING START REAL RECORDING SIGNAL FROM CMANAGER")
                char = worker.findCharacteristicByUUID("FEC5")
                # not creating a flag to indicate the samples hasn't been recorded   
                worker.writeValueForCharacteristic(char.createStopFlag(), char)
                time.sleep(3)
                worker.writeValueForCharacteristic(char.createStartFlag(), char)

    def stopECG(self, address):
        for worker in self.peripheralWorkers:
            if worker.peripheral.address == address: # found the ecg peripheral
                NSLog("SENDING STOP REAL RECORDING SIGNAL FROM CMANAGER")
                char = worker.findCharacteristicByUUID("FEC5")
                worker.writeValueForCharacteristic(char.createStopFlag(), char)
                                
    def readECGData(self, address):
        for worker in self.peripheralWorkers:
            if worker.peripheral.address == address: # found the ecg peripheral
                NSLog("SENDING RECORDED SAMPLES TO CLIENT")
                service = worker.findServiceByUUID("FEC0")
                data = service.queue.get()
                service.queue.task_done()
                return data           
        return "Not found"

    # CBCentralManager delegate methods
    def centralManagerDidUpdateState_(self, central):
        ble_state = central._.state
        if ble_state == CBCentralManagerStateUnkown:
            NSLog("state unkown")
        elif ble_state == CBCentralManagerStateResetting:
            NSLog("resetting")
        elif ble_state == CBCentralManagerStateUnsupported:
            NSLog("BLE is not supported")
            #AppHelper.stopEventLoop()
        elif ble_state == CBCentralManagerStateUnauthorized:
            NSLog("unauthorized")
        elif ble_state == CBCentralManagerStatePoweredOff:
            NSLog("power off")
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
        found = self.findWorkerForPeripheral(peripheral)       
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
        w = self.findWorkerForPeripheral(peripheral)
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
        worker = self.findWorkerForPeripheral(peripheral)
        # dispose worker and remove peripheral
        if worker != False:
            worker.stop()
            self.peripheralWorkers.remove(worker)
            NSLog("Disconnect from Peripheral No %@", worker.peripheral.number)
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

    
    def findWorkerForPeripheral(self, peripheral):
        for w in self.peripheralWorkers:
            if w.peripheral.instance == peripheral:
                return w           
        return False # not found



