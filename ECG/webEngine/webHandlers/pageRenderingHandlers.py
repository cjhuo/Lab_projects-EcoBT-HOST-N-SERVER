'''
Created on Feb 17, 2013

@author: cjhuo
'''

import tornado.web
import functools

from config import *

from BaseHandler import BaseHandler

# tweak to add cookie at the very beginning due to the set_secure_cookie bug
def initPycketCookie(method):
    
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.session.get('init'):
            print 'Initializing pycket cookie'
            self.session.set('init', 'init')
        return method(self, *args, **kwargs)
    return wrapper    

# static page rendering handlers
class MainHandler(BaseHandler):
    #@tornado.web.authenticated
    @initPycketCookie
    def get(self):
        '''
        if not self.current_user:
            self.redirect("/login")
            return
        username = tornado.escape.xhtml_escape(self.current_user["name"])
        if not self.session.get('username'):
            self.session.set('username', username)
        print self.session.get('username')
        '''
        self.render(
            "index_ecg.html",
            page_title="ECG Demo",
            header_text="ECG Demo",
            footer_text="ECG Demo",
            #username = username
        )
        
class LogOutHandler(BaseHandler):
    def get(self):
        if self.current_user:
            self.clear_all_cookies()
        self.redirect("/login")            

class AnalysisHandler(BaseHandler):
    def get(self):
        self.render(
            "analysis.html",
            page_title="ECG Analysis Viewer",
            header_text="ECG Analysis Viewer",
            footer_text="",
            frequency = frequency
        )

class AnalysisAllInOnceHandler(BaseHandler):
    def get(self):
        self.render(
            "analysis_allInOne.html",
            page_title="ECG Viewer",
            header_text="ECG Viewer",
            footer_text="",
            frequency = frequency
        )
        
class AnalysisOldHandler(BaseHandler):
    def get(self):
        self.render(
            "analysis_old.html",
            page_title="ECG Analysis Viewer",
            header_text="ECG Analysis Viewer",
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
    
class SDCardPageHandler(BaseHandler):
    def get(self):     
        self.render(
            "sdCard.html",
            page_title="",
            header_text="",
            footer_text="",
        )  