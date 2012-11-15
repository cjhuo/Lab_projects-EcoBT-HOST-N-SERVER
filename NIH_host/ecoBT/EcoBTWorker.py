'''
Created on Nov 14, 2012

@author: cjhuo
'''
import threading
from Queue import Queue
        
class EcoBTWorker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._queue = Queue() #data queue
        self._global_sockets = []
        
    def run(self):
        while True:
            data = self._queue.get()
            self._queue.task_done()               
            #process data
            print data
            axis, val = data
            data = {'axis': axis, 'value': val}
            for socket in self._global_sockets:
                socket.write_message(data) 
        
    def getGlobalSockets(self, socket):
        return self._global_sockets
    
    def getQueue(self):
        return self._queue
    

class DBinsert(threading.Thread):
    pass
