import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import os.path

import sys
sys.dont_write_bytecode = True

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

from fakePlot import PointHandler


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/plot', PlotHandler),
            (r'/plot2', PlotHandler2),
            (r'/point', PointHandler),
            (r'/one', OneHandler)
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

class PlotHandler2(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "plot2.html",
            page_title = "GMap+Tornado Test2",
            header_text = "Generate a plot",
            footer_text = "Simple plot test",
        )

class OneHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "time_series.html",
            page_title = "one graph test",
            header_text = "Generate a plot",
            footer_text = "Simple plot test",
        )

if __name__ == "__main__":
    print "Running on localhost:8000"
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
