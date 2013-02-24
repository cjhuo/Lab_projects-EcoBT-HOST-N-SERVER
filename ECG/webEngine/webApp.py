import os.path

import tornado.web

from handlers.fake.fakePlotHandler import *
from handlers.ECGHandler import *
from handlers.pageRenderingHandlers import *
from handlers.AuthHandlers import AuthHandler

from db.Models import DataSource, Device, DataLog
from ecg.ECG_reader import ECG_reader

class Application(tornado.web.Application):
    def __init__(self):
        self.ds = DataSource()
        self.ecg = ECG_reader()
        
        self.handlers = [
                (r'/', MainHandler),          
                (r'/soundMonitor', SoundMonitorHandler),
                (r'/ecgHandler', ECGHandler, dict(ecg = self.ecg)),
                (r'/ecgAllInOne', ECGAllInOneHandler),
                (r'/cardReader', CardReaderHandler),
                (r'/tempAnalysis', TempAnalysisHandler),
                (r'/analysis_old', AnalysisOldHandler),
                (r'/analysis_allInOne', AnalysisAllInOnceHandler),            
                (r'/orientation', OrientationHandler),
                (r'/temperature', TemperatureHandler),
                (r'/liveECG', LiveECGHandler),
                (r'/administration', AdministrationHandler),
                (r'/plot', PlotHandler),
                (r'/analysis', AnalysisHandler),
                (r'/point', PointHandler, dict(ds = self.ds)),
                (r'/dsp', DSPHandler, dict(ecg = self.ecg)),
                (r"/socket", ClientSocket, dict(ds = self.ds)),
                (r"/login", AuthHandler),
                (r"/logout", LogOutHandler)
            ]

        settings = dict(
            template_path=os.path.join(
                os.path.dirname(__file__), "templates"),
            static_path=os.path.join(
                os.path.dirname(__file__), "static"),
            debug=True,
            cookie_secret="BlaBlaBlaBlaBlaBlaBlaBlaBlaBlaBlaBlaBla",
            login_url="/login",        
        )
        tornado.web.Application.__init__(self, self.handlers, **settings)