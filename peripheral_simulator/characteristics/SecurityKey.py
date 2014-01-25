'''
Created on Jan 25, 2014

@author: cjhuo
'''
from Foundation import *
#from PyObjCTools import AppHelper
from config_peripheral import *
from objc import *
import random, string, struct

from Characteristic import Characteristic

class SecurityKey(Characteristic):
    
    def initializeInstance(self):
        print "Initializing Characteristic Instance"
        self.instance = CBMutableCharacteristic.alloc().initWithType_properties_value_permissions_(CBUUID.UUIDWithString_(self.UUID),
                                                       CBCharacteristicPropertyRead | CBCharacteristicPropertyWriteWithoutResponse,
                                                       nil, # ensures the value is treated dynamically
                                                       CBAttributePermissionsReadable | CBAttributePermissionsWriteable)


    def initializeDescriptors(self):
        print "Initializing descriptors.."
        self.instance._.descriptors = [CBMutableDescriptor.alloc().
                                            initWithType_value_(CBUUID.UUIDWithString_(CBUUIDCharacteristicUserDescriptionString),
                                                                u'secret key: unicode16')]
        
    def handleReadRequest(self, request, securityHandler):
        #testNSData = NSString.alloc().initWithString_(u'AES').dataUsingEncoding_(NSUTF8StringEncoding) # default value
        self.key = self.randomword(16)
        securityHandler.setParameters(key=self.key)
        request._.value = NSData.alloc().initWithBytes_length_(struct.pack("@16s", self.key), len(self.key))
        return (request, CBATTErrorSuccess[0]) # CBATTErrorSuccess is a tuple, only first one useful

    def _lazysecret(self, secret, blocksize=16, padding='}'):
        if len(secret) != 16:
            if secret < 16:
                return secret + (blocksize - len(secret)) * padding
            else:
                return secret[:16]
        return secret
    
    def randomword(self, length):
        return ''.join(random.sample(string.lowercase+string.digits,length))
    