import os.path

import tornado.web

from handlers.fake.fakePlotHandler import *
from handlers.ECGHandler import *
from webEngine.config import *
from db.Models import DataSource, Device, DataLog
from ecg.ECG_reader import ECG_reader

class Application(tornado.web.Application):
    def __init__(self):
        self.ds = DataSource()
        self.ecg = ECG_reader()
        
        self.handlers = [
                (r'/', MainHandler),
                (r'/soundMonitor', SoundMonitorHandler),
                (r'/fileHandler', FileHandler, dict(ecg = self.ecg)),
                (r'/cardReader', CardReaderHandler),
                (r'/tempAnalysis', TempAnalysisHandler),
                (r'/analysis_old', AnalysisOldHandler),
                (r'/analysis_allInOne', AnalysisAllInOnceHandler),            
                (r'/orientation', OrientationHandler),
                (r'/temperature', TemperatureHandler),
                (r'/plot', PlotHandler),
                (r'/analysis', AnalysisHandler),
                (r'/point', PointHandler, dict(ds = self.ds)),
                (r'/dsp', DSPHandler, dict(ecg = self.ecg)),
                (r"/socket", ClientSocket, dict(ds = self.ds))
            ]

        settings = dict(
            template_path=os.path.join(
                os.path.dirname(__file__), "templates"),
            static_path=os.path.join(
                os.path.dirname(__file__), "static"),
            debug=True,
        )
        tornado.web.Application.__init__(self, self.handlers, **settings)

# static page rendering handlers
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "index.html",
            page_title="ECG and SIDs portal",
            header_text="Header goes here",
            footer_text="Footer goes heare"
        )
        
class AnalysisHandler(tornado.web.RequestHandler):
    def get(self):
        if self.get_arguments("test"):
            print self.get_argument("test")
        self.render(
            "analysis.html",
            page_title="ECG Analysis Viewer",
            header_text="ECG Analysis Viewer",
            footer_text="",
        )
    
class AnalysisAllInOnceHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "analysis_allInOne.html",
            page_title="DSP Analysis Viewer",
            header_text="DSP Analysis Viewer",
            footer_text="",
        )
        
class AnalysisOldHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "analysis_old.html",
            page_title="DSP Analysis Viewer",
            header_text="DSP Analysis Viewer",
            footer_text="",
        )
        
class TempAnalysisHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "tempAnalysis.html",
            page_title="TempAnalysis viewer",
            header_text="TempAnalysis viewer",
            footer_text="",
        ) 
        
class CardReaderHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "cardReader.html",
            page_title="cardReader viewer",
            header_text="cardReader viewer",
            footer_text="",
        )        
        
class SoundMonitorHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "soundMonitor.html",
            page_title="Sound Viewer",
            header_text="Sound Viewer",
            footer_text="",
        )     
        
# live page rendering handlers
class PlotHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            name = self.get_argument("name") # node's name, e.g., MAC addres
        except Exception:
            name = None
        self.render(
            "live/plot.html",
            page_title="SIDs viewer 1",
            header_text="Generate a plot",
            footer_text="",
            serverAddr = plotServerAddr,
            nodeName = name,
        )
        
class OrientationHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            name = self.get_argument("name") # node's name, e.g., MAC addres
        except Exception:
            name = None
        self.render(
            "live/orientation.html",
            page_title="Orientation viewer",
            header_text="Orientation viewer",
            footer_text="",
            serverAddr = orientationServerAddr,
            nodeName = name,
        )   
        
class TemperatureHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            name = self.get_argument("name") # node's name, e.g., MAC addres
        except Exception:
            name = None        
        self.render(
            "live/temperature.html",
            page_title="temperature viewer",
            header_text="temperature viewer",
            footer_text="",
            serverAddr = temperatureServerAddr,
            nodeName = name,
        )               