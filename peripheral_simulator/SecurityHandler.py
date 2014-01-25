'''
Created on Jan 25, 2014

@author: cjhuo
'''

# dynamically load modules from implementation package
import os
for module in os.listdir(os.path.join(os.path.dirname(__file__), "securityHandlers")):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    exec("from securityHandlers import %s" % module[:-3])
del module

class SecurityHandler(object):
    def __init__(self, type):
        self.parameters = {}
        self.type = type
        self.encryptionObj = None
        
    def setType(self, type):
        self.type = type
        
    def setEncryptionObj(self, encyptStr):
        if encyptStr == "AES_CFB":
            self.encryptionObj = AES_CFB.AES_CFB(self.parameters)
    
    def getEncryptionObj(self):
        return self.encryptionObj

        
    def setParameters(self, *args, **kwargs):
        for key, val in kwargs.iteritems():
            self.parameters[key] = val
        try:
            self.setEncryptionObj(self.type)
            print "EncryptionObj initialized"
        except KeyError:
            pass
    
        
        
