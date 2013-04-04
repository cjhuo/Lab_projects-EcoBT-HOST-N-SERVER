import os.path

import tornado.web

from webHandlers.fake.fakePlotHandler import *
from webHandlers.ECGHandler import *
from webHandlers.pageRenderingHandlers import *
from webHandlers.AuthHandlers import AuthHandler
from webHandlers.SDCardHandler import SDCardHandler

from host.Sockets import Sockets
from host.EcoBTWebSocket import EcoBTWebSocket

from db.Models import DataSource, Device, DataLog
from ecg.ECG_reader import ECG_reader

class Application(tornado.web.Application):
    def __init__(self, ecoBTApp):
        self.ds = DataSource()
        self.ecg = ECG_reader()
        self.globalSockets = Sockets()
        self.ecoBTApp = ecoBTApp
        
        settings = dict(
            template_path=os.path.join(
                os.path.dirname(__file__), "templates"),
            static_path=os.path.join(
                os.path.dirname(__file__), "static"),
            debug=True,
            cookie_secret="BlaBlaBlaBlaBlaBlaBlaBlaBlaBlaBlaBlaBla",
            login_url="/login",        
        )        
        
        self.handlers = [
                (r'/', MainHandler),          
                (r'/ecgHandler', ECGHandler, dict(ecg = self.ecg)),
                (r'/ecgAllInOne', ECGAllInOneHandler, dict(ecg = self.ecg)),            
                (r'/cardReader', CardReaderHandler),
                (r'/analysis_allInOne', AnalysisAllInOnceHandler),   
                (r'/liveECG', LiveECGHandler),
                (r'/administration', AdministrationHandler),
                (r'/plot', PlotHandler),
                (r'/analysis', AnalysisHandler),
                (r'/point', PointHandler, dict(ds = self.ds)),
                (r"/fakeSocket", ClientSocket, dict(ds = self.ds)),
                #(r"/login", AuthHandler),
                #(r"/logout", LogOutHandler),
                (r"/socket", EcoBTWebSocket, dict(globalSockets = self.globalSockets, 
                                              ecoBTApp = self.ecoBTApp)),
                (r"/sdCard", SDCardPageHandler),
                (r"/sdCardLoad", SDCardHandler),
                (r"/Uploads/(.*)", tornado.web.StaticFileHandler, {"path": settings['static_path'] + '/Uploads'}),
            ]

        tornado.web.Application.__init__(self, self.handlers, **settings)