'''
Created on Jan 21, 2014

@author: cjhuo
'''

from ladon.ladonizer import ladonize
from ladon.types.ladontype import LadonType
from ladon.compat import PORTABLE_STRING
import types

class Band(LadonType):
    name = PORTABLE_STRING
    album_titles = [ PORTABLE_STRING ]

class Album(LadonType):
    band = Band
    title = PORTABLE_STRING
    songs = [ PORTABLE_STRING ]

class Group(LadonType):
    gid = int
    name = unicode
    display_name = unicode

class User(LadonType):
    uid = int
    username = unicode
    primary_group = Group
    secondary_groups = [ Group ]

class Calculator(object):
    """
    This service does the math, and serves as example for new potential Ladon users.
    """
    @ladonize(int,int,rtype=Album)
    def add(self,a,b):
        """
        Add two integers together and return the result
        
        @param a: 1st integer
        @param b: 2nd integer
        @rtype: The result of the addition
        """
        return a+b
    @ladonize(int, int, rtype=types.NoneType)
    def delete(self, a, b):
        return a - b 
    

