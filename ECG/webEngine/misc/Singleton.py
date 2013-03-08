'''
Created on Nov 1, 2012

@author: cjhuo
'''
class Singleton(object):
        
    def __new__(cls,*dt,**mp):
        if not hasattr(cls,'_inst'):
            cls._inst = super(Singleton, cls).__new__(cls,dt,mp)
        else:
            def init_pass(self,*dt,**mp):pass
            cls.__init__ = init_pass
            
        return cls._inst