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
        if not self.current_user:
            self.redirect("/login")
            return
        username = tornado.escape.xhtml_escape(self.current_user["name"])
        self.render(
            "index.html",
            page_title="ECG Demo",
            header_text="ECG Demo",
            footer_text="ECG Demo",
            username = username
        )
        
class LogOutHandler(BaseHandler):
    def get(self):
        if self.current_user:
            self.clear_all_cookies()
        self.redirect("/login")            

class AnalysisHandler(BaseHandler):
    def get(self):
        if self.get_arguments("test"):
            print self.get_argument("test")
        self.render(
            "analysis.html",
            page_title="ECG Analysis Viewer",
            header_text="ECG Analysis Viewer",
            footer_text="",
        )
    
class AnalysisAllInOnceHandler(BaseHandler):
    def get(self):
        self.render(
            "analysis_allInOne.html",
            page_title="ECG Viewer",
            header_text="ECG Viewer",
            footer_text="",
        )
        
class AnalysisOldHandler(BaseHandler):
    def get(self):
        self.render(
            "analysis_old.html",
            page_title="ECG Analysis Viewer",
            header_text="ECG Analysis Viewer",
            footer_text="",
        )
        
class TempAnalysisHandler(BaseHandler):
    def get(self):
        self.render(
            "tempAnalysis.html",
            page_title="TempAnalysis Viewer",
            header_text="TempAnalysis Viewer",
            footer_text="",
        ) 
        
class CardReaderHandler(BaseHandler):
    def get(self):
        self.render(
            "cardReader.html",
            page_title="SD CardReader Viewer",
            header_text="SD CardReader Viewer",
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
class PlotHandler(BaseHandler):
    def get(self):
        try:
            name = self.get_argument("name") # node's name, e.g., MAC addres
        except Exception:
            name = None
        self.render(
            "live/plot.html",
            page_title="SIDs Viewer 1",
            header_text="Generate a plot",
            footer_text="",
            serverAddr = plotServerAddr,
            nodeName = name,
        )
        
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
        
class LiveECGHandler(BaseHandler):
    def get(self):  
        try:
            name = self.get_argument("name") # node's name, e.g., MAC addres
        except Exception:
            name = None   
        self.render(
            "live/ecg.html",
            page_title="Live ECG Viewer",
            header_text="Live ECG Viewer",
            footer_text="",
            serverAddr = LiveECGServerAddr,
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