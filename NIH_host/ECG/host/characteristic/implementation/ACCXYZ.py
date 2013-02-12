'''
Created on Feb 9, 2013

@author: cjhuo
'''
import binascii
import struct

from Characteristic import *

class ACCXYZ(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0
        
    def process(self):
        value = self.instance._.value
        hex_str = binascii.hexlify(value)
        x, y, z = struct.unpack("<hhh", value) #only first 12bit is valid according to data sheet
        return self.processACC(x, y, z)
 
    def processACC(self, x, y, z):
        x = (0.0 + (x >> 4))  / 1000
        y = (0.0 + (y >> 4)) / 1000
        z = (0.0 + (z >> 4)) / 1000
        x = 1.0 if x>1.0 else x
        x = -1.0 if x<-1.0 else x
        y = 1.0 if y>1.0 else y
        y = -1.0 if y<-1.0 else y
        z = 1.0 if z>1.0 else z
        z = -1.0 if z<-1.0 else z         
        
        print "X: % .3fg Y: % .3fg Z: % .3fg" % (x, y, z)  
        '''
        x = math.atan2(x, math.sqrt(y*y+z*z))
        data = ('x', x)
        self.worker.getQueue().put(data)
        
        z = math.atan2(y, math.sqrt(x*x+z*z))
        data = ('z', z)
        self.worker.getQueue().put(data)

        if x<0 and z<0:
            x = -math.asin(x)-3.141592
        elif x>0 and z<0:
            x = 3.141592 - math.asin(x)
        else:   
            x = math.asin(x)
        data = {'type': 'orientation', 'axis': 'x', 'value': x}
        self.delegateWorker.getQueue().put(data)
        '''
        
        #x = math.asin(x)
        data = {'type': 'orientation', 
                'value': { 'x': x,
                           'y': y,
                           'z': z
                          },
                'uuid': self.UUID
                }
        #data = {'type': 'orientation', 'axis': 'x', 'value': x}
        return data
        #y = math.asin(y)
        #data = {'type': 'orientation', 'axis': 'y', 'value': y}
        #self.delegateWorker.getQueue().put(data)
        #z = math.acos(z)
        #data = {'type': 'orientation', 'axis': 'z', 'value': z}
        #self.delegateWorker.getQueue().put(data)