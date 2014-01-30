'''
Created on Jan 26, 2014

@author: cjhuo
'''

import tornado.web, json, uuid, pprint

from config_central import *
from Gateway import Gateway
from Security import *
from Authentication import *
import os, pickle, struct, binascii, random

class KWDict(object):
    def __init__(self):
        self.kwfile = os.path.dirname(__file__)+'/KWDICT'
        if not os.path.exists(self.kwfile):
            pf = open(self.kwfile, 'wb', 0)
            self.kwdict = {}
            pickle.dump(self.kwdict, pf)
            self.pf.close()
        else:
            pf = open(self.kwfile, 'rb', 0)
            self.kwdict = pickle.load(pf)
            pf.close()        
    
    def findTokenByID(self, id):
        if id in self.kwdict.iterkeys():
            print 'find token ', self.kwdict[id]
            return self.kwdict[id]
        return None
    
    def generateTokenForID(self, id):
        token = random.getrandbits(64)
        self.kwdict[id] = token
        print 'token generated', token
        pf = open(self.kwfile, 'wb', 0)
        pickle.dump(self.kwdict, pf)
        pf.close()
        return token

class CentralServerApp(tornado.web.Application):
    def __init__(self):
        '''''''''''''''''''''''''''''''''''''''''''''
        This sockets dict stores every gateway session
        dict key: websocket instance of gateway
        dict value: Gateway Object instance
        '''''''''''''''''''''''''''''''''''''''''''''       
        self.websockets = {}
        self.kwdict = KWDict()
        self.query_queue = {}
         
        
        self.handlers = [
                (r"/", MainHandler),
                (r"/socket", GWWebsocket, dict(websockets = self.websockets, kwdict=self.kwdict, query_queue=self.query_queue)),
                (r"/check", checkHandler, dict(websockets = self.websockets)),
                (r"/query", queryHandler, dict(websockets = self.websockets, query_queue=self.query_queue)),
                ]

        settings = dict(
                        debug=True,
                        cookie_secret="BlaBlaBlaBlaBlaBlaBlaBlaBlaBlaBlaBlaBla",       
                        )
        
        tornado.web.Application.__init__(self, self.handlers, **settings)
        
        
class queryHandler(tornado.web.RequestHandler):
    def initialize(self, websockets, query_queue):
        self.websockets = websockets
        self.query_queue = query_queue

    @tornado.web.asynchronous
    def get(self):
        qtype = self.get_argument('query_type')
        gw_id = int(self.get_argument('gateway_id'))
        prl_id = int(self.get_argument('peripheral_id'))
        srv_id = str(self.get_argument('service_id'))
        chr_id = str(self.get_argument('characteristic_id'))
        message = self.get_argument('message', None)
        gw_found = False
        prl_found = False
        srv_found = False
        chr_found = False
        try:
            for websocket, gateway in self.websockets.iteritems():
                if gateway.getUUID() == gw_id:
                    gw_found = True
                    for peripheral in gateway.peripherals:
                        if peripheral['id'] == prl_id:
                            prl_found = True
                            for service in peripheral['profileHierarchy'].iterkeys():
                                if service == srv_id:
                                    srv_found = True
                                    if service == SECURITY_SERVICE:
                                        self.write("cannot operate on security service")
                                        self.finish()
                                        return                                    
                                    if service == AUTHENTICATION_SERVICE:
                                        self.write("cannot operate on authentication service")
                                        self.finish()
                                        return                                    
                                    if service == GAP_SERVICE:
                                        self.write("cannot operate on GAP service")
                                        self.finish()
                                        return                                    
                                    if service == GATT_SERVICE:
                                        self.write("cannot operate on GATT service")
                                        self.finish()
                                        return                                    
                                    for char in peripheral['profileHierarchy'][srv_id].iterkeys():
                                        if char == chr_id:
                                            chr_found = True
                                            if qtype == 'Read':
                                                query_id = random.getrandbits(64)
                                                print 'new query', query_id
                                                websocket.write_message(json.dumps({
                                                                    'type': 'peripheralQuery',
                                                                    'value': {
                                                                              'queryID': query_id,
                                                                              'peripheralID': prl_id,
                                                                              'action': qtype,
                                                                              'serviceUUID': srv_id,
                                                                              'characteristicUUID': chr_id
                                                                              }
                                                                    }))          
                                            if qtype == 'Write':
                                                query_id = random.getrandbits(64)
                                                print 'new query', query_id
                                                websocket.write_message(json.dumps({
                                                                    'type': 'peripheralQuery',
                                                                    'value': {
                                                                              'queryID': query_id,
                                                                              'peripheralID': prl_id,
                                                                              'action': qtype,
                                                                              'serviceUUID': srv_id,
                                                                              'characteristicUUID': chr_id,
                                                                              'message': message
                                                                              }
                                                                    }))          
                                            self.query_queue[query_id] = self                                            
            if not gw_found:
                self.write("gateway not found")
                self.finish()
            if not prl_found:
                self.write("peripheral not found")
                self.finish()                               
            if not srv_found:
                self.write("service not found")
                self.finish()  
            if not chr_found:
                self.write("characteristic not found")
                self.finish()  
        except Exception as e:
            print "Error on peripheral query format:", e
        
