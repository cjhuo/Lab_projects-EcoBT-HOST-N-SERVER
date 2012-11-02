'''
Created on Nov 1, 2012

@author: cjhuo
'''
import threading
import time
        
class PeriodicExecutor(threading.Thread):
    def __init__(self,sleep,func, params=None):
        """ execute func(params) every 'sleep' seconds """
        self.func = func
        self.params = params
        self.sleep = sleep
        threading.Thread.__init__(self,name = "PeriodicExecutor")
        self.setDaemon(1)
    def run(self):
        while 1:
            time.sleep(self.sleep)
            if self.params is None:
                self.func()
            else:
                self.func(self.params)