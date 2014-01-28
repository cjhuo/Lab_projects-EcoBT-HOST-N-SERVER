'''
Created on Jan 24, 2014

@author: cjhuo
'''
from Foundation import *
#from PyObjCTools import AppHelper
from config_peripheral import *
from objc import *
import struct

from Characteristic import Characteristic

class TestCharacteristic(Characteristic):
    
        
    def initializeInstance(self):
        print "Initializing Characteristic Instance"
        self.instance = CBMutableCharacteristic.alloc().initWithType_properties_value_permissions_(CBUUID.UUIDWithString_(self.UUID),
                                                       CBCharacteristicPropertyNotify | CBCharacteristicPropertyRead,
                                                       nil, # ensures the value is treated dynamically
                                                       CBAttributePermissionsReadable)


    def initializeDescriptors(self):
        print "Initializing descriptors.."
        
        '''
        Format:8bit, Exponent:sint8, Unit:uint16, Namespace:8bit, Description:16bit
        '''
        data = struct.pack("@BbHBH", 8, 0, 1, 0, 0)
        
        self.instance._.descriptors = [CBMutableDescriptor.alloc().initWithType_value_(CBUUID.UUIDWithString_(CBUUIDCharacteristicUserDescriptionString),
                                                                u'TestDescriptor'),
                                       CBMutableDescriptor.alloc().initWithType_value_(CBUUID.UUIDWithString_(CBUUIDCharacteristicFormatString),
                                                                NSData.alloc().initWithBytes_length_(data, len(data)))
                                       ]
        
    '''
    return unencrypted return value, 
    but should pre-packed into string
    if value is not a string
    '''
    def handleReadRequest(self):
        message = 1234
        message = struct.pack("@i", message)
        return message
        