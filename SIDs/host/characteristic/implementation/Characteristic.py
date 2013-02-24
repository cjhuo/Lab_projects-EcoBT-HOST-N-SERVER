'''
Created on Feb 9, 2013

@author: cjhuo

@summary:  interface of Characteristic
'''

class Characteristic(object):
    def __init__(self):
        self.UUID = None
        self.instance = None
        self.service = None # tell u which this characteristic belongs
        self.privilege = None   # 0: Read Only; 1: Read and Write; 
                                # 2: Read Only but need to be read at the beginning(e.g. System info)
        
    def setUUID(self, UUID):
        self.UUID = UUID
    
    def setInstance(self, instance):
        self.instance = instance
    
    def setService(self, service):
        self.service = service 
        
    def setPeripheralWorker(self, peripheralWorker):
        self.peripheralWorker = peripheralWorker
        
    def setUUIDInstanceServicePeripheralWorker(self, UUID, instance, service, peripheralWorker):
        self.UUID = UUID
        self.instance = instance
        self.service = service
        self.peripheralWorker = peripheralWorker
        
    def setRole(self):
        pass
        
    def process(self):
        return {'type': 'Not implemented',
                'uuid': self.UUID}