'''
Created on Feb 10, 2013

@author: cjhuo
'''
import json

import tornado.websocket

class EcoBTWebSocket(tornado.websocket.WebSocketHandler):
    def initialize(self, globalSockets, ecoBTApp):
        self.globalSockets = globalSockets    
        self.ecoBTApp = ecoBTApp               
        
    def open(self):
        self.globalSockets.append(self)
        self.ecoBTApp.managerWorker.sendState()
        print "WebSocket opened"

    def on_close(self):
        self.globalSockets.remove(self)
        print "WebSocket closed"
        
    def on_message(self, message):
        print message
        if message == 'peripheralList':
            self.ecoBTApp.managerWorker.sendPeripheralList()