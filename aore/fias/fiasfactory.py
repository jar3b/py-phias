# -*- coding: utf-8 -*-
import psycopg2
from bottle import template

from aore.dbutils.dbimpl import DBImpl
from aore.fias.search import SphinxSearch
from aore.config import db_conf


class FiasFactory:
    def __init__(self):
        self.db = DBImpl(psycopg2, db_conf)
        self.searcher = SphinxSearch(self.db)
        self.expand_templ = template('aore/templates/postgre/expand_query.sql', aoid="//aoid")
        self.normalize_templ = template('aore/templates/postgre/normalize_query.sql', aoid="//aoid")

    # text - строка поиска
    # strong - строгий поиск (True) или "мягкий" (False) (с допущением ошибок, опечаток)
    # Строгий используется при импорте из внешних систем (автоматически), где ошибка критична
    def find(self, text, strong=False):
        try:
            results = self.searcher.find(text, strong)
        except Exception, err:
            return dict(error=err.args[0])

        return results

    # Нормализует подаваемый AOID или AOGUID в актуальный AOID
    def normalize(self, aoid_guid):
        try:
            sql_query = self.normalize_templ.replace("//aoid", aoid_guid)
            rows = self.db.get_rows(sql_query, True)
        except Exception, err:
            return dict(error=err.args[0])

        if len(rows) == 0:
            return []
        else:
            return rows[0]

    # Разворачивает AOID в представление (перед этим нормализует)
    def expand(self, aoid_guid):
        try:
            normalized_id = self.normalize(aoid_guid)
            if 'aoid' not in normalized_id:
                raise BaseException("Invalid AOID or AOGUID")
            else:
                normalized_id = normalized_id['aoid']
            sql_query = self.expand_templ.replace("//aoid", normalized_id)
            rows = self.db.get_rows(sql_query, True)
        except Exception, err:
            return dict(error=err.args[0])

        return rows
