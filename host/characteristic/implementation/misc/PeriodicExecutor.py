'''
Created on Nov 1, 2012

@author: cjhuo
'''
from Foundation import *
import threading
from threading import Event
import time
        
class PeriodicExecutor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self,name = "ECGPeriodicExecutor")
        self.setFlag = Event()
        
    def setParams(self,sleep,func, param1=None, param2=None):
        """ execute func(params) every 'sleep' seconds """
        self.func = func
        self.param1 = param1
        self.param2 = param2
        self.sleep = sleep
        
        self.setDaemon(1)
    def run(self):
        while not self.setFlag.isSet():       
            if self.param2 == None:
                self.func(self.param1)
            else:
                self.func(self.param1, self.param2)
            time.sleep(self.sleep)
        NSLog('EXITING PERIODIC EXECUTOR FROM CHARATERISTIC %@',  self.param1.UUID)