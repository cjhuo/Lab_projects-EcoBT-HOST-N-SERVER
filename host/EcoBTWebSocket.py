'''
Created on Feb 10, 2013

@author: cjhuo
'''
from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *

import json
import csv
import os
import xlwt
from datetime import datetime
import tornado.websocket

class EcoBTWebSocket(tornado.websocket.WebSocketHandler):
    def initialize(self, globalSockets, ecoBTApp):
        self.globalSockets = globalSockets    
        self.ecoBTApp = ecoBTApp               
        
    def open(self):
        if len(self.globalSockets) <= 2: # allow only 3 socket to connect
            self.globalSockets.append(self)
            self.ecoBTApp.managerWorker.sendState()                
            print "WebSocket opened"
        else:
            self.close()

    def on_close(self):
        if self.globalSockets.contains(self):
            self.globalSockets.remove(self)
            print "WebSocket closed"
        '''
        if len(self.globalSockets) == 0: # time to ask host to stopScan
            self.handleMessage("stopScan")
        '''
        
        
    def on_message(self, message):
        try:
            #self.ecoBTApp.managerWorker.delegateWorker.getQueue().put(message)
            self.handleMessage(message)
        except Exception as e:
            print >>sys.stderr, e
            self.write_message({'from': 'central', 
                                'data': {'type': 'message',
                                         'value': 'error'}
                                })
        
    def handleMessage(self, message):           
        if message == 'stopScan':
            print 'No client connected, stop scanning'
            self.ecoBTApp.managerWorker.stopScan()
        elif type(message) == unicode: # messages send from client are unicode
            print 'Got message from a client: ', message
            if message == 'start': # manager startScan signal             
                self.ecoBTApp.managerWorker.startScan()
                if self.ecoBTApp.managerWorker.state == 1:
                    self.ecoBTApp.managerWorker.state = 2
                elif self.ecoBTApp.managerWorker.state == 4:
                    self.ecoBTApp.managerWorker.state = 3
                self.ecoBTApp.managerWorker.sendState()
                # self.ecoBTApp.managerWorker.sendState() 
            elif message == 'peripheralList':
                self.ecoBTApp.managerWorker.sendPeripheralList()
            elif message.startswith("SIDs_EnterPage"):
                address = message[14:]
                # stopScan
                self.ecoBTApp.managerWorker.stopScan() 
                self.ecoBTApp.managerWorker.state = 4
                #self.ecoBTApp.managerWorker.sendState()
                # cancel all other connection
                #self.ecoBTApp.managerWorker.cancelAllConnectionExcept(\
                #                self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).peripheral)
                # remove old uncombined logs
                
                path = os.path.join(os.path.dirname(__file__), os.pardir, "data")
                for file in os.listdir(path):
                    if file.endswith("left.csv") or file.endswith("right.csv"):
                        os.remove(os.path.join(path, file))
                
            elif message.startswith("startSIDs"):
                address = message[9:]
                self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).findSIDsStatus().startSIDs()
                
            elif message.startswith("stopSIDs"): 
                address = message[8:]
                self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).findSIDsStatus().stopSIDs()         
            elif message.startswith("sendSIDsSet"): 
                address = message[11:]
                self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).findSIDsSet().sendSettingsToFrontend()  
            elif message == "combineLog":
                path = os.path.join(os.path.dirname(__file__), os.pardir, "data")
                lFile = None
                rFile = None
                for file in os.listdir(path):
                    if file.endswith("left.csv"):
                        lFile = os.path.join(path, file)
                    elif file.endswith("right.csv"):
                        rFile = os.path.join(path, file)
                #combine logs
                wb = xlwt.Workbook()
                ws = wb.add_sheet("LEFT NODE")
                with open(lFile, 'r') as fd:
                    lReader = csv.reader(fd, delimiter=',')
                    for rowx, row in enumerate(lReader):
                        for colx, col in enumerate(row):
                            ws.write(rowx, colx, col)
                log_name = "FULL_" + datetime.now().strftime("%Y%m%d%H%M%S")
                wb.save(os.path.join(path, log_name))
                ws = wb.add_sheet("RIGHT NODE")
                with open(rFile, 'r') as fd:
                    rReader = csv.reader(fd, delimiter=',')         
                    for rowx, row in enumerate(rReader):
                        for colx, col in enumerate(row):
                            ws.write(rowx, colx, col)                
                
                wb.save(os.path.join(path, log_name))
                #remove separate logs
                os.remove(lFile)
                os.remove(rFile)
                '''                
                self.ecoBTApp.managerWorker.stopScan() 
                self.ecoBTApp.managerWorker.state = 4
                #self.ecoBTApp.managerWorker.sendState()
                # cancel all other connection
                self.ecoBTApp.managerWorker.cancelAllConnectionExcept(\
                                self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).peripheral)     
                '''       
            '''
            elif message.startswith("startTestECG"):
                address = message[12:]
                self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).findECGService().startTestECG()
                self.ecoBTApp.managerWorker.stopScan() 
                self.ecoBTApp.managerWorker.state = 4
                #self.ecoBTApp.managerWorker.sendState()
                # cancel all other connection
                self.ecoBTApp.managerWorker.cancelAllConnectionExcept(\
                                self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).peripheral)
            elif message.startswith("startECG"):
                address = message[8:]
                self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).findECGService().startECG()       
            elif message.startswith("stopECG"):
                address = message[7:]
                self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).findECGService().stopECG()         
            '''           
