'''
Created on Jan 24, 2014

@author: cjhuo
'''
from Foundation import *
#from PyObjCTools import AppHelper
from config_peripheral import *
from objc import *

class Characteristic(object):
    def __init__(self, UUID):
        self.UUID = UUID
        self.value = None
        self.instance = None
        self.initializeInstance()
        self.initializeDescriptors()
        
    def initializeInstance(self):
        pass
    
    def initializeDescriptors(self):
        pass
    
    def handleReadRequest(self):
        pass
    
    def handleWriteRequest(self, data):
        pass