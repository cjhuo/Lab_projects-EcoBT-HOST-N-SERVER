import tornado.web
from tornado import websocket

import threading
import time
import random
import json

from db.Models import DataSource, Device, DataLog

from datetime import datetime

from sqlalchemy.sql import desc

import ecg.ECG_reader

#fake the labels for each channels for demo purpose, 
#eventually label information should be passed from ecg module
ECG_CHANNELLABELS = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
GLOBALS = {
    'sockets': []
}     

class SensorPlot(tornado.web.UIModule):
    def render(self):
        pass

class PointHandler(tornado.web.RequestHandler):
    def initialize(self, ds):
        self.ds = ds
        
    def get(self):
        #self.db_test()
        val = db_insert(self.ds)
        self.write(val)

class SubmitHandler(tornado.web.RequestHandler):
    def post(self): 
        data = json.loads(self.get_argument("data"))
        print data
        
        #format of getBinInfo(): [[min, max, value],[min,max,value],...]
        bins = ecg.ECG_reader.getBinInfo(data['qPoint'][0], data['tPoint'][0]);
        
        print bins
        self.write({'data': bins}) #format of bins json: {'data': bins info}
        
class DSPHandler(tornado.web.RequestHandler):
    def get(self):        
        #val = self.fakeData()  #should be replaced by ecg dsp data generation module
        val = self.getDataFromDicomFile()
        self.write(val)
        
    def getDataFromDicomFile(self):
        wavech, peaks = ecg.ECG_reader.getTestData()
        
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
    def open(self):
        GLOBALS['sockets'].append(self)
        print "WebSocket opened"

    def on_close(self):
        GLOBALS['sockets'].remove(self)
        print "WebSocket closed"
        
class PeriodicExecutor(threading.Thread):
    def __init__(self,sleep,func,params):
        """ execute func(params) every 'sleep' seconds """
        self.func = func
        self.params = params
        self.sleep = sleep
        threading.Thread.__init__(self,name = "PeriodicExecutor")
        self.setDaemon(1)
    def run(self):
        while 1:
            time.sleep(self.sleep)
            self.func(self.params)
     
def db_insert(ds):
    session = ds.getSession()
    
    val = {'point': random.randint(-100, 130)}
    dataLog = DataLog('1', datetime.now(), val)
    session.add(dataLog)
    session.commit()
    dl = session.query(DataLog).filter(DataLog.dId == '1').order_by(desc(DataLog.timestamp)).first()
    val = dl.data
    session.close()
    print val
    return val      
        
def db_test(ds):
    if ds.hasEngine():
        print 'DB engine is on, data file for storage is %s' % ds.getDBPATH().split('sqlite:')[1].strip('/')
    session = ds.getSession()
    device = Device('test', 'testDecrip')
    session.add(device)
    session.commit()
    
    dataLog = DataLog(device.id, datetime.now(), 'testData')
    session.add(dataLog)
    session.commit()
    dl = session.query(DataLog).filter(DataLog.dId == device.id).order_by(desc(DataLog.timestamp)).one()
    print dl.timestamp, dl.data
    session.close()
        
def pushData(ds):
    if len(GLOBALS['sockets']) != 0:
        val = db_insert(ds)
        for socket in GLOBALS['sockets']:
            socket.write_message(val)

if __name__ == "__main__":
    DSPHandler().getDataFromDicomFile()
       
        
        
            