'''
Created on Feb 17, 2013

@author: cjhuo
'''

import tornado.web

from config import *

from BaseHandler import BaseHandler

# static page rendering handlers
class MainHandler(BaseHandler):
    #@tornado.web.authenticated
    def get(self):
        '''
        if not self.current_user:
            self.redirect("/login")
            return
        username = tornado.escape.xhtml_escape(self.current_user["name"])
        '''
        self.render(
            "index_sids.html",
            page_title="SIDs Demo",
            header_text="SIDs Demo",
            footer_text="SIDs Demo",
            #username = username
        )
        
class LogOutHandler(BaseHandler):
    def get(self):
        if self.current_user:
            self.clear_all_cookies()
        self.redirect("/login")            
             
class LiveSIDsHandler(BaseHandler):
    def get(self):  
        try:
            name = self.get_argument("name") # node's name, e.g., MAC addres
            side = self.get_argument("side") # node's location on the board
        except Exception:
            name = None   
            side = None
        self.render(
            "live/sids.html",
            page_title="Live SIDs Viewer",
            header_text="Live SIDs Viewer",
            footer_text="",
            serverAddr = LiveSIDsServerAddr,
            nodeName = name,
            side = side
        )  
                
class SIDsDualHandler(BaseHandler):
    def get(self):  
        try:
            nameL = self.get_argument("nameL", None) # node's name, e.g., MAC addres
            nameR = self.get_argument("nameR", None) # node's name, e.g., MAC addres
        except Exception:
            name = None   
        self.render(
            "live/sids_dual.html",
            page_title="Live SIDs Viewer",
            header_text="Live SIDs Viewer",
            footer_text="",
            serverAddr = LiveSIDsServerAddr,
            nodeNameL = nameL,
            nodeNameR = nameR
        )  


class AdministrationHandler(BaseHandler):
    def get(self):     
        self.render(
            "live/administration.html",
            page_title="Administration Viewer",
            header_text="Administration Viewer",
            footer_text="",
            serverAddr = administrationServerAddr,
        )     