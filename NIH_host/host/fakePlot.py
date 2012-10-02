import tornado.web
import random

from db.Models import DataSource, Device, DataLog

from datetime import datetime

from sqlalchemy.sql import desc

from ecg.ECG_reader import *


class SensorPlot(tornado.web.UIModule):
    def render(self):
        pass

class PointHandler(tornado.web.RequestHandler):
    def initialize(self, ds):
        self.ds = ds
        
    def get(self):
        #self.db_test()
        val = self.db_insert()
        self.write(val)


    def db_insert(self):
        session = self.ds.getSession()
        
        val = {'point': random.randint(-100, 130)}
        dataLog = DataLog('1', datetime.now(), val)
        session.add(dataLog)
        session.commit()
        dl = session.query(DataLog).filter(DataLog.dId == '1').order_by(desc(DataLog.timestamp)).first()
        val = dl.data
        session.close()
        print val
        return val
        
        
        
    def db_test(self):
        if self.ds.hasEngine():
            print 'DB engine is on, data file for storage is %s' % self.ds.getDBPATH().split('sqlite:')[1].strip('/')
        session = self.ds.getSession()
        device = Device('test', 'testDecrip')
        session.add(device)
        session.commit()
        
        dataLog = DataLog(device.id, datetime.now(), 'testData')
        session.add(dataLog)
        session.commit()
        dl = session.query(DataLog).filter(DataLog.dId == device.id).order_by(desc(DataLog.timestamp)).one()
        print dl.timestamp, dl.data
        session.close()
        
class SubmitHandler(tornado.web.RequestHandler):
    def post(self): 
        data = self.get_argument("data")
        print data
        #self.write({'test': 'test'})
        
class DSPHandler(tornado.web.RequestHandler):
    def get(self):        
        datasets = self.fakeData(2)#should be replaced by ecg dsp data generation module
        print datasets
        val = {'dspData': datasets}
        self.write(val)
           
    ''' 
    generate data for n channels with 100 data each, ranged from (-100, 100)
    The datasets dict should have the structure as below:
    datasets = {
                    "channel1": {
                        label: "channel",
                        data: [array of [x, y]]
                    },
                    "channel2": {
                        label: "channel2",
                        data: [array of [x, y]]
                    }
                }
    '''
    def fakeData(self, n):
        return getTestData()
        '''
        datasets = dict()
        for i in range(n):
            data = [[j, random.randint(-100, 100)] for j in range(100)]            
            label = "channel " + str(i)
            datasets[label] = dict()
            datasets[label]['data'] = data 
            datasets[label]['label'] = label
        return datasets
        '''

        
        
        
        
        
            