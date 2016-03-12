# -*- coding: utf-8 -*-
import json
import logging

from bottle import response

from aore.search.fiasfactory import FiasFactory
from miscutils.bottlecl import BottleCL


class App(BottleCL):
    def __init__(self):
        super(App, self).__init__()
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

        self._factory = FiasFactory()

    def init_routes(self):
        self.add_route(r'/expand/<aoid:re:[\w]{8}(-[\w]{4}){3}-[\w]{12}>', self.__expand)
        self.add_route(r'/normalize/<aoid:re:[\w]{8}(-[\w]{4}){3}-[\w]{12}>', self.__normalize)
        self.add_route(r'/find/<text>', self.__find)
        self.add_route(r'/find/<text>/<strong>', self.__find)
        self.add_error(404, self.basic_error_handler)
        self.add_error(500, self.basic_error_handler)

    def __expand(self, aoid):
        response.content_type = 'application/json'
        response.set_header('Access-Control-Allow-Origin', '*')

        return json.dumps(self._factory.expand(aoid))

    def __normalize(self, aoid):
        response.content_type = 'application/json'
        response.set_header('Access-Control-Allow-Origin', '*')

        return json.dumps(self._factory.normalize(aoid))

    def __find(self, text, strong=False):
        strong = (strong == "strong")
        response.content_type = 'application/json'
        response.set_header('Access-Control-Allow-Origin', '*')

        return json.dumps(self._factory.find(text, strong))

    @staticmethod
    def basic_error_handler(error):
        response.content_type = 'application/json'
        response.set_header('Access-Control-Allow-Origin', '*')

        return json.dumps(dict(error=error.status))
