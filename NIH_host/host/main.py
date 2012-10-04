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

from fakePlot import PointHandler, DSPHandler, SubmitHandler

from db.Models import DataSource, Device, DataLog


class Application(tornado.web.Application):
    def __init__(self):
        ds = DataSource()
        
        handlers = [
            (r'/', MainHandler),
            (r'/plot', PlotHandler),
            (r'/analysis', AnalysisHandler),
            (r'/point', PointHandler, dict(ds = ds)),
            (r'/dsp', DSPHandler),
            (r'/submit', SubmitHandler)
        ]
        settings = dict(
            template_path=os.path.join(
                os.path.dirname(__file__), "../templates"),
            static_path=os.path.join(
                os.path.dirname(__file__), "../static"),
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        
        
        


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "index.html",
            page_title="A Tornado Test Page",
            header_text="Header goes here",
            footer_text="Footer goes heare"
        )


class PlotHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "plot.html",
            page_title="JQuery Plot test",
            header_text="Generate a plot",
            footer_text="Simple plot test",
        )
        
        
class AnalysisHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "analysis.html",
            page_title="Signal Analysis Interface",
            header_text="Signal Analysis Interface",
            footer_text="",
        )
        
if __name__ == "__main__":
    print "Running on localhost:8000"
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    
    #open a browser for the web interface
    webbrowser.open_new('http://localhost:8000/')
    
    #start web server
    tornado.ioloop.IOLoop.instance().start()
    
