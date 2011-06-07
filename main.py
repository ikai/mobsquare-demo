import tornado.ioloop
import tornado.web

import config

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world %s" % config.FACEBOOK_APPLICATION_ID)

application = tornado.web.Application([
    (r"/", MainHandler),
], debug=True)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()