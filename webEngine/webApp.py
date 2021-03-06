import os.path

import tornado.web

from webHandlers.fake.fakePlotHandler import *
from webHandlers.ECGHandler import *
from webHandlers.pageRenderingHandlers import *
from webHandlers.AuthHandlers import AuthHandler
from webHandlers.ConfigFileHandlers import *
from webHandlers.SDCardHandler import SDCardHandler

from host.Sockets import Sockets
from host.EcoBTWebSocket import EcoBTWebSocket

from db.Models import DataSource, Device, DataLog
from ecg.ECG_reader import ECG_reader
import redis

class Application(tornado.web.Application):
    def __init__(self, ecoBTApp):
        self.ds = DataSource()
        self.ecg = ECG_reader()
        self.globalSockets = Sockets()
        self.ecoBTApp = ecoBTApp
        
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
                (r'/liveSIDs', LiveSIDsHandler),
                (r'/administration', AdministrationHandler),
                (r'/plot', PlotHandler),
                (r'/analysis', AnalysisHandler),
                (r'/point', PointHandler, dict(ds = self.ds)),
                #(r'/dsp', DSPHandler, dict(ecg = self.ecg)),
                (r"/fakeSocket", ClientSocket, dict(ds = self.ds)),
                (r"/login", AuthHandler),
                (r"/logout", LogOutHandler),
                (r"/socket", EcoBTWebSocket, dict(globalSockets = self.globalSockets, 
                                              ecoBTApp = self.ecoBTApp)),
                (r"/config", ConfigHandler, dict(ecoBTApp = self.ecoBTApp)),
                (r"/sdCard", SDCardHandler)
            ]

        settings = dict(
            template_path=os.path.join(
                os.path.dirname(__file__), "templates"),
            static_path=os.path.join(
                os.path.dirname(__file__), "static"),
            debug=True,
            cookie_secret="BlaBlaBlaBlaBlaBlaBlaBlaBlaBlaBlaBlaBla",
            login_url="/login", 
            pycket = {
                        'engine': 'redis',
                        'storage': {
                            'connection_pool': redis.ConnectionPool(max_connections=2 ** 31),
                            'host': 'localhost',
                            'port': 6379,
                            'db_sessions': 10,
                            'db_notifications': 11,
                       },   
                       #'cookies': {
                       #            'expires_days': 120,
                       #            },
                       }       
        )
        tornado.web.Application.__init__(self, self.handlers, **settings)