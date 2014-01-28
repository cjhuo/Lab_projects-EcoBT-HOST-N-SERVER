'''
Created on Jan 28, 2014

@author: cjhuo
'''


def SecurityHandlerFactory(securityType):
    if securityType == 1:
        return AES_CFB()
    
class SecurityHandler(object):
    def __init__(self):
        self.secured = False
        self.peripheralWorker = None
            
    def initialize(self, peripheralWorker):
        pass
            
    
    def isSecured(self):
        pass
    
    def setParameter(self, characteristic):
        pass
    
    def reset(self):
        pass
    
class AES_CFB(SecurityHandler):
    def __init__(self):
        SecurityHandler.__init__(self)
        self.key = None
        self.IV = None
        self.encryptionObj = None
    
    def initialize(self, peripheralWorker):
        self.peripheralWorker = peripheralWorker
        peripheralWorker.readValueForCharacteristic('7772')
        peripheralWorker.readValueForCharacteristic('7773')
        
    def isSecured(self):
        return self.encryptionObj != None
        
    def setParameter(self, characteristic):
        import struct
        from Crypto.Cipher import AES
        if self.peripheralWorker.UUID2Str(characteristic._.UUID) == '7772': #key
            self.key, = struct.unpack("@16s", characteristic._.value)
        if self.peripheralWorker.UUID2Str(characteristic._.UUID) == '7773': #key
            self.IV, = struct.unpack("@16s", characteristic._.value)
        try:
            self.encryptionObj = AES.new(self.key, AES.MODE_CFB, self.IV)
            print "EncryptionObj initialized"
        except:
            pass        
    
    def reset(self):
        self.key = None
        self.IV = None
        self.encryptionObj = None
        
            
            