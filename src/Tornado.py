import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import asyncio

#from Scan import Scan
import ServerHandler
import Aor

sql = ServerHandler.Sql()
cache = ServerHandler.Cache()
#scan = Scan()

AliveSockets = set()


class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        return self.get_secure_cookie("i")


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("templates/index.html",
                    servers=sql.Get(), stats=cache.Fetch())


class ResourceHandler(tornado.web.RequestHandler):

    def get(self, resource):
        print(resource)
        res = open('src/static/' + resource).read()
        self.set_header("Content-Type", 'text/css; charset="utf-8"')
        self.write(res)


class FetchWebsocket(tornado.websocket.WebSocketHandler):

    def open(self):
        AliveSockets.add(self)
        print("Fetch websocket opened - client " + self.request.remote_ip)

    def on_message(self, message):
        print(self.request.remote_ip + " requested panel " + message)
        #res = scan.Fetch(message)
        res = "placeholder"
        self.write_message(res)
        print(self.request.remote_ip + " was sent " + message)

    def on_close(self):
        AliveSockets.remove(self)
        print("Fetch websocket closed - client " + self.request.remote_ip)


def SendFetchMessage(message):
    for ws in AliveSockets:
        ws.write_message(message)


class LoginManager(tornado.web.RequestHandler):

    def get(self):
        self.render("templates/login.html")

    def post(self):
        self.set_secure_cookie("i", "TODO_RANDOM_KEY")
        self.redirect("/admin")


class AdminInterface(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("templates/admin.html", servers=sql.Get())

    def delete(self):
        pass

    def post(self):
        pass


def make_app():

    settings = {
        "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        "login_url": "/login",
        "xsrf_cookies": True,
        "debug": True
    }

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/static/(.*)", ResourceHandler),
        (r"/fetch", FetchWebsocket),
        (r"/login", LoginManager),
        (r"/admin", AdminInterface),
        (r"/aor", Aor.AorMaster)
    ], **settings)


def run_app():
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

run_app()
