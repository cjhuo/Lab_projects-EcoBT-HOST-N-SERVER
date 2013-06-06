'''
Created on Feb 9, 2013

@author: cjhuo
'''
from IOBluetooth import *

# dynamically load modules from implementation package
import os
for module in os.listdir(os.path.join(os.path.dirname(__file__), "implementation")):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    exec("from implementation import %s" % module[:-3])
del module

def createCharacteristic(UUID, instance, service, peripheralWorker):
    c = None
    if UUID in ProfileDict.keys():
        objStr = ProfileDict[UUID] + '.' + ProfileDict[UUID] + '()'
        c = eval(objStr)
    else: # found a profile that has not implemented
        c = Characteristic.Characteristic()
    c.setUUIDInstanceServicePeripheralWorker(UUID, instance, service, peripheralWorker)
    c.setRole() # identify itself if it is a setter or getter of the service

    return c    
    
    