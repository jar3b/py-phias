from pathlib import Path
from typing import Iterator

import asyncpg
import click
from jinja2 import Environment, FileSystemLoader

from settings import AppConfig
from .aoxmltableentry import AoXmlTableEntry
from .schemas import ALLOWED_TABLES


class DbFiller:
    __slots__ = ['conf', 'tpl_env', 'pool', 'indexes_dropped']
    conf: AppConfig
    tpl_env: Environment
    pool: asyncpg.Pool
    indexes_dropped: bool

    def __init__(self, conf: AppConfig) -> None:
        self.tpl_env = Environment(loader=FileSystemLoader('orchestra/templates'))
        self.conf = conf
        self.indexes_dropped = False

    async def create(self, source: Path) -> None:
        # create pool
        conf = self.conf.pg
        dsn = f'postgres://{conf.user}:{conf.password}@{conf.host}:{conf.port}/{conf.name}'
        self.pool = await asyncpg.create_pool(dsn, max_inactive_connection_lifetime=conf.pool_recycle)

        try:
            # get entities from folder
            entries_iterator = self.__get_entries_iterator_from_folder(source)

            # create tables
            await self.__run_query('create_structure.sql')
            # drop indexes
            await self.__run_query('drop_indexes.sql')
            # fill data
            for table_entry in entries_iterator:
                self.process_single_entry(table_entry.operation_type, table_entry)
            # create indexes
            await self.__run_query('create_indexes.sql')
        finally:
            await self.pool.close()

    def __get_entries_iterator_from_folder(self, folder: Path) -> Iterator[AoXmlTableEntry]:
        for xml_file in folder.glob("*.XML"):
            xml_table = AoXmlTableEntry.from_dir(xml_file)
            if xml_table.table_name in ALLOWED_TABLES:
                yield xml_table
            else:
                del xml_table

    async def __run_query(self, template_name: str) -> None:
        click.echo(f'Executing "{template_name}"...')

        query = self.tpl_env.get_template(template_name).render()
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(query)

        click.echo(f'Template "{template_name}" executed into db')
