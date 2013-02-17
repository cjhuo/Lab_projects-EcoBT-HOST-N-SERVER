'''
Created on Feb 9, 2013

@author: cjhuo
'''

class Service(object):
    def __init__(self, UUID, instance):
        self.UUID = UUID
        self.instance = instance
        self.characteristics = []
        
    def setUUID(self, UUID):
        self.UUID = UUID   
        
    def setInstance(self, instance):
        self.instance = instance