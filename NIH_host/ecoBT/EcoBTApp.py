from Cocoa import NSKeyDown, NSKeyUp, NSKeyDownMask, NSEvent, NSControlKeyMask
from Foundation import *

from PyObjCTools import AppHelper
from AppKit import NSApp, NSApplication, NSWorkspace

from IOBluetooth import *
from objc import *

import array
import binascii
import struct


class EcoBTApp():
    def __init__(self, worker):
        self.pool = NSAutoreleasePool.alloc().init()
        self.delegate = EcoBTDelegate.alloc().init()
        self.delegate.setWorker(worker)
        self.runLoop = NSRunLoop.currentRunLoop()
        self.runLoop.run()
        self.pool.release()

class EcoBTDelegate(NSObject):
    def init(self):
        self.connected = False
        self.connected_peripheral = None
        print "Set CBCentralManager delegate"
        self.manager = CBCentralManager.alloc().initWithDelegate_queue_(self, nil)
        return self

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
            AppHelper.stopEventLoop()
        elif ble_state == CBCentralManagerStateUnauthorized:
            print "unauthorized"
        elif ble_state == CBCentralManagerStatePoweredOff:
            print "power off"
        elif ble_state == CBCentralManagerStatePoweredOn:
            print "ble is ready!!"
            self.startScan()
        else:
            print "test"

    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self,
                                                                     central,
                                                                     peripheral,
                                                                     advtisement_data,
                                                                     rssi):
        print "Found Peripheral ", peripheral._.name, rssi
        NSLog("%@", advtisement_data)
        options = NSDictionary.dictionaryWithObject_forKey_(
            NSNumber.numberWithBool_(YES),
            CBConnectPeripheralOptionNotifyOnDisconnectionKey
        )
        self.connected_peripheral = peripheral
        self.connected_peripheral.setDelegate_(self)
        self.manager.connectPeripheral_options_(peripheral, options)
        print "Connect, stopScan"
        self.stopScan()

    def centralManager_didRetrivePeripherals_(self, central, peripherals):
        print "Retrive peripherals"

    def centralManager_didConnectPeripheral_(self, central, peripheral):
        print "Connected to peripheral ", peripheral._.name
        self.connected = True
        self.connected_peripheral.discoverServices_(None)

    def centralManager_didDisconnectPeripheral_error_(self,
                                                      central,
                                                      peripheral,
                                                      error):
        self.connected = False
        print "Disconnect"

    def centralManager_didFailToConnectPeripheral_error_(self,
                                                         central,
                                                         peripheral,
                                                         error):
        print "Fail to Connect"

    # CBPeripheral delegate methods
    def peripheral_didDiscoverServices_(self, peripheral, error):
        for service in peripheral._.services:
            print "Service found with UUID: ", service._.UUID
            if service._.UUID == CBUUID.UUIDWithString_("180D"):
                print "UUID Matched!!"
            elif service._.UUID == CBUUID.UUIDWithString_("FFA0"):
                print "%s Found!!" % service._.UUID
                peripheral.discoverCharacteristics_forService_(nil, service)
            else:
                pass


    def peripheral_didDiscoverCharacteristicsForService_error_(self,
                                                               peripheral,
                                                               service,
                                                               error):
        print "didDiscoverCharacteristicsForService"
        if service._.UUID == CBUUID.UUIDWithString_("FFA0"):
            print "discovering chars"
            for char in service._.characteristics:
                NSLog("%@", char._.UUID)
                notify_list = []
                notify_list.append(CBUUID.UUIDWithString_("FFA3"))
                notify_list.append(CBUUID.UUIDWithString_("FFA4"))
                notify_list.append(CBUUID.UUIDWithString_("FFA5"))
                if char._.UUID in notify_list:
                    print "Set Notify for ", char._.UUID
                    peripheral.setNotifyValue_forCharacteristic_(True, char)
                if char._.UUID == CBUUID.UUIDWithString_("FFA1"):
                    self.connected_peripheral.readValueForCharacteristic_(char)



    def peripheral_didUpdateValueForCharacteristic_error_(self,
                                                          peripheral,
                                                          characteristic,
                                                          error):
#        print "Read Characteristic(%s) value" % characteristic._.UUID
        if characteristic._.UUID == CBUUID.UUIDWithString_("FFA1"):
            hex_str = binascii.hexlify(characteristic._.value)
            acc_enable = int(hex_str, base=16)
            if acc_enable == 0:
                print "Enable ACC"
                byte_array = array.array('b', chr(1))
            else:
                print "Disable ACC"
                byte_array = array.array('b', chr(0))
            val_data = NSData.dataWithBytes_length_(byte_array, len(byte_array))
            peripheral.writeValue_forCharacteristic_type_(
                val_data, characteristic,
                CBCharacteristicWriteWithResponse)
        # FFA3: x, FFA4: y, FFA5: z
        if characteristic._.UUID == CBUUID.UUIDWithString_("FFA3") or\
           characteristic._.UUID == CBUUID.UUIDWithString_("FFA4") or\
           characteristic._.UUID == CBUUID.UUIDWithString_("FFA5"):     
            hex_str = binascii.hexlify(characteristic._.value)
            print characteristic._.UUID, hex_str, int(hex_str, base=16)            
            
            # put data into queue
            if characteristic._.UUID == CBUUID.UUIDWithString_("FFA3"):
                data = ('x', int(hex_str, base=16))                
                self.worker.getQueue().put(data)
            elif characteristic._.UUID == CBUUID.UUIDWithString_("FFA4"):
                data = ('y', int(hex_str, base=16))                
                self.worker.getQueue().put(data)
            elif characteristic._.UUID == CBUUID.UUIDWithString_("FFA5"):    
                data = ('z', int(hex_str, base=16))                
                self.worker.getQueue().put(data)

    def setWorker(self, worker):
        self.worker = worker
        #self.worker.getQueue().put('This is a test')
    
    def peripheral_didWriteValueForCharacteristic_error_(self,
                                                         peripheral,
                                                         characteristic,
                                                         error):
        pass

    def peripheral_didUpdateNotificationStateForCharacteristic_error_(self,
                                                                      peripheral,
                                                                      characteristic,
                                                                      error):
        print "char(" + str(characteristic._.UUID) + ") is auto-notify? " + str(characteristic.isNotifying())


def main():
    # app = NSApplication.sharedApplication()
    #global pool, delegate, s

    pool = NSAutoreleasePool.alloc().init()
    delegate = EcoBTDelegate.alloc().init()
    # s = objc.selector(delegate.centralManagerDidUpdateState_,signature='v')

    # now = NSDate.alloc().init()
#    timer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(
#            now, 1, delegate, s, None, True)

    runLoop = NSRunLoop.currentRunLoop()
#    runLoop.addTimer_forMode_(timer, NSDefaultRunLoopMode)
    runLoop.run()
    # NSApp().setDelegate_(delegate)
    # globals()['workspace'] = NSWorkspace.sharedWorkspace()
    # AppHelper.runEventLoop()
    pool.release()
    
if __name__ == '__main__':
    #main()
    worker = 'test'
    EcoBTApp(worker)

    
