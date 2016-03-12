# -*- coding: utf-8 -*-

from bottle import Bottle


class BottleCL(object):
    def __init__(self):
        self._app = Bottle()
        self.init_routes()

    def init_routes(self):
        pass

    def add_route(self, route_path, handler):
        self._app.route(route_path, callback=handler)

    def add_error(self, error_code, handler):
        if not self._app.error_handler:
            self._app.error_handler = {error_code: handler}
        else:
            self._app.error_handler[error_code] = handler

    def start(self, **kwargs):
        self._app.run(**kwargs)
