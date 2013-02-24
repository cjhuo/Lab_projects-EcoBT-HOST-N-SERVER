'''
Created on Nov 1, 2012

@author: cjhuo
'''
import random
from datetime import datetime
from sqlalchemy.sql import desc
from db.Models import DataSource, Device, DataLog

class FakeDataGenerator():
    
    def __init__(self, ds):
        self.ds = ds     
    
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
