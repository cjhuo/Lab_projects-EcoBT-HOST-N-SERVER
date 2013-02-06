'''
Created on Feb 6, 2013

@author: cjhuo

@summary: 
EcoBTDeleageteWorker Interface
'''

import threading
from Queue import Queue  

class EcoBTDelegateWorker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._queue = Queue() #data queue
        self._global_sockets = []

    def run(self):
        pass
    
    def getQueue(self):
        return self._queue
                    
    def getGlobalSockets(self):
        return self._global_sockets
    
    def setGlobalSockets(self):
        return self._global_sockets