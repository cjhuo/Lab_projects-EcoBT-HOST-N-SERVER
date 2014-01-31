'''
Created on Jan 25, 2014

@author: cjhuo
'''


from Foundation import *
#from PyObjCTools import AppHelper
from config_peripheral import *
from objc import *
import struct, binascii

from Characteristic import Characteristic

class DeviceInfo(Characteristic):
    
        
    def initializeInstance(self):
        print "Initializing Characteristic Instance"
        self.instance = CBMutableCharacteristic.alloc().initWithType_properties_value_permissions_(CBUUID.UUIDWithString_(self.UUID),
                                                       CBCharacteristicPropertyRead,
                                                       nil, # ensures the value is treated dynamically
                                                       CBAttributePermissionsReadable)


    def initializeDescriptors(self):
        print "Initializing descriptors.."
        self.instance._.descriptors = [CBMutableDescriptor.alloc().
                                            initWithType_value_(CBUUID.UUIDWithString_(CBUUIDCharacteristicUserDescriptionString),
                                                                u'DeviceInformation')]
        
    '''
    return unencrypted return value, 
    but should pre-packed into string
    if value is not a string
    '''
    def handleReadRequest(self):
        message = 0xC8E0EBFFFE16B31A 
        data = struct.pack("@Q", message)
        return NSData.alloc().initWithBytes_length_(data, len(data))
        