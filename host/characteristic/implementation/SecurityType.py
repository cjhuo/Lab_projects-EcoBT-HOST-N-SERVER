'''
Created on Jan 25, 2014

@author: cjhuo
'''

from Foundation import *
#from PyObjCTools import AppHelper
from IOBluetooth import *
from objc import *

import array, binascii, struct

from Characteristic import *

class SecurityType(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 2
        self.acc_enable = 0
        
    def process(self):
        tp, = struct.unpack("@B", self.instance._.value)
        
        print "Type is ", tp