class checkHandler(tornado.web.RequestHandler):
    def initialize(self, websockets):
        self.websockets = websockets
        
    def get(self):
        overview_map = {'gateways': []}
        for websocket, gateway in self.websockets.iteritems():
            overview_map['gateways'].append({
                                            'gateway_id': gateway.getUUID(),
                                            'peripherals': gateway.peripherals
                                            })
        self.write(json.dumps(overview_map))

"""
for checking whether the websocket connect is still alive
"""
from threading import Thread, Event
import time
class PeriodicPinger(Thread):
    def __init__(self, websocket):
        Thread.__init__(self,name = "PeriodicPinger")
        self.websocket = websocket
        self.flag = Event()
        
    def run(self):
        while not self.flag.isSet():
            print 'sending ping to websocket', self.websocket
            self.websocket.ping("ping")
            time.sleep(5)
    
    def stop(self):
        self.flag.set()
        
        
import tornado.websocket
class GWWebsocket(tornado.websocket.WebSocketHandler):
    def initialize(self, websockets, kwdict, query_queue):
        self.websockets = websockets    
        self.kwdict = kwdict
        self.query_queue = query_queue
        
    def open(self):
        # initialize gateway websocket
        self.websockets[self] = Gateway()
        self.websockets[self].setPeriodicPinger(PeriodicPinger(self))
        self.websockets[self].getPeriodicPinger().start()
        
        print 'Number of Connected Gateway ', len(self.websockets)

        print "WebSocket opened"
        
        # Check authentication by sending gateway token request
        self.write_message(json.dumps({
                                       'type': 'gatewayAuthentication'                                       
                                       }))

    def on_close(self):
        if self in self.websockets.keys():
            self.websockets[self].getPeriodicPinger().stop()
            del self.websockets[self]
            print "WebSocket closed"
        print 'Number of Connected Gateway ', len(self.websockets)
        
        
    def on_message(self, message):
        #self.handleMessage(message)
        report = json.loads(message)
        
        #print 'got message '
        #pprint.pprint(report)
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
                        self.websockets[self].setUUID(report['value']['gatewayUUID'])
                    else:
                        # assign an id to this gateway, and send to gateway
                        #self.websockets[self].setUUID(uuid.uuid4().int)
                        self.websockets[self].setUUID(random.getrandbits(16))
                        self.write_message(json.dumps({
                                            'type': 'gatewayUUID',
                                            'value': self.websockets[self].getUUID()
                                            }))
                    print 'gateway', self.websockets[self].getUUID(), ' is authorized'
                else:
                    print 'un-authorized gateway, closing connection...'
                    self.close()
                    del self.websockets[self]
                    return
            else: 
                pass # already authorized, ignore
        elif report['type'] == 'snapshot':
            self.websockets[self].peripherals = report['value']['connected_peripherals']
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
                            fp = open(os.path.join(os.path.dirname(__file__), 'Authentication.py'), 'r')
                            authenticationHandlerCls = fp.read()
                            #authenticationHandlerObj = pickle.dumps(Authentication())
                            self.write_message(json.dumps({
                                                'type': 'peripheralAuthenticationHandlerCls',
                                                'value': {
                                                          'peripheralID': peripheralInfo['id'],
                                                          'authenticationHandlerCls': authenticationHandlerCls
                                                          }
                                                }))
                            fp.close()
                    '''
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
                    '''
                            
        elif report['type'] == 'peripheralSecurityTypeCheck':
            fp = open(os.path.join(os.path.dirname(__file__), 'Security.py'), 'r')
            securityHandlerCls = fp.read()
            #securityHandlerObj = pickle.dumps(SecurityHandlerFactory(report['value']['securityType']))
            self.write_message(json.dumps({
                                           'type': 'peripheralSecurityHandlerCls',
                                           'value': {
                                                     'securityType': report['value']['securityType'],
                                                     'peripheralID': report['value']['peripheralID'],
                                                     'securityHandlerCls': securityHandlerCls
                                                     }
                                           }))
            fp.close()
        elif report['type'] == 'peripheralAuthenticationTokenQuery':        
        # check if the peripheral's token is stored in central's knowledge base
        # else generate one and store it
            token = self.kwdict.findTokenByID(report['value']['peripheralID'])
            if token == None:
                token = self.kwdict.generateTokenForID(report['value']['peripheralID'])

            self.write_message(json.dumps({
                                           'type': 'peripheralAuthenticationTokenResponse',
                                           'value': {
                                                     'peripheralID': report['value']['peripheralID'],
                                                     'authenticationToken': token
                                                     }
                                           }))                
        elif report['type'] == 'peripheralQueryFeedback':
            #import binascii
            #print 'value is ', binascii.unhexlify(report['value']['rtValue']) 
            
            #test
            #print 'value is ', (struct.unpack("@i",binascii.unhexlify(report['value']['rtValue'])))[0]
            
            query_id = report['value']['queryID']
            print 'query feedback', query_id, 'result', report['value']['rtValue']
            if query_id in self.query_queue.iterkeys():
                self.query_queue[query_id].write(json.dumps({'query_id': query_id,
                                                             'result': report['value']['rtValue']
                                                             }))
                self.query_queue[query_id].finish()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Not a valid entry")