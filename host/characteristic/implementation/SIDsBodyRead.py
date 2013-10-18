'''
Created on Oct 17, 2013

@author: cjhuo
'''

import binascii

from Characteristic import *

class SIDsBodyRead(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0
        
    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)
        print "SIDsBodyRead", hex_str
        
        # 2 bytes(signed short)
        # parser TBD!!!!!!!
        tempC = None
        
        
        
        # send to frontend
        data = {
                'type': 'BodyTemp',
                'value': tempC
                }
        
        self.peripheralWorker.delegateWorker.getQueue().put(data)
 
  