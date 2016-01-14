# -*- coding: utf-8 -*-

import sphinxapi

import logging
import json


class SphinxSearch:
    def __init__(self):
        self.client = sphinxapi.SphinxClient()
        self.client.SetServer("localhost", 9312)
        self.client.SetLimits(0, 10)

    def find(self, text):
        # TODO: ADD index
        logging.info("12")
        result = self.client.Query(text)
        print json.dumps(result)
        logging.info("12")
