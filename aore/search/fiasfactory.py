import logging
import psycopg2
import re
import traceback
import urllib.parse
from bottle import template
from uuid import UUID

from aore.config import DatabaseConfig, BasicConfig
from aore.dbutils.dbimpl import DBImpl
from .search import SphinxSearch


class FiasFactory:
    def __init__(self):
        self.db = DBImpl(psycopg2, DatabaseConfig)
        self.searcher = SphinxSearch(self.db)
        self.expand_templ = template('aore/templates/postgre/expand_query.sql', aoid="//aoid")
        self.normalize_templ = template('aore/templates/postgre/normalize_query.sql', aoid="//aoid")
        self.gettext_templ = template('aore/templates/postgre/gettext_query.sql', aoid="//aoid")

    # Проверка, что строка является действительым UUID v4
    @staticmethod
    def __check_uuid(guid):
        try:
            UUID(guid)
        except ValueError:
            return False

        return True

    # Проверяет входящий параметр на соотвествие
    # param - сам параметр
    # rule - "boolean", "uuid", "text"
    def __check_param(self, param, rule):
        if rule == "boolean":
            assert isinstance(param, bool), "Invalid parameter type"
        if rule == "uuid":
            assert isinstance(param, str) and self.__check_uuid(
                param), "Invalid parameter value"
            if rule == "text":
                assert isinstance(param, str), "Invalid parameter type"
                assert len(param) > 3, "Text too short"
                pattern = re.compile(r"[A-za-zА-Яа-я \-,.#№]+")
                assert pattern.match(param), "Invalid parameter value"

    # text - строка поиска
    # strong - строгий поиск (True) или "мягкий" (False) (с допущением ошибок, опечаток)
    # Строгий используется при импорте из внешних систем (автоматически), где ошибка критична
    def find(self, text, strong=False):
        try:
            text = urllib.parse.unquote(str(text))
            self.__check_param(text, "text")
            self.__check_param(strong, "boolean")

            results = self.searcher.find(text, strong)
        except Exception as err:
            if BasicConfig.logging:
                logging.error(traceback.format_exc())
            if BasicConfig.debug_print:
                traceback.print_exc()
            return dict(error=str(err))

        return results

    # Нормализует подаваемый AOID или AOGUID в актуальный AOID
    def normalize(self, aoid_guid):
        try:
            self.__check_param(aoid_guid, "uuid")

            sql_query = self.normalize_templ.replace("//aoid", aoid_guid)
            rows = self.db.get_rows(sql_query, True)

            assert len(rows), "Record with this AOID not found in DB"
        except Exception as err:
            if BasicConfig.logging:
                logging.error(traceback.format_exc())
            if BasicConfig.debug_print:
                traceback.print_exc()
            return dict(error=str(err))

        if len(rows) == 0:
            return []
        else:
            return rows[0]

    # Разворачивает AOID в представление (перед этим нормализует)
    def expand(self, aoid_guid):
        try:
            self.__check_param(aoid_guid, "uuid")

            normalized_id = self.normalize(aoid_guid)
            assert 'aoid' in normalized_id, "AOID or AOGUID not found in DB"
            normalized_id = normalized_id['aoid']

            sql_query = self.expand_templ.replace("//aoid", normalized_id)
            rows = self.db.get_rows(sql_query, True)
        except Exception as err:
            if BasicConfig.logging:
                logging.error(traceback.format_exc())
            if BasicConfig.debug_print:
                traceback.print_exc()
            return dict(error=str(err))

        return rows

    # Возвращает простую текстовую строку по указанному AOID (при AOGUID будет
    # ошибка, так что нужно предварительно нормализовать), ищет и в
    def gettext(self, aoid):
        try:
            self.__check_param(aoid, "uuid")

            sql_query = self.gettext_templ.replace("//aoid", aoid)
            rows = self.db.get_rows(sql_query, True)

            assert len(rows), "Record with this AOID not found in DB"
        except Exception as err:
            if BasicConfig.logging:
                logging.error(traceback.format_exc())
            if BasicConfig.debug_print:
                traceback.print_exc()
            return dict(error=str(err))

        return rows
