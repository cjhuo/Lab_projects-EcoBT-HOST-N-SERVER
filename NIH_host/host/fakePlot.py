import tornado.web
from tornado import websocket

import random
import json

from fakeDataGenerator import FakeDataGenerator
from fakePush import FakePush

import ecg.ECG_reader


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

class SubmitHandler(tornado.web.RequestHandler):
    def post(self): 
        data = json.loads(self.get_argument("data"))
        print data
        
        #format of getBinInfo(): [[min, max, value],[min,max,value],...]
        bins = ecg.ECG_reader.getBinInfo(data['qPoint'][0], data['tPoint'][0]);
        
        print bins
        self.write({'data': bins}) #format of bins json: {'data': bins info}
        
        
#fake the labels for each channels for demo purpose, 
#eventually label information should be passed from ecg module
ECG_CHANNELLABELS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']

class DSPHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.ecg = ecg.ECG_reader.ECG_reader()
        
    def get(self):        
        #val = self.fakeData()  #should be replaced by ecg dsp data generation module
        val = self.getDataFromDicomFile()
        self.write(val)
        
    def post(self): 
        data = json.loads(self.get_argument("data"))
        print data
        
        #format of getBinInfo(): [[min, max, value],[min,max,value],...]
        bins = self.ecg.getBinInfo(data['qPoint'][0], data['tPoint'][0]);
        
        print bins
        self.write({'data': bins}) #format of bins json: {'data': bins info}
        
    def getDataFromDicomFile(self):
        #wavech, peaks = ecg.ECG_reader.getTestData()
        wavech, peaks = self.ecg.getTestData()
        
        #create dataset dict to be sent to web server and fill in data
        datasets = []
        for i in range(len(wavech)):
            data = [wavech[i][j] for j in range(len(wavech[i]))]
            label = ECG_CHANNELLABELS[i]            
            #label = "channel " + str(i)
            datasets.append(dict())
            datasets[i]['data'] = data 
            datasets[i]['label'] = label
            
        #add peak information to structure to be sent to frontend
        # format of peaks: "peaks": [index of 1st peak, index of 2nd peak, ...]

        val = {'dspData': datasets, 'peaks': peaks}
        #print val
        return val
   
           
    ''' 
    generate data for n channels with 100 data each, ranged from (-100, 100)
    The datasets dict should have the structure as below:
    datasets = [
                    {
                        label: "channel",
                        #data: [array of [x, y]]
                        data: [array of y]
                    },
                    {
                        label: "channel2",
                        #data: [array of [x, y]]
                        data: [array of y]
                    },
                ]
    '''
    def fakeData(self, n=2):
        datasets = dict()
        for i in range(n):
            #data = [[j, random.randint(-100, 100)] for j in range(100)]  
            data = [random.randint(-100, 100) for j in range(100)]           
            #label = "channel " + str(i)
            label = ECG_CHANNELLABELS[i]
            print label
            datasets[label] = dict()
            datasets[label]['data'] = data 
            datasets[label]['label'] = label
        return (datasets,[])
        
        
class ClientSocket(websocket.WebSocketHandler):
    def initialize(self, ds):
        self.ds = ds
        
    def open(self):
        FakePush(self.ds).getGlobalSockets().append(self)
        print "WebSocket opened"

    def on_close(self):
        FakePush(self.ds).getGlobalSockets().remove(self)
        print "WebSocket closed"

if __name__ == "__main__":
    DSPHandler().getDataFromDicomFile()
       
        
        
            