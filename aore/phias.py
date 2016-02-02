# -*- coding: utf-8 -*-
import json
import logging

from bottle import Bottle, response

from aore.fias.fiasfactory import FiasFactory

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
app = Bottle()
fias_factory = FiasFactory()


@app.route('/expand/<aoid:re:[\w]{8}(-[\w]{4}){3}-[\w]{12}>')
def expand(aoid):
    response.content_type = 'application/json'
    return json.dumps(fias_factory.expand(aoid))


@app.route('/normalize/<aoid:re:[\w]{8}(-[\w]{4}){3}-[\w]{12}>')
def normalize(aoid):
    response.content_type = 'application/json'
    return json.dumps(fias_factory.normalize(aoid))


@app.route('/find/<text>')
@app.route('/find/<text>/<strong>')
def find(text, strong=False):
    logging.warning("START")
    strong = (strong == "strong")
    response.content_type = 'application/json'

    res = json.dumps(fias_factory.find(text, strong))
    logging.warning("END")
    return res


@app.error(404)
def error404(error):
    response.content_type = 'application/json'
    return json.dumps(dict(error="Page not found"))
