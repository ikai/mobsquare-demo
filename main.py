import tornado.ioloop
import tornado.web
from tornado import httpclient 

import urllib
import re
import json
import os

import pymongo
import bson

import config

CALLBACK_URL = urllib.quote(config.REDIRECT_URL + "/callback")
LOGIN_URL = "https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&scope=email,user_checkins,publish_checkins,manage_friendlists" % (config.FACEBOOK_APPLICATION_ID, CALLBACK_URL)
ACCESS_TOKEN_URL_TPL = "https://graph.facebook.com/oauth/access_token?client_id=" + config.FACEBOOK_APPLICATION_ID \
  + "&redirect_uri=" + CALLBACK_URL \
  + "&client_secret=" + config.FACEBOOK_APPLICATION_SECRET \
  + "&code="
  
API = {
    "profile" : "https://graph.facebook.com/me?access_token=%s",
    "places" : "https://graph.facebook.com/search?type=place&center=%(lat)s,%(lon)s&distance=%(distance)d&access_token=%(access_token)s"
}

connection = pymongo.Connection()
db = connection.mobsq_db

def get_user(user_id):
    return db.profiles.find_one({"_id" : bson.objectid.ObjectId(user_id)})

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        user_id = self.get_secure_cookie("user_id")
        if not user_id:
            pass
        else:
            self.render("templates/main.html", user_id=user_id)
        
class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect(LOGIN_URL)
        
ACCESS_TOKEN_REGEX = re.compile("access_token=(.*)&expires=(.*)")
class OnLoginHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous    
    def get(self):
        # Store this somewhere
        code = self.get_argument("code")
        access_token_url = ACCESS_TOKEN_URL_TPL + code
        client = httpclient.AsyncHTTPClient()                        
        client.fetch(access_token_url, self.on_fetched_token)
        # tornado.ioloop.IOLoop.instance().start()
        
    def on_fetched_token(self, response):
        if response.error:
            print "Error:", response.error
        else:
            body = response.body
            matches = ACCESS_TOKEN_REGEX.search(body)
            if matches:
                access_token = matches.group(1)
                print "Access token: %s" % access_token
                client = httpclient.AsyncHTTPClient()                        
                # lambda is effectively a function factory for us
                client.fetch(API["profile"] % access_token, lambda response: self.on_profile_fetch(response, access_token))      
                
    def on_profile_fetch(self, response, access_token):
        if response.error:        
            print "Error:", response.error
        else:
            profile = json.loads(response.body)
            profile["access_token"] = access_token
            print "Writing profile: %s" % profile
            profile_id = db.profiles.insert(profile, safe=True)
            print "Wrote profile with ID: %s" % profile_id
            self.set_secure_cookie("user_id", str(profile_id))
            self.write("Cookie set.")
            self.finish()
  
class NearbyLocationsHandler(tornado.web.RequestHandler):
    
    @tornado.web.asynchronous    
    def get(self):
        user_id = self.get_secure_cookie("user_id")
        if not user_id:
            # Should probably throw up an error here
            pass
        else:
            lat = self.get_argument("lat")
            lon = self.get_argument("lon")        
            user = get_user(user_id)
            
            url = API["places"] % { "lat" : lat, 
                                    "lon" : lon,
                                    "distance" : 1000,
                                    "access_token" : user["access_token"] }
            
            client = httpclient.AsyncHTTPClient()                        
            client.fetch(url, self.on_fetch_places)
            
    def on_fetch_places(self, response):
        places = json.loads(response.body)
        self.write(json.dumps(places))
        self.finish()
        
    


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/login", LoginHandler),
    (r"/callback", OnLoginHandler),
    (r"/nearby", NearbyLocationsHandler)
], cookie_secret=config.COOKIE_SECRET,
   static_path=os.path.join(os.path.dirname(__file__), "static"),
   debug=True)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()