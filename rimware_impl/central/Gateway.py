'''
Created on Jan 27, 2014

@author: cjhuo
'''

class Gateway(object):
    def __init__(self):
        self.authtorized = False
        self.peripherals = None
        self.uuid = None
        self.pinger = None
        
    def setUUID(self, uuid):
        self.uuid = uuid
        return self.uuid
        
    def isAuthorized(self):
        return self.authtorized
    
    def getUUID(self):
        return self.uuid
    
    def setAuthorized(self, authorized):
        self.authtorized = authorized
    
    def setPeriodicPinger(self, pinger):
        self.pinger = pinger
        
    def getPeriodicPinger(self):
        return self.pinger