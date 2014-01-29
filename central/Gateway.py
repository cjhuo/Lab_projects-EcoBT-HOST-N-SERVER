'''
Created on Jan 27, 2014

@author: cjhuo
'''

class Gateway(object):
    def __init__(self):
        self.authtorized = False
        self.peripherals = None
        self.uuid = None
        
    def setUUID(self, uuid):
        self.uuid = uuid
        return self.uuid
        
    def isAuthorized(self):
        return self.authtorized
    
    def getUUID(self):
        return self.uuid
    
    def setAuthorized(self, authorized):
        self.authtorized = authorized