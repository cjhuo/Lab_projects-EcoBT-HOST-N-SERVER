'''
Created on Feb 10, 2013

@author: cjhuo
'''
from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *

import json

import tornado.websocket

class EcoBTWebSocket(tornado.websocket.WebSocketHandler):
    def initialize(self, globalSockets, ecoBTApp):
        self.globalSockets = globalSockets    
        self.ecoBTApp = ecoBTApp               
        
    def open(self):
        self.globalSockets.append(self)
        self.handleMessage("sendState")
        print "WebSocket opened"

    def on_close(self):
        self.globalSockets.remove(self)
        '''
        if len(self.globalSockets) == 0: # time to ask host to stopScan
            self.handleMessage("stopScan")
        '''
        print "WebSocket closed"
        
    def on_message(self, message):
        #self.ecoBTApp.managerWorker.delegateWorker.getQueue().put(message)
        self.handleMessage(message)
        
    def handleMessage(self, message):      
        if message == 'sendState': # ask for send state from central, happens when a new sockets connected to server
            self.ecoBTApp.managerWorker.sendState()
        elif message == 'stopScan':
            print 'No client connected, stop scanning'
            self.ecoBTApp.managerWorker.stopScan()
        elif type(message) == unicode: # messages send from client are unicode
            print 'Got message from a client: ', message
            if message == 'start': # manager startScan signal
                self.ecoBTApp.managerWorker.startScan()  
                # self.ecoBTApp.managerWorker.sendState() 
            elif message == 'peripheralList':
                self.ecoBTApp.managerWorker.sendPeripheralList()
            elif message.startswith("startECG"):
                pNum = message[8:]
                print "Sending out Start Signal to Node: ", pNum
                self.ecoBTApp.managerWorker.startECG(int(pNum))           
