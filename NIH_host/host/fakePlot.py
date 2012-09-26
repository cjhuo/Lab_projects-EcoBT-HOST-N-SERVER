import tornado.web
import random

class SensorPlot(tornado.web.UIModule):
    def render(self):
        pass

class PointHandler(tornado.web.RequestHandler):
    def get(self):
        val = {'point': random.randint(-100, 130)}
        self.write(val)
