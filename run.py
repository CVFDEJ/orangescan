#!/usr/bin/python3
# -*- coding: utf-8 -*-

from app import app
import sys
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

if __name__ == '__main__':
    http_server = HTTPServer(WSGIContainer(app))
    app.debug = False
    # app.debug = True
    port = sys.argv[1]
    http_server.listen(port)
    IOLoop.instance().start()
