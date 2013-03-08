'''
Created on Oct 30, 2012

@author: cjhuo
'''
import os.path
import tornado.ioloop
import tornado.web

from tornado.options import define, options
from tornado import websocket

GLOBALS={
    'sockets': []
}

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "index.html",
            page_title="",
            header_text="Header goes here",
            footer_text="Footer goes heare"
        )

class ClientSocket(websocket.WebSocketHandler):
    def open(self):
        GLOBALS['sockets'].append(self)
        print "WebSocket opened"

    def on_close(self):
        print "WebSocket closed"
        GLOBALS['sockets'].remove(self)

class Announcer(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        data = self.get_argument('data')
        print len(GLOBALS['sockets'])
        for socket in GLOBALS['sockets']:
            socket.write_message(data)
        self.write('Posted')

settings = dict(
    template_path=os.path.join(
        os.path.dirname(__file__), "templates"),
    static_path=os.path.join(
        os.path.dirname(__file__), "static"),
    debug=True,
)

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/socket", ClientSocket),
    (r"/push", Announcer),
], **settings)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    print "Running on localhost:8888"
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()