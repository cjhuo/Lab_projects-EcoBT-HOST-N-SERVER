'''
Created on Feb 17, 2013

@author: cjhuo
'''

import tornado.web

from config import *

from BaseHandler import BaseHandler

# static page rendering handlers
class MainHandler(BaseHandler):
    @tornado.web.authenticated
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
        
class TempAnalysisHandler(BaseHandler):
    def get(self):
        self.render(
            "tempAnalysis.html",
            page_title="TempAnalysis Viewer",
            header_text="TempAnalysis Viewer",
            footer_text="",
        ) 
        
class SoundMonitorHandler(BaseHandler):
    def get(self):
        self.render(
            "soundMonitor.html",
            page_title="Sound Viewer",
            header_text="Sound Viewer",
            footer_text="",
        )     
        
# live page rendering handlers
class OrientationHandler(BaseHandler):
    def get(self):
        try:
            name = self.get_argument("name") # node's name, e.g., MAC addres
        except Exception:
            name = None
        self.render(
            "live/orientation.html",
            page_title="Orientation Viewer",
            header_text="Orientation Viewer",
            footer_text="",
            serverAddr = orientationServerAddr,
            nodeName = name,
        )
        
class TemperatureHandler(BaseHandler):
    def get(self):
        try:
            name = self.get_argument("name") # node's name, e.g., MAC addres
        except Exception:
            name = None        
        self.render(
            "live/temperature.html",
            page_title="Temperature Viewer",
            header_text="Temperature Viewer",
            footer_text="",
            serverAddr = temperatureServerAddr,
            nodeName = name,
        )  

class LiveSIDsHandler(BaseHandler):
    def get(self):  
        try:
            name = self.get_argument("name") # node's name, e.g., MAC addres
        except Exception:
            name = None   
        self.render(
            "live/sids.html",
            page_title="Live SIDs Viewer",
            header_text="Live SIDs Viewer",
            footer_text="",
            serverAddr = LiveSIDsServerAddr,
            nodeName = name,
        )  

class SIDsAllHandler(BaseHandler):
    def get(self):  
        try:
            name = self.get_argument("name") # node's name, e.g., MAC addres
        except Exception:
            name = None   
        self.render(
            "live/sidsAll.html",
            page_title="Live SIDs Viewer",
            header_text="Live SIDs Viewer",
            footer_text="",
            serverAddr = LiveSIDsServerAddr,
            soundServerAddr = soundServerAddr,
            nodeName = name,
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