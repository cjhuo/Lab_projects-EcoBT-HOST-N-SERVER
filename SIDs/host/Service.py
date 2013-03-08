'''
Created on Feb 9, 2013

@author: cjhuo
'''

class Service(object):
    def __init__(self, UUID, instance):
        self.UUID = UUID
        self.instance = instance
        self.characteristics = []
        self.delayQueue = []
        
    def setUUID(self, UUID):
        self.UUID = UUID   
        
    def setInstance(self, instance):
        self.instance = instance
        
    def PushToDelayQueue(self, obj):
        self.delayQueue.append(obj)
        # print all I have in queue
        if len(self.delayQueue) != 0:
            print "There is ", len(self.delayQueue), " task in delay of Service ", self.UUID
            for obj in self.delayQueue:
                print obj
        else:
            print "There is no job in delayQueue of service ", self.UUID
