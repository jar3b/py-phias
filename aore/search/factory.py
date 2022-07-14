import logging
import re
import traceback
import urllib.parse
import uuid
from typing import Dict, List

import asyncpg
from aiohttp import web
from jinja2 import Template, FileSystemLoader, Environment

from .search import SphinxSearch
from .. import log
from ..exceptions import FiasNotFoundException
from ..schemas import AoElementModel


class FiasFactory:
    pool: asyncpg.Pool
    searcher: SphinxSearch
    queries: Dict[str, str]

    def __init__(self, app: web.Application):
        self.pool = app['pg']
        self.searcher = SphinxSearch(self.pool)

        env = Environment(loader=FileSystemLoader('aore/templates/postgre'))
        self.queries = {
            'expand': env.get_template('query_expand.sql').render(),
            'normalize': env.get_template('query_normalize.sql').render(),
            'convert': env.get_template('query_convert.sql').render(),
            'gettext': env.get_template('query_gettext.sql').render(),
        }

    # Нормализует подаваемый AOID или AOGUID в актуальный AOID
    async def normalize(self, aoid_or_aoguid: uuid.UUID) -> uuid.UUID:
        try:
            async with self.pool.acquire() as conn:
                record = await conn.fetchrow(self.queries['normalize'], aoid_or_aoguid)

            if not record:
                raise FiasNotFoundException("Record with this AOID not found in DB")

            return record['aoid']
        except Exception as e:
            log.error(f'Cannot normalize {aoid_or_aoguid}', exc_info=e)
            raise

    # Разворачивает AOID в представление (перед этим нормализует)
    async def expand(self, aoid_or_aoguid: uuid.UUID) -> List[AoElementModel]:
        try:
            normalized_aoid = await self.normalize(aoid_or_aoguid)
            async with self.pool.acquire() as conn:
                records = await conn.fetch(self.queries['expand'], normalized_aoid)

            if not records:
                raise FiasNotFoundException("Cannot expand full address chain")

            return [AoElementModel(**r) for r in records]
        except Exception as e:
            log.error(f'Cannot expand {aoid_or_aoguid}', exc_info=e)
            raise

    # # Проверка, что строка является действительым UUID v4
    # @staticmethod
    # def __check_uuid(guid):
    #     try:
    #         UUID(guid)
    #     except ValueError:
    #         return False
    #
    #     return True
    #
    # # Проверяет входящий параметр на соотвествие
    # # param - сам параметр
    # # rule - "boolean", "uuid", "text"
    # def __check_param(self, param, rule):
    #     if rule == "boolean":
    #         assert isinstance(param, bool), "Invalid parameter type"
    #     if rule == "uuid":
    #         assert isinstance(param, str) and self.__check_uuid(
    #             param), "Invalid parameter value"
    #         if rule == "text":
    #             assert isinstance(param, str), "Invalid parameter type"
    #             assert len(param) > 3, "Text too short"
    #             pattern = re.compile(r"[A-za-zА-Яа-я \-,.#№]+")
    #             assert pattern.match(param), "Invalid parameter value"
    #
    # # text - строка поиска
    # # strong - строгий поиск (True) или "мягкий" (False) (с допущением ошибок, опечаток)
    # # Строгий используется при импорте из внешних систем (автоматически), где ошибка критична
    # def find(self, text, strong=False):
    #     try:
    #         text = urllib.parse.unquote(str(text))
    #         self.__check_param(text, "text")
    #         self.__check_param(strong, "boolean")
    #
    #         results = self.searcher.find(text, strong)
    #     except Exception as err:
    #         if BasicConfig.logging:
    #             logging.error(traceback.format_exc())
    #         if BasicConfig.debug_print:
    #             traceback.print_exc()
    #         return dict(error=str(err))
    #
    #     return results
    #

    #
    # # Преобразует AOID в AOGUID
    # def convert(self, aoid: str):
    #     try:
    #         self.__check_param(aoid, "uuid")
    #
    #         sql_query = self.convert_templ.replace("//aoid", aoid)
    #         rows = self.db.get_rows(sql_query, True)
    #
    #         assert len(rows), "Record with this AOID not found in DB"
    #     except Exception as err:
    #         if BasicConfig.logging:
    #             logging.error(traceback.format_exc())
    #         if BasicConfig.debug_print:
    #             traceback.print_exc()
    #         return dict(error=str(err))
    #
    #     if len(rows) == 0:
    #         return []
    #     else:
    #         return rows[0]
    #
    #
    # # Возвращает простую текстовую строку по указанному AOID (при AOGUID будет
    # # ошибка, так что нужно предварительно нормализовать), ищет и в
    # def gettext(self, aoid):
    #     try:
    #         self.__check_param(aoid, "uuid")
    #
    #         sql_query = self.gettext_templ.replace("//aoid", aoid)
    #         rows = self.db.get_rows(sql_query, True)
    #
    #         assert len(rows), "Record with this AOID not found in DB"
    #     except Exception as err:
    #         if BasicConfig.logging:
    #             logging.error(traceback.format_exc())
    #         if BasicConfig.debug_print:
    #             traceback.print_exc()
    #         return dict(error=str(err))
    #
    #     return rows
