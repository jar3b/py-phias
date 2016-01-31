# -*- coding: utf-8 -*-
import psycopg2
from bottle import template

from aore.dbutils.dbimpl import DBImpl
from aore.fias.search import SphinxSearch
from aore.config import db as dbparams


class FiasFactory:
    def __init__(self):
        self.db = DBImpl(psycopg2, dbparams)
        self.searcher = SphinxSearch(self.db)
        self.expand_templ = template('aore/templates/postgre/expand_query.sql', aoid="//aoid")

    # text - строка поиска
    # strong - строгий поиск (True) или "мягкий" (False) (с допущением ошибок, опечаток)
    # out_format - "full" or "simple" - полный (подробно для каждого подпункта) или простой (только строка и AOID)
    def find(self, text, strong=False, out_format="simple"):
        try:
            results = self.searcher.find(text, strong)
        except Exception, err:
            return dict(error=err.args[0])

        return results

    # Нормализует подаваемый AOID или AOGUID в актуальный AOID
    def normalize(self, aoid_guid):
        pass

    # Разворачивает AOID в представление (перед этим нормализует)
    def expand(self, aoid_guid):
        try:
            sql_query = self.expand_templ.replace("//aoid", aoid_guid)
            rows = self.db.get_rows(sql_query, True)
        except Exception, err:
            return dict(error=err.args[0])

        return rows
