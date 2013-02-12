'''
Created on Feb 9, 2013

@author: cjhuo
'''

class Service(object):
    def __init__(self):
        self.UUID = None
        self.instance = None
        self.characteristics = []
        
    def setUUID(self, UUID):
        self.UUID = UUID   
        
    def setInstance(self, instance):
        self.instance = instance