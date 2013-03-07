'''
Created on Feb 17, 2013

@author: cjhuo
'''
import tornado.escape
from pycket.session import SessionMixin

class BaseHandler(tornado.web.RequestHandler, SessionMixin):
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if user_json is not None:
            return tornado.escape.json_decode(user_json)
        return None