'''
Created on Jan 28, 2014

@author: cjhuo
'''

class Authentication(object):
    def __init__(self):
        self.token = None
        self.peripheralWorker = None
        self.authorized = False
    
    def initialize(self, peripheralWorker):
        self.peripheralWorker = peripheralWorker
        import random
        
        # check if the peripheral's token is stored in central's knowledge base
        # TBD
        # else generate one and store it
        if self.token == None:
            self.token = random.getrandbits(64)
    
    def checkAuthentication(self, securityHandler=None):
        from config_central import AUTHENTICATION_CHAR
        import struct, binascii
        data = binascii.hexlify(struct.pack("@Q", self.token))
        print 'Assigning an authentication to peripheral', self.peripheralWorker.identifier, ': ', self.token
        if securityHandler != None:
            data = securityHandler.encrypt(data)
        self.peripheralWorker.writeValueForCharacteristic(data, AUTHENTICATION_CHAR, True)
        self.authorized = True
    
    def reset(self):
        self.authorized = None
        self.initialize(peripheralWorker)
    
    def isAuthorized(self):
        return self.authorized