'''
Created on Feb 10, 2013

@author: cjhuo
'''

import tornado.websocket

class EcoBTWebSocket(tornado.websocket.WebSocketHandler):
    def initialize(self, globalSockets):
        self.globalSockets = globalSockets                   
        
    def open(self):
        self.globalSockets.append(self)
        print "WebSocket opened"

    def on_close(self):
        self.globalSockets.remove(self)
        print "WebSocket closed"
        
    def on_message(self, message):
        pass