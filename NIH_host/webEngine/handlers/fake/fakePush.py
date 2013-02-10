'''
Created on Nov 1, 2012

@author: cjhuo
'''
from fakeDataGenerator import FakeDataGenerator
from periodicExecutor import PeriodicExecutor
from misc.Singleton import Singleton

class FakePush(Singleton):  #to acchieve singleton of fakepush
    
    def __init__(self, ds):
        self.global_sockets = []
        self.ds = ds           
        #for demo purpose
        PeriodicExecutor(2, self.pushData).start()
        
    def getGlobalSockets(self):
        return self.global_sockets
                
    def pushData(self):
        if len(self.global_sockets) != 0:
            val = FakeDataGenerator(self.ds).db_insert()
            for socket in self.global_sockets:
                socket.write_message(val)