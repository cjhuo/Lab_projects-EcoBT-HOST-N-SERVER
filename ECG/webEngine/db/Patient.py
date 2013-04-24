'''
Created on Jan 13, 2013

@author: cjhuo

insert breathing sound wave file as blob into db
'''

from Models import *
import sys

        
#testcase    
if __name__ == '__main__':
    ds = DataSource()
    session = ds.getSession()
    p = Patient()
    session.add(p)
    session.commit()
    
    r = Record('testRecord', p.id)
    session.add(r)
    session.commit()
    
    print p.records