'''
Created on Feb 9, 2013

@author: cjhuo

@summary:  interface of Characteristic
'''

class Characteristic(object):
    def __init__(self):
        self.UUID = None
        self.instance = None
        self.privilege = None   # 0: Read Only; 1: Read and Write; 
                                # 2: Read Only but need to be read at the beginning(e.g. System info)
        
    def setUUID(self, UUID):
        self.UUID = UUID
    
    def setInstance(self, instance):
        self.instance = instance
        
    def setPeripheralWorker(self, peripheralWorker):
        self.peripheralWorker = peripheralWorker
        
    def process(self):
        return {'type': 'Not implemented',
                'uuid': self.UUID}