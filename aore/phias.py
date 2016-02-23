# -*- coding: utf-8 -*-
import json
import logging

from bottle import Bottle, response

from aore.search.fiasfactory import FiasFactory

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
app = Bottle()
fias_factory = FiasFactory()


@app.route(r'/expand/<aoid:re:[\w]{8}(-[\w]{4}){3}-[\w]{12}>')
def expand(aoid):
    response.content_type = 'application/json'
    response.set_header('Access-Control-Allow-Origin', '*')

    return json.dumps(fias_factory.expand(aoid))


@app.route(r'/normalize/<aoid:re:[\w]{8}(-[\w]{4}){3}-[\w]{12}>')
def normalize(aoid):
    response.content_type = 'application/json'
    response.set_header('Access-Control-Allow-Origin', '*')

    return json.dumps(fias_factory.normalize(aoid))


@app.route(r'/find/<text>')
@app.route(r'/find/<text>/<strong>')
def find(text, strong=False):
    strong = (strong == "strong")
    response.content_type = 'application/json'
    response.set_header('Access-Control-Allow-Origin', '*')

    return json.dumps(fias_factory.find(text, strong))


@app.error(404)
def error404(error):
    response.content_type = 'application/json'
    response.set_header('Access-Control-Allow-Origin', '*')

    return json.dumps(dict(error="Page not found"))
