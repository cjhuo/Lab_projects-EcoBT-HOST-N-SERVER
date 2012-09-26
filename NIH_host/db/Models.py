from sqlalchemy.orm import relationship, backref, joinedload_all
from sqlalchemy import Column, BigInteger, Integer, Enum, String, Boolean, \
    DateTime, ForeignKey, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import hashlib
from DataSource import *

Base = declarative_base()


class DataSource():
    #to acchieve singleton of datasource
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DataSource, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance
    
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
    
    
#ORM Models
    
class Device(Base):
    __tablename__ = 'device'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        
class DataLog(Base):
    __tablename__ = 'datalog'
    id = Column(BigInteger, primary_key=True)
    dId = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    data = Column(PickleType, nullable=True)
    
    def __init__(self, dId, timestamp, data):
        self.dId = dId
        self.timestamp = timestamp
        self.data = data
       
            
            
#testcase    
if __name__ == '__main__':
    DataSource()