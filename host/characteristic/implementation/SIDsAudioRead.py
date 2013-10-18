'''
Created on Oct 17, 2013

@author: cjhuo
'''

import binascii

from Characteristic import *

class SIDsAudioRead(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0
        
    def process(self):
        hex_str = binascii.hexlify(self.instance._.value)

        print "SIDSAudioRead", hex_str
        
        # 4 sets of 4 bytes. In each set, 2 bytes(short) left first, 2bytes(short) right after
        # parser TBD!!!!!
        audioList = [] #length of 4, each item is list of length 2
        
        
        
        data = {
                'type': 'Audio',
                'value': audioList
                }
        
        self.peripheralWorker.delegateWorker.getQueue().put(data)
       