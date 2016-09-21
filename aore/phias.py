# -*- coding: utf-8 -*-
import json
import logging

from bottle import response, request

from aore.search.fiasfactory import FiasFactory
from borest import app, Route, Error


class App(object):
    _factory = None

    def __init__(self, log_filename):
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG, filename=log_filename)

        App._factory = FiasFactory()

    @Route(r'/expand/<aoid:re:[\w]{8}(-[\w]{4}){3}-[\w]{12}>')
    class Expand(object):
        def get(self, aoid):
            response.content_type = 'application/json'
            response.set_header('Access-Control-Allow-Origin', '*')

            return json.dumps(App._factory.expand(aoid))

    @Route(r'/normalize/<aoid:re:[\w]{8}(-[\w]{4}){3}-[\w]{12}>')
    class Normalize(object):
        def get(self, aoid):
            response.content_type = 'application/json'
            response.set_header('Access-Control-Allow-Origin', '*')

            return json.dumps(App._factory.normalize(aoid))

    @Route(r'/find/<text>')
    class Find(object):
        def get(self, text):
            strong = 'strong' in request.query and request.query.strong == '1'
            response.content_type = 'application/json'
            response.set_header('Access-Control-Allow-Origin', '*')

            return json.dumps(App._factory.find(text, strong))

    @Route(r'/gettext/<aoid:re:[\w]{8}(-[\w]{4}){3}-[\w]{12}>')
    class GetText(object):
        def get(self, aoid):
            response.content_type = 'application/json'
            response.set_header('Access-Control-Allow-Origin', '*')

            return json.dumps(App._factory.gettext(aoid))

    @staticmethod
    @Error(404)
    def basic_error_handler(error):
        response.content_type = 'application/json'
        response.set_header('Access-Control-Allow-Origin', '*')

        return json.dumps(dict(error=error.status))

    @staticmethod
    @Error(500)
    def basic_error_handler(error):
        response.content_type = 'application/json'
        response.set_header('Access-Control-Allow-Origin', '*')

        return json.dumps(dict(error=error.status))
