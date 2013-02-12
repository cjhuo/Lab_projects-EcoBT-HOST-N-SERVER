'''
Created on Feb 10, 2013

@author: cjhuo
'''

class Peripheral(object):
    def __init__(self, instance, name, rssi, number):
        self.instance = instance
        self.name = name
        self.rssi = rssi
        self.number = number