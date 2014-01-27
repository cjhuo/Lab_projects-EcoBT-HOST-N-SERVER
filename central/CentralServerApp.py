'''
Created on Jan 26, 2014

@author: cjhuo
'''

import tornado.web, json, uuid

from config_central import *
from Gateway import Gateway

class CentralServerApp(tornado.web.Application):
    def __init__(self):
        '''''''''''''''''''''''''''''''''''''''''''''
        This sockets dict stores every gateway session
        dict key: websocket instance of gateway
        dict value: Gateway Object instance
        '''''''''''''''''''''''''''''''''''''''''''''       
        self.websockets = {}
        
        self.handlers = [
                (r"/", MainHandler),
                (r"/socket", GWWebsocket, dict(websockets = self.websockets)),
                ]

        settings = dict(
                        debug=True,
                        cookie_secret="BlaBlaBlaBlaBlaBlaBlaBlaBlaBlaBlaBlaBla",       
                        )
        
        tornado.web.Application.__init__(self, self.handlers, **settings)

import tornado.websocket

class GWWebsocket(tornado.websocket.WebSocketHandler):
    def initialize(self, websockets):
        self.websockets = websockets    
        
    def open(self):
        # initialize gateway websocket
        self.websockets[self] = Gateway()
        
        print 'Number of Connected Gateway ', len(self.websockets)

        print "WebSocket opened"
        
        # Check authentication by sending gateway token request
        self.write_message(json.dumps({
                                       'type': 'gatewayAuthentication'                                       
                                       }))

    def on_close(self):
        if self in self.websockets.keys():
            del self.websockets[self]
            print "WebSocket closed"
        print 'Number of Connected Gateway ', len(self.websockets)
        
        
    def on_message(self, message):
        print 'got message ', message
        #self.handleMessage(message)
        report = json.loads(message)
        if self.websockets[self].isAuthorized() == False: # check authorization first
            token = None
            try:
                token = report['authorizationToken']
            except: # un-authorized
                print 'un-authorized gateway, closing connection...'
                self.close()
                del self.websockets[self]
                return
            
            if token == GATEWAY_AUTHENTICATION_TOKEN:
                self.websockets[self].setAuthorized(True)
                # assign an id to this gateway, and send to gateway
                self.websockets[self].setUUID = uuid.uuid4().int
                self.write_message({
                                    'type': 'gatewayUUID',
                                    'value': self.websockets[self].setUUID
                                    })
                print 'gateway', self.websockets[self].setUUID, ' is authorized'
            else:
                print 'un-authorized gateway, closing connection...'
                self.close()
                del self.websockets[self]
                return
        else:
            pass


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Not a valid entry")