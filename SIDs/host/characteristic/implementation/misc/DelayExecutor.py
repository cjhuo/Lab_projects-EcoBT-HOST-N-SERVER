'''
Created on Feb 15, 2013

@author: cjhuo
'''
import threading
import time

# only can functions with 2 argument...
class DelayExecutor(threading.Thread):
    def __init__(self,sleep,func, param1, param2, param3):
        """ execute func(params) after 'sleep' seconds """
        self.func = func
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3
        self.sleep = sleep
        threading.Thread.__init__(self,name = "DelayExecutor")
        self.setDaemon(1)
    def run(self):
        time.sleep(self.sleep)
        self.func(self.param1, self.param3)
        self.func(self.param2, self.param3)