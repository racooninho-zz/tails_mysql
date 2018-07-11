# External imports
import tornado.ioloop
import tornado.web
import web

tornado_routes = [
    (r"/order", web.Order)]

if __name__ == "__main__":


    port = 8080
    print('Server runnin on http://127.0.0.1:8080/order '
          '\nTo stop press CTRL+C'
          '\nAfter pressing CTRL+C send another request to stop the server')

    application = tornado.web.Application(tornado_routes)
    application.listen(port)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().close()
