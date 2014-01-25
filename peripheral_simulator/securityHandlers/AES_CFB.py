'''
Created on Jan 25, 2014

@author: cjhuo
'''

from Crypto.Cipher import AES

class AES_CFB(object):
    
    def __init__(self, parameters):
        self.obj = AES.new(parameters['key'], AES.MODE_CFB, parameters['IV'])
    
    def encrypt(self, message):
        return self.obj.encrypt(message)
    
    def decript(self, message):
        return self.obj.decrypt(message)