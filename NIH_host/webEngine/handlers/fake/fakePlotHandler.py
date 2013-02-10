import tornado.web
from tornado import websocket

import random
import json

from fakeDataGenerator import FakeDataGenerator
from fakePush import FakePush

#import ecg.ECG_reader


class SensorPlot(tornado.web.UIModule):
    def render(self):
        pass

class PointHandler(tornado.web.RequestHandler):
    def initialize(self, ds):
        self.ds = ds
        
    def get(self):
        #self.db_test()
        val = FakeDataGenerator(self.ds).db_insert()
        self.write(val)

        
class ClientSocket(websocket.WebSocketHandler):
    def initialize(self, ds):
        self.ds = ds
        
    def open(self):
        FakePush(self.ds).getGlobalSockets().append(self)
        print "WebSocket opened"

    def on_close(self):
        FakePush(self.ds).getGlobalSockets().remove(self)
        print "WebSocket closed"


        
        
            