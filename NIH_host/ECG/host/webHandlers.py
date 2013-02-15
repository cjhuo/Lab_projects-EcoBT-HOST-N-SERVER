'''
Created on Feb 15, 2013

@author: cjhuo
'''
import tornado.web

import json

class ECGHandler(tornado.web.RequestHandler):
    def initialize(self, ecoBTApp):
        self.ecoBTApp = ecoBTApp

    def post(self):
        address = json.loads(self.get_argument("address"))
        print address
        data = self.ecoBTApp.managerWorker.readECGData(address)
        self.write({'data': data})