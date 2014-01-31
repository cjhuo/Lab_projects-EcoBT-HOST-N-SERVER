'''
Created on Jan 24, 2014

@author: cjhuo
'''
from Foundation import *
#from PyObjCTools import AppHelper
from config_peripheral import *
from objc import *

class Service(object):
    def __init__(self, UUID, primary, characteristics):
        self.UUID = UUID
        self.characteristics = characteristics
        if primary is True:
            self.instance = CBMutableService.alloc().initWithType_primary_(CBUUID.UUIDWithString_(UUID), YES)
        else:
            pass # not implemented yet
        
        charInstList = []
        for char in characteristics:
            charInstList.append(char.instance)
        self.instance._.characteristics = charInstList