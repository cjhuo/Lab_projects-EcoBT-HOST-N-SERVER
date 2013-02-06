'''
Created on Feb 5, 2013

@author: cjhuo

@summary: monitor the input queue where command sent from UI is stored, and send to where the worker belongs to
A CM delegate worker has members as below:
list of connected sockets

'''
from EcoBTDelegateWorker import EcoBTDelegateWorker
from threading import Event

class EcoBTCentralManagerDelegateWorker(EcoBTDelegateWorker):
    def __init__(self):
        EcoBTDelegateWorker.__init__(self)

    def run(self):
        while True:
            data = self._queue.get()
            self._queue.task_done()               
            #process data
            if(data != 'stop'):
                if(len(self._global_sockets) != 0):
                    #print data
                    axis, val = data
                    data = {'axis': axis, 'value': val}
                    for socket in self._global_sockets:
                        socket.write_message(data) 
            else: # stop signal received
                break
    
