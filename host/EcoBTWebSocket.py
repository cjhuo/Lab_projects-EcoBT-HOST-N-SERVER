'''
Created on Feb 10, 2013

@author: cjhuo
'''
from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *
from EmailSender import EmailSender
import json

from datetime import datetime

import tornado.websocket


class EcoBTWebSocket(tornado.websocket.WebSocketHandler):

    def initialize(self, globalSockets, ecoBTApp):
        self.globalSockets = globalSockets
        self.ecoBTApp = ecoBTApp

    def open(self):
        if len(self.globalSockets) < 20:  # allow only 1 socket to connect
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
            # self.ecoBTApp.managerWorker.delegateWorker.getQueue().put(message)
            self.handleMessage(message)
        except:
            self.write_message({'from': 'central',
                                'data': {'type': 'message',
                                         'value': 'error'}
                                })

    def handleMessage(self, message):
        if message == 'stopScan':
            print 'No client connected, stop scanning'
            self.ecoBTApp.managerWorker.stopScan()
        elif type(message) == unicode:  # messages send from client are unicode
            print 'Got message from a client: ', message
            if message == 'start':  # manager startScan signal
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
                # self.ecoBTApp.managerWorker.sendState()
                # cancel all other connection
                self.ecoBTApp.managerWorker.cancelAllConnectionExcept(
                    self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).peripheral)
            elif message.startswith("sendSIDsState"):
                address = message[len("sendSIDsState"):]
                sids = self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address)
                sids.findSIDsStatus().sendState()

#            elif message.startswith("SIDsloadByFile"):
#                address = message[len("SIDsloadByFile"):]
#                sids = self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address)
#                sids.findSIDsSet().loadFile(address)
#                sids.findSIDsRead().loadFile(address)

            elif message.startswith("startSIDs"):
                address = message[9:]
                sids = self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address)
                timestamp = datetime.now()
                sids.findSIDsSet().loadFile(address)
                sids.findSIDsRead().loadFile(address)
                # prepare log files
                sids.findSIDsStatus().createLogFile(timestamp)
                sids.findACCControl().createLogFile(timestamp)
                sids.findBodyTempControl().createLogFile(timestamp)
                # start sensors
                sids.findSIDsStatus().startSIDs()
                sids.findACCControl().startACC()
                sids.findBodyTempControl().startBodyTemp()
                sids.findAudioControl().startAudioRead()

            elif message.startswith("stopSIDs"):
                address = message[8:]
                sids = self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address)
                # close log files
                sids.findSIDsStatus().closeLogFile()
                sids.findACCControl().closeLogFile()
                sids.findBodyTempControl().closeLogFile()
                # stop sensors
                sids.findACCControl().stopACC()
                sids.findBodyTempControl().stopBodyTemp()
                sids.findAudioControl().stopAudioRead()
                sids.findSIDsStatus().stopSIDs()

            elif message.startswith("sendSIDsSet"):
                address = message[11:]
                sids = self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).findSIDsSet()
                sids.loadFile(address)
                sids.sendSettingsToFrontend()
            elif message.startswith("sendCO2Formula"):
                address = message[len("sendCO2Formula"):]
                sids = self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).findSIDsRead()
                sids.loadFile(address)
                sids.sendParamsToFrontend()
            elif message.startswith("disconnectSIDs"):
                address = message[len("disconnectSIDs"):]
                sids = self.ecoBTApp.managerWorker.findPeripheralWorkerByAddress(address).stop()
            else:  # json
                data = json.loads(message)
                emailContent = "This is an alert sent from SIDs monitor\
                                notifying you some of the body conditions\
                                of the baby went wrong. NECCESSARY ACTIONS\
                                NEED TO BE TAKEN! \n\nThe following are\
                                current status of the baby: \n\
                                Current body temperature: " + data['temp']\
                    + "\nCurrent CO2 density: " + data['hum'] \
                    + "\n(Normal Body temperature Ranage: " \
                    + data['tempRangeMin'] + '~' + data['tempRangeMax'] + ", " +\
                    "Normal CO2 density: " + data['humRangeMin'] + '~' + data['humRangeMax'] + ")"
                EmailSender().send_email(emailContent, data['email'])

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
