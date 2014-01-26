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

class Authentication(Characteristic):
    
        
    def initializeInstance(self):
        self.authenticationToken = None
        print "Initializing Characteristic Instance"
        self.instance = CBMutableCharacteristic.alloc().initWithType_properties_value_permissions_(CBUUID.UUIDWithString_(self.UUID),
                                                       CBCharacteristicPropertyWrite,
                                                       nil, # ensures the value is treated dynamically
                                                       CBAttributePermissionsWriteable)


    def initializeDescriptors(self):
        print "Initializing descriptors.."
        self.instance._.descriptors = [CBMutableDescriptor.alloc().
                                            initWithType_value_(CBUUID.UUIDWithString_(CBUUIDCharacteristicUserDescriptionString),
                                                                u'Authentication')]

    def handleWriteRequest(self, data):
        if self.authenticationToken == None: # first time assign a token
            self.authenticationToken = data
            return True
        else: # compare with stored token
            return self.authenticationToken == data
        