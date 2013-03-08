'''
Created on Feb 7, 2013

@author: cjhuo
'''

class Sockets(object):
    def __init__(self):
        self.sockets = []
        
    def append(self, socket):
        self.sockets.append(socket)
        
    def remove(self, socket):
        self.sockets.remove(socket)
    
    def __len__(self):
        return len(self.sockets)
    
    def contains(self, socket):
        for s in self.sockets:
            if s is socket:
                return True
        return False
        