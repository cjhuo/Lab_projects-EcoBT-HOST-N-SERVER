import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import os.path
import webbrowser

import sys
sys.dont_write_bytecode = True

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

from host.fakePlot import *
from ecg.ECG_reader import ECG_reader

from db.Models import DataSource, Device, DataLog


class Application(tornado.web.Application):
    def __init__(self):
        ds = DataSource()
        ecg = ECG_reader()
        
        handlers = [
            (r'/', MainHandler),
            (r'/fileHandler', FileHandler, dict(ecg = ecg)),
            (r'/cardReader', CardReaderHandler),
            (r'/tempAnalysis', TempAnalysisHandler),
            (r'/analysis_old', AnalysisOldHandler),
            (r'/analysis_allInOne', AnalysisAllInOnceHandler),            
            (r'/orientation', OrientationHandler),
            (r'/temperature', TemperatureHandler),
            (r'/plot', PlotHandler),
            (r'/analysis', AnalysisHandler),
            (r'/point', PointHandler, dict(ds = ds)),
            (r'/dsp', DSPHandler, dict(ecg = ecg)),
            (r"/socket", ClientSocket, dict(ds = ds))
        ]
        settings = dict(
            template_path=os.path.join(
                os.path.dirname(__file__), "templates"),
            static_path=os.path.join(
                os.path.dirname(__file__), "static"),
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "index.html",
            page_title="ECG and SIDs portal",
            header_text="Header goes here",
            footer_text="Footer goes heare"
        )


class PlotHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "plot.html",
            page_title="SIDs viewer 1",
            header_text="Generate a plot",
            footer_text="",
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
        
class OrientationHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "orientation.html",
            page_title="Orientation viewer",
            header_text="Orientation viewer",
            footer_text="",
        )   
        
class TemperatureHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "temperature.html",
            page_title="temperature viewer",
            header_text="temperature viewer",
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
                               
        
if __name__ == "__main__":
    
    logFile = open('log.txt','a+', 0)
    stdOut = sys.stdout
    stdErr = sys.stderr
    sys.stdout = logFile
    sys.stderr = logFile
    
    print "Running on localhost:8000"
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    
    #open a browser for the web interface
    #webbrowser.open_new('http://localhost:8000/')
    
    #start web server
    tornado.ioloop.IOLoop.instance().start()
    
    
    sys.stdout = stdOut
    sys.stderr = stdErr
    
