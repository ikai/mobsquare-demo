import tornado.ioloop
import tornado.web
from tornado import httpclient 

import urllib
import re
import json

import pymongo
import config

CALLBACK_URL = urllib.quote(config.REDIRECT_URL + "/callback")
LOGIN_URL = "https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&scope=email,user_checkins,publish_checkins,manage_friendlists" % (config.FACEBOOK_APPLICATION_ID, CALLBACK_URL)
ACCESS_TOKEN_URL_TPL = "https://graph.facebook.com/oauth/access_token?client_id=" + config.FACEBOOK_APPLICATION_ID \
  + "&redirect_uri=" + CALLBACK_URL \
  + "&client_secret=" + config.FACEBOOK_APPLICATION_SECRET \
  + "&code="
  
connection = pymongo.Connection()
db = connection.mobsq_db

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world %s" % config.FACEBOOK_APPLICATION_ID)
        
class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect(LOGIN_URL)
        
ACCESS_TOKEN_REGEX = re.compile("access_token=(.*)&expires=(.*)")
FETCH_PROFILE_URL = "https://graph.facebook.com/me?access_token=%s"

    

class OnLoginHandler(tornado.web.RequestHandler):
    def get(self):
        # Store this somewhere
        code = self.get_argument("code")
        access_token_url = ACCESS_TOKEN_URL_TPL + code
        client = httpclient.AsyncHTTPClient()
        self.write("Code is: %s" % code)
        self.write("Access token url: %s" % access_token_url)
                
        # Builds a callback for LoginHandler
        def on_profile_fetch(response, access_token):
            if response.error:        
                print "Error:", response.error
            else:
                profile = json.loads(response.body)
                profile["access_token"] = access_token
                print "Writing profile: %s" % profile
                p_id = db.profiles.insert(profile, safe=True)
                print "Wrote profile with ID: %s" % p_id
                
        
        def on_fetched_token(response):
            if response.error:
                print "Error:", response.error
            else:
                body = response.body
                matches = ACCESS_TOKEN_REGEX.search(body)
                if matches:
                    access_token = matches.group(1)
                    print "Access token: %s" % access_token
                    # lambda is effectively a function factory for us
                    client.fetch(FETCH_PROFILE_URL % access_token, lambda response: on_profile_fetch(response, access_token))        
        client.fetch(access_token_url, on_fetched_token)
        # tornado.ioloop.IOLoop.instance().start()
    


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", LoginHandler),
    (r"/callback", OnLoginHandler)
], debug=True)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()