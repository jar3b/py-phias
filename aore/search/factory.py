import uuid
from typing import Dict, List

import asyncpg
from aiohttp import web
from jinja2 import FileSystemLoader, Environment

from .search import SphinxSearch
from .. import log
from ..exceptions import FiasNotFoundException
from ..schemas import AoElementModel, AoResultItemModel


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

    # Преобразует AOID в AOGUID
    async def convert(self, aoid: uuid.UUID) -> uuid.UUID:
        try:
            async with self.pool.acquire() as conn:
                record = await conn.fetchrow(self.queries['convert'], aoid)

            if not record:
                raise FiasNotFoundException("Record with this AOID not found in DB")

            return record['aoguid']
        except Exception as e:
            log.error(f'Cannot convert {aoid}', exc_info=e)
            raise

    # Возвращает простую текстовую строку по указанному AOID (при AOGUID будет
    # ошибка, так что нужно предварительно нормализовать)
    async def gettext(self, aoid: uuid.UUID) -> str:
        try:
            async with self.pool.acquire() as conn:
                record = await conn.fetchrow(self.queries['gettext'], aoid)

            if not record:
                raise FiasNotFoundException("Record with this AOID not found in DB")

            return record['fullname']
        except Exception as e:
            log.error(f'Cannot get text for {aoid}', exc_info=e)
            raise

    async def find(self, text: str, strong: bool = False) -> List[AoResultItemModel]:
        """
        Ищет адресный объект по тексту

        :param text: строка поиска
        :param strong: строгий поиск (True) или "мягкий" (False) (с допущением ошибок, опечаток)
        Строгий используется при импорте из внешних систем (автоматически), где ошибка критична
        :return:
        """

        # TODO: implement
        # results = self.searcher.find(text, strong)
        return [AoResultItemModel(
            cort=0, text="г Усть-Перепиздуйск", ratio=1288,
            aoid=uuid.UUID('5c8b06f1-518e-496e-b683-7bf917e0d70b')
        )]
