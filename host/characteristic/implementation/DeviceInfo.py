'''
Created on Feb 9, 2013

@author: cjhuo
'''

import binascii
import struct

from Characteristic import *
class DeviceInfo(Characteristic):
    def __init__(self):
        Characteristic.__init__(self)
        self.privilege = 2
        
    def process(self):
        data = {'type': 'deviceInfo', 
                'value': self.decryptAddress(self.instance._.value),
                }
        self.peripheralWorker.peripheral.address = data['value']
        self.peripheralWorker.delegateWorker.getQueue().put(data)
        
    
    def decryptAddress(self, value):
        hex_str = binascii.hexlify(value)
        a1, a2, a3, a4, a5, a6 = struct.unpack('cccxxccc', value)
        address = str(binascii.hexlify(a6) + '-' + binascii.hexlify(a5) + '-' + binascii.hexlify(a4) + '-' + \
         binascii.hexlify(a3) + '-' + binascii.hexlify(a2) + '-' + binascii.hexlify(a1))
        print "Peripheral No.", self.peripheralWorker.peripheral.number, "-" , 'MAC Address: ', address
        return address