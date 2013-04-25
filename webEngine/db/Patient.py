'''
Created on Jan 13, 2013

@author: cjhuo

insert breathing sound wave file as blob into db
'''

from Models import *
import sys

class PatientController():
    def __init__(self):
        self.ds = DataSource()
        if self.ds.hasEngine():
            self.session = self.ds.getSession()
        else: 
            print "no db engine connected"
            sys.exit(1)
        
    def __enter__(self):
        return self
        
    def insert(self, name=None, gender=None, age=None, id=None):
        patient = Patient(name, gender, age, id)
        self.session.add(patient)
        self.session.commit()
        return patient.id # return id of newly created patient
    
    '''
    return type: a Patient object with given id
    '''
    def findByID(self, id):
        return self.session.query(Patient).filter(Patient.id == id).one()
    
    '''
    return type: list of Patient object
    '''
    def findAllByName(self, name):
        return self.session.query(Patient).filter(Patient.name == name).all()
    
        
    def __exit__(self, type, value, traceback):
        #conn = self.session.connection()
        #self.session.remove()
        #conn.close()
        self.session.close()
        
from uuid import uuid4
#testcase    
if __name__ == '__main__':
    pc = PatientController()
    pId = pc.insert(id=uuid4().int)
    
    print pId
    
    print pc.findByID(pId).id
    
    for p in pc.findAllByName(None):
        print p.id
    '''
    ds = DataSource()
    session = ds.getSession()
    p = Patient()
    session.add(p)
    session.commit()
    
    
    r = Record('testRecord', p.id)
    session.add(r)
    session.commit()
    
    print p.records
    '''