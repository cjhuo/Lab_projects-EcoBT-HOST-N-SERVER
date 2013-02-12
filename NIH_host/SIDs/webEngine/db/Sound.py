'''
Created on Jan 13, 2013

@author: cjhuo

insert breathing sound wave file as blob into db
'''

from Models import *
import sys

class Sound():
    def __init__(self):
        self.ds = DataSource()
        if self.ds.hasEngine():
            self.session = self.ds.getSession()
        else: 
            print "no db engine connected"
            sys.exit(1)
        
    def __enter__(self):
        return self
        
    def insert(self, id, timestamp, data):
        soundLog = SoundLog(id, timestamp, data)
        self.session.add(soundLog)
        self.session.commit()
        return self
    
        
    def __exit__(self, type, value, traceback):
        conn = self.session.connection()
        self.session.remove()
        conn.close()
        
#testcase    
if __name__ == '__main__':
    from datetime import datetime
    with Sound() as sound:
        sound.insert(1, datetime.now(), '12345')