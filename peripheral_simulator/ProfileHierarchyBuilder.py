'''
Created on Jan 24, 2014

@author: cjhuo
'''

from config_peripheral import ProfileDict
from Service import Service

# dynamically load modules from implementation package
import os
for module in os.listdir(os.path.join(os.path.dirname(__file__), "characteristics")):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    exec("from characteristics import %s" % module[:-3])
del module

def createHierarchy(peripheralWorker):
    for serviceUUID, charUUIDs in ProfileDict.iteritems():
        charList = []
        if len(charUUIDs) != 0:
            for charUUID, objStr in charUUIDs.iteritems():
                char = eval(objStr+'.'+objStr+'("'+ charUUID +'")')
                charList.append(char)
        service = Service(serviceUUID, True, charList)
        peripheralWorker.manager.addService_(service.instance)
        peripheralWorker.services.append(service)
