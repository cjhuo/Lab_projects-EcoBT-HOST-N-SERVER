'''
Created on Oct 17, 2013

@author: cjhuo
'''
from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *

import array
import struct
import binascii

from Characteristic import *


'''
structure:
4 sets of left and right channel's raw data
Length of each channel's data is 2 bytes. 16 bytes in total.
Message patern: LRLRLRLR (L: raw data of left channel, raw data of right channel)
'''
class SIDsAudioRead(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0
        
    def process(self):
        value = self.instance._.value
        dataSet = struct.unpack("<hhhhhhhh", value)

        print "SIDSAudioRead", dataSet
        
        # calculate mean value of left channel and right channel
        leftSum, rightSum = 0, 0
        for idx in range(0, 16, 2):
            leftSum += dataSet[idx]
            rightSum += dataSet[idx+1]
        leftAvg = leftSum / (len(dataSet)/2)
        righAvg = righSum / (len(dataSet)/2)
        
        data = {
                'type': 'Audio',
                'leftAvg': leftAvg,
                'righAvg': rightAvg 
                }
        
        self.peripheralWorker.delegateWorker.getQueue().put(data)
       