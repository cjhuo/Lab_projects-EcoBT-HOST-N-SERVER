'''
Created on Feb 5, 2013

@author: cjhuo

@summary: 
monitor the output queue where data generated from EcoBT node is stored, and broadcast to UI

'''
from EcoBTDelegateWorker import EcoBTDelegateWorker
from multiprocessing import Value

class EcoBTPeripheralDelegateWorker(EcoBTDelegateWorker):
    def __init__(self):
        EcoBTDelegateWorker.__init__(self)
        self.address = None # mac address of this peripheral


    def run(self):
        while True:
            data = self._queue.get()
            self._queue.task_done()
            #print 'sockets: ', self.getGlobalSockets()               
            #process data
            if data != 'stop':
                print data
                if data['type'] == 'deviceInfo':
                    self.address = data['value']
                elif len(self._global_sockets) != 0:
                    #print data
                    data['name'] = self.address # add peripheral's MAC address as its name
                    for socket in self._global_sockets.sockets:
                        socket.write_message(data) 
            else: # stop signal received
                break
                    