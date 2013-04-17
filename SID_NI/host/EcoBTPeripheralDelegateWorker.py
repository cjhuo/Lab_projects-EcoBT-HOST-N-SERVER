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
        self.number = None # peripheral's sequence number


    def run(self):
        while True:
            data = self._queue.get()
            self._queue.task_done()
            #print 'sockets: ', self.getGlobalSockets()               
            #process data
            if data != 'stop':
                try:
                    if data['type'] == 'deviceInfo':
                        self.address = data['value']
                except Exception:
                    print "Data Invalid!!!", data
                #print "Peripheral delegate worker ", self.number, " got data from Queue: \n", data
                if len(self._global_sockets) != 0:
                    #print data
                    data['address'] = self.address # add peripheral's MAC address as its name
                    data['number'] = self.number
                    packet = {'from': 'node', 'data': data}
                    for socket in self._global_sockets.sockets:
                        socket.write_message(packet) 
            else: # stop signal received
                break
                    