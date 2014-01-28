'''
Created on Jan 26, 2014

@author: cjhuo
'''

import tornado.web, json, uuid, pprint

from config_central import *
from Gateway import Gateway
from Security import *
from Authentication import *
import pickle, struct, binascii

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
        #self.handleMessage(message)
        report = json.loads(message)
        
        print 'got message '
        pprint.pprint(report)
        if report['type'] == 'gatewayAuthenticationFeedback':
            if self.websockets[self].isAuthorized() == False: # check authorization first
                token = None
                try:
                    # assuming this is a message with type of gatewayAuthenticationFeedback
                    token = report['value']['authorizationToken']
                except: # un-authorized
                    print 'un-authorized gateway, closing connection...'
                    self.close()
                    del self.websockets[self]
                    return
                
                if token == GATEWAY_AUTHENTICATION_TOKEN:
                    self.websockets[self].setAuthorized(True)
                    if 'gatewayUUID' in (report['value']).keys() and report['value']['gatewayUUID'] != None:
                        self.websockets[self].setUUID = report['value']['gatewayUUID']
                    else:
                        # assign an id to this gateway, and send to gateway
                        self.websockets[self].setUUID = uuid.uuid4().int
                        self.write_message(json.dumps({
                                            'type': 'gatewayUUID',
                                            'value': self.websockets[self].setUUID
                                            }))
                    print 'gateway', self.websockets[self].setUUID, ' is authorized'
                else:
                    print 'un-authorized gateway, closing connection...'
                    self.close()
                    del self.websockets[self]
                    return
            else: 
                pass # already authorized, ignore
        elif report['type'] == 'snapshot':
            for peripheralInfo in report['value']['connected_peripherals']:
                if peripheralInfo['id'] != None:
                    if peripheralInfo['isSecured'] == False:
                        if SECURITY_SERVICE in peripheralInfo['profileHierarchy'].iterkeys():
                            # ask what security approach it is
                            self.write_message(json.dumps({
                                                'type': 'peripheralSecurityTypeCheck',
                                                'value': {
                                                          'peripheralID': peripheralInfo['id'],
                                                          'securityService': SECURITY_SERVICE,
                                                          'securityTypeCharacteristic': SECURITY_TYPE_CHARACTERISTIC
                                                          }
                                                }))
                    if peripheralInfo['isAuthorized'] == False:
                        if AUTHENTICATION_SERVICE in peripheralInfo['profileHierarchy'].iterkeys():
                            # provide authentication checking instance
                            authenticationHandlerObj = pickle.dumps(Authentication())
                            self.write_message(json.dumps({
                                                'type': 'peripheralAuthenticationHandlerObj',
                                                'value': {
                                                          'peripheralID': peripheralInfo['id'],
                                                          'authenticationHandlerObj': authenticationHandlerObj
                                                          }
                                                }))
                    # test
                    if peripheralInfo['isSecured'] and peripheralInfo['isAuthorized']:
                        self.write_message(json.dumps({
                                            'type': 'peripheralQuery',
                                            'value': {
                                                      'queryID': uuid.uuid4().int,
                                                      'peripheralID': peripheralInfo['id'],
                                                      'action': 'Read',
                                                      'serviceUUID': '7780',
                                                      'characteristicUUID': '7781'
                                                      }
                                            })) 
                            
        elif report['type'] == 'peripheralSecurityTypeCheck':
            securityHandlerObj = pickle.dumps(SecurityHandlerFactory(report['value']['securityType']))
            self.write_message(json.dumps({
                                           'type': 'peripheralSecurityHandlerObj',
                                           'value': {
                                                     'peripheralID': report['value']['peripheralID'],
                                                     'securityHandlerObj': securityHandlerObj
                                                     }
                                           }))
        elif report['type'] == 'peripheralQueryFeedback':
            #import binascii
            #print 'value is ', binascii.unhexlify(report['value']['rtValue']) 
            
            #test
            print 'value is ', struct.unpack("@i",binascii.unhexlify(report['value']['rtValue']))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Not a valid entry")