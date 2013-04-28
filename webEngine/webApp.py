import os.path

import tornado.web

from webHandlers.pageRenderingHandlers import *
from webHandlers.AuthHandlers import AuthHandler
from webHandlers.ConfigFileHandlers import *

from host.Sockets import Sockets
from host.EcoBTWebSocket import EcoBTWebSocket

from db.Models import DataSource, Device, DataLog

class Application(tornado.web.Application):
    def __init__(self, ecoBTApp):
        self.ds = DataSource()
        self.globalSockets = Sockets()
        self.ecoBTApp = ecoBTApp
        
        self.handlers = [
                (r'/', MainHandler),          
                (r'/soundMonitor', SoundMonitorHandler),
                (r'/tempAnalysis', TempAnalysisHandler),           
                (r'/orientation', OrientationHandler),
                (r'/temperature', TemperatureHandler),
                (r'/liveSIDs', LiveSIDsHandler),
                (r'/sidsDual', SIDsDualHandler),
                (r'/sidsAll', SIDsAllHandler),
                (r'/administration', AdministrationHandler),
                (r"/login", AuthHandler),
                (r"/logout", LogOutHandler),
                (r"/socket", EcoBTWebSocket, dict(globalSockets = self.globalSockets, 
                                              ecoBTApp = self.ecoBTApp)),
                (r"/config", ConfigHandler, dict(ecoBTApp = self.ecoBTApp))
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