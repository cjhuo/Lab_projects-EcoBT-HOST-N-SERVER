from sqlalchemy.orm import relationship, backref, joinedload_all
from sqlalchemy import Column, BigInteger, Integer, Enum, String, Boolean, \
    DateTime, ForeignKey, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import hashlib
from DataSource import *
from misc.Singleton import Singleton

Base = declarative_base()


class DataSource(Singleton):    #to acchieve singleton of datasource
    
    def __init__(self, engine=None):
        if engine is None:
            #connect db
            self.engine = create_engine(DB_PATH, echo=False)
        else:
            self.engine = engine
        if self.engine is None:
            print 'engine is null'
        #create table if needed
        Base.metadata.create_all(self.engine)
        self.sessionMaker = scoped_session(sessionmaker(bind=self.engine, autoflush=False))

    def getSession(self):
        return self.sessionMaker()

    def getEngine(self):
            return self.engine
    
    def setEngine(self, engine):
        self.engine = engine
        
    def hasEngine(self):
        return self.engine != None
    def getDBPATH(self):
        return DB_PATH
    
    
#ORM Models
    
class Device(Base):
    __tablename__ = 'device'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        
class DataLog(Base):
    __tablename__ = 'datalog'
    id = Column(Integer, primary_key=True)
    dId = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    data = Column(PickleType, nullable=True)
    
    def __init__(self, dId, timestamp, data):
        self.dId = dId
        self.timestamp = timestamp
        self.data = data
       
            
            
from datetime import datetime            
#testcase    
if __name__ == '__main__':
    ds = DataSource()
    print ds.hasEngine()
    session = ds.getSession()
    device = Device('test', 'testDecrip')
    session.add(device)
    session.commit()
    
    dataLog = DataLog(device.id, datetime.now(), 'testData')
    session.add(dataLog)
    session.commit()
    dl = session.query(DataLog).filter(DataLog.dId == device.id).one()
    print dl.timestamp, dl.data