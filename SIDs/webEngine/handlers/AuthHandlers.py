'''
Created on Feb 17, 2013

@author: cjhuo
'''

import tornado.auth
import tornado.escape
import tornado.web

from BaseHandler import BaseHandler
 
class AuthHandler(BaseHandler, tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()
 
    def _on_auth(self, user):
        if not user:
            self.send_error(500)
            return
        self.set_secure_cookie("user", tornado.escape.json_encode(user))
        print tornado.escape.json_encode(user)
        self.redirect("/")