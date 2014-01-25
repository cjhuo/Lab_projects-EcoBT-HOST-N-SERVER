'''
Created on Jan 25, 2014

@author: cjhuo
'''
from Foundation import *
#from PyObjCTools import AppHelper
from config_peripheral import *
from objc import *
import struct

from Characteristic import Characteristic

class SecurityType(Characteristic):
    
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
                                                                u'AES_CFB: "uint8",\
                                                                parameters:\
                                                                1. secret key: unicode16,\
                                                                2. IV: unicode16')]        
        
    def handleReadRequest(self, request, securityHandler):
        #testNSData = NSString.alloc().initWithString_(u'AES').dataUsingEncoding_(NSUTF8StringEncoding) # default value
        data = struct.pack("@B", 1)
        request._.value = NSData.alloc().initWithBytes_length_(data, len(data))
        return (request, CBATTErrorSuccess[0]) # CBATTErrorSuccess is a tuple, only first one useful
