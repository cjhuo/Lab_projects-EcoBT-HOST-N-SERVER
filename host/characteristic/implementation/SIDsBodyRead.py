'''
Created on Oct 17, 2013

@author: cjhuo
'''

import binascii

from Characteristic import *

class SIDsBodySet(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 0
        
    def process(self):
        pass