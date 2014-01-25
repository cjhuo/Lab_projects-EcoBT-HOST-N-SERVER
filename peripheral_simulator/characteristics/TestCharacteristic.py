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
        self.instance._.descriptors = [CBMutableDescriptor.alloc().
                                            initWithType_value_(CBUUID.UUIDWithString_(CBUUIDCharacteristicUserDescriptionString),
                                                                u'TestDescriptor')]
        
    def handleReadRequest(self, request, securityHandler):
        if securityHandler.getEncryptionObj() != None:
            ciphertext = securityHandler.getEncryptionObj().encrypt("bytes")
            data = struct.pack("@"+str(len(ciphertext))+"s", ciphertext)          
            #testNSData = NSString.alloc().initWithString_(u'1234').dataUsingEncoding_(NSUTF8StringEncoding) # default value
            request._.value = NSData.alloc().initWithBytes_length_(data, len(data))
            return (request, CBATTErrorSuccess[0]) # CBATTErrorSuccess is a tuple, only first one useful
        else:
            return (request, CBATTErrorReadNotPermitted)
